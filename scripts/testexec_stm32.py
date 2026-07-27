#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  STM32 実機向け testexec ランナー（Linux / Windows 両対応）
#
#  asp3_core の test/testexec.py は asp3_core 単体を configure する前提のため、
#  CubeMX 外側プロジェクト（nucleo_*）では使えない。本スクリプトは外側プロジェクト
#  を 1 テストずつ configure（-DASP3_APPLDIR/APPLNAME/APPCFGNAME 差し替え）→
#  build → STM32_Programmer_CLI で書込み → シリアル出力を判定する。
#
#  判定は CI ランナー（asp3_core scripts/ci/run_testexec.py）互換:
#    PASS    "All check points passed."（hrt1/dlynse は SPECIAL_SPEC の完走マーカ）
#    SKIP    "This test program is not necessary."
#    FAIL    "## "・"not ok " 行・"Unregistered Exception"・SPECIAL_SPEC の fail
#    TIMEOUT 期限内にいずれも出ない
#
#  --rejudge で（実行せず）保存済み serial ログのみ再判定する。
#
#  必要なもの:
#    - Python 3.8+ と pyserial（pip install pyserial）
#    - CMake / Ninja / arm-none-eabi-gcc（CubeMX 生成済みプロジェクト）
#    - STM32_Programmer_CLI（自動探索。環境変数 STM32_PROGRAMMER_CLI で明示指定可）
#
#  使い方:
#    scripts/testexec_stm32.py --board nucleo_h563zi [--port COM10|/dev/ttyACM0] [test ...]
#    --port 省略時は ST-LINK 仮想 COM ポート（VID 0x0483）を自動検出する。
#    テスト名省略時は標準機能テスト一式（拡張パッケージ・perf・arm_* は対象外）
#
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial が必要です:  pip install pyserial")

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CORE = os.path.join(REPO, "asp3", "asp3_core")

BAUDRATE = 115200
STLINK_VID = 0x0483  # STMicroelectronics（ST-LINK VCP）

#  STM32_Programmer_CLI の探索パターン（OS 別・新しいバージョンを優先）
_PROGRAMMER_GLOBS = [
    #  STM32CubeCLT / CubeMX バンドル（Linux）
    "~/.local/share/stm32cube/bundles/programmer/*/bin/STM32_Programmer_CLI",
    "~/STM32CubeCLT*/STM32CubeProgrammer/bin/STM32_Programmer_CLI",
    "/opt/st/STM32CubeCLT*/STM32CubeProgrammer/bin/STM32_Programmer_CLI",
    "/opt/st/stm32cubeprog*/bin/STM32_Programmer_CLI",
    #  CubeMX バンドル（Windows）
    "~/AppData/Local/stm32cube/bundles/programmer/*/bin/STM32_Programmer_CLI.exe",
    #  スタンドアロン / CLT インストーラ（Windows）
    "C:/Program Files/STMicroelectronics/STM32Cube/STM32CubeProgrammer/bin/"
    "STM32_Programmer_CLI.exe",
    "C:/ST/STM32CubeCLT*/STM32CubeProgrammer/bin/STM32_Programmer_CLI.exe",
    "C:/Program Files/STMicroelectronics/STM32CubeCLT*/STM32CubeProgrammer/bin/"
    "STM32_Programmer_CLI.exe",
]


def _version_key(path):
    """パス中の数値列でバージョン比較（2.22.0 > 2.9.0 を保証）"""
    return [int(n) for n in re.findall(r"\d+", path)]


def find_programmer():
    """STM32_Programmer_CLI の実体パスを返す。見つからなければ終了。"""
    env = os.environ.get("STM32_PROGRAMMER_CLI")
    if env:
        if not os.path.isfile(env):
            sys.exit(f"STM32_PROGRAMMER_CLI={env} が存在しない")
        return env
    found = shutil.which("STM32_Programmer_CLI")
    if found:
        return found
    cands = []
    for pat in _PROGRAMMER_GLOBS:
        cands += glob.glob(os.path.expanduser(pat))
    if not cands:
        sys.exit("STM32_Programmer_CLI が見つからない。"
                 "環境変数 STM32_PROGRAMMER_CLI で明示指定してください。")
    return os.path.normpath(max(cands, key=_version_key))


def find_port():
    """ST-LINK の仮想 COM ポートを自動検出する。"""
    cands = [p for p in list_ports.comports() if p.vid == STLINK_VID]
    if not cands:
        sys.exit("ST-LINK 仮想 COM ポートを検出できない。--port で指定してください。")
    if len(cands) > 1:
        print("複数の ST-LINK VCP を検出: "
              + ", ".join(p.device for p in cands)
              + f" → {cands[0].device} を使用", flush=True)
    return cands[0].device


#  標準機能テスト（asp3_core test/testexec.py の TEST_SPEC から、
#  拡張パッケージ（messagebuf/ovrhdr/rstr/subprio/inherit）・perf・arm_* を除く）
TEST_SPEC = {
    **{f"cpuexc{i}": {"SRC": f"test_cpuexc{i}", "CFG": "test_cpuexc"}
       for i in range(1, 11)},
    "dlynse":   {"SRC": "test_dlynse"},
    "dtq1":     {"SRC": "test_dtq1"},
    "exttsk":   {"SRC": "test_exttsk"},
    "flg1":     {"SRC": "test_flg1"},
    "hrt1":     {"SRC": "test_hrt1"},
    "int1":     {"SRC": "test_int1"},
    "mpf1":     {"SRC": "test_mpf1"},
    **{f"mutex{i}": {"SRC": f"test_mutex{i}"} for i in range(1, 9)},
    "notify1":  {"SRC": "test_notify1"},
    "pdq1":     {"SRC": "test_pdq1"},
    "raster1":  {"SRC": "test_raster1"},
    "raster2":  {"SRC": "test_raster2"},
    "sem1":     {"SRC": "test_sem1"},
    "sem2":     {"SRC": "test_sem2"},
    "suspend1": {"SRC": "test_suspend1"},
    "sysman1":  {"SRC": "test_sysman1"},
    "sysstat1": {"SRC": "test_sysstat1"},
    "task1":    {"SRC": "test_task1"},
    "tmevt1":   {"SRC": "test_tmevt1"},
}


def run(cmd, log_path, cwd=None, timeout=300):
    """cmd（引数リスト）を実行しログに落とす。shell を介さないので OS 非依存。"""
    with open(log_path, "w") as out:
        out.write("$ " + subprocess.list2cmdline(cmd) + "\n")
        out.flush()
        return subprocess.call(cmd, cwd=cwd, timeout=timeout,
                               stdout=out, stderr=subprocess.STDOUT) == 0


def open_serial(port):
    ser = serial.Serial(port, BAUDRATE, timeout=0.5)  # 8N1（pyserial 既定）
    ser.reset_input_buffer()
    return ser


#  判定マーカー（asp3_core scripts/ci/run_testexec.py と同一仕様）
PASS_MARK = "All check points passed."
SKIP_MARK = "This test program is not necessary."
FAIL_PATTERNS = (
    re.compile(r"^not ok "),
    re.compile(r"^## "),
    re.compile(r"^Unregistered (Exception|Interrupt)"),
)
SPECIAL_SPEC = {
    "hrt1": {
        "pass": "high resolution timer count test finishes.",
        "fail": (re.compile(r"goes back"),),
    },
    "dlynse": {
        "pass": "-- for checking boundary conditions --",
        "fail": (re.compile(r"sil_dly_nse\(\d+\): \d+ NG"),),
    },
}


def judge_text(test, text):
    special = SPECIAL_SPEC.get(test, {})
    pass_mark = special.get("pass", PASS_MARK)
    fail_patterns = FAIL_PATTERNS + special.get("fail", ())
    for line in text.splitlines():
        for pat in fail_patterns:
            if pat.search(line):
                return "FAIL", line.strip()
    if SKIP_MARK in text:
        return "SKIP", "not necessary on this target"
    if pass_mark in text:
        return "PASS", ""
    return None, ""


def judge_serial(test, ser, deadline, log_file):
    buf = b""
    while time.time() < deadline:
        #  timeout=0.5 の read(1) でブロックしつつ、溜まっている分をまとめて回収
        chunk = ser.read(1)
        if not chunk:
            continue
        chunk += ser.read(ser.in_waiting or 0)
        buf += chunk
        log_file.write(chunk)
        log_file.flush()
        verdict, detail = judge_text(test, buf.decode("ascii", errors="replace"))
        if verdict:
            return verdict, detail
    return "TIMEOUT", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", default="nucleo_h563zi")
    ap.add_argument("--port", default=None,
                    help="シリアルポート（例 COM10 / /dev/ttyACM0）。"
                         "省略時は ST-LINK VCP を自動検出")
    ap.add_argument("--run-timeout", type=int, default=60)
    ap.add_argument("--rejudge", action="store_true",
                    help="実行せず保存済み serial ログのみ再判定")
    ap.add_argument("tests", nargs="*", default=list(TEST_SPEC))
    args = ap.parse_args()

    board_dir = os.path.join(REPO, args.board, "sample1")
    build_dir = os.path.join(board_dir, "build", "TestExec")
    elf = None  # configure 後に *.elf を探す
    logs = os.path.join(build_dir, "logs")
    os.makedirs(logs, exist_ok=True)

    results = {}
    if args.rejudge:
        for test in args.tests:
            slog = os.path.join(logs, f"{test}.serial.log")
            if not os.path.isfile(slog):
                results[test] = ("NO_LOG", "")
                continue
            with open(slog, "rb") as f:
                text = f.read().decode("ascii", errors="replace")
            verdict, detail = judge_text(test, text)
            results[test] = (verdict or "TIMEOUT", detail)
        return summary(results)

    programmer = find_programmer()
    port = args.port or find_port()
    print(f"programmer: {programmer}\nport      : {port}\n", flush=True)

    for test in args.tests:
        spec = TEST_SPEC.get(test)
        if spec is None:
            results[test] = ("SKIP", "unknown test name")
            continue
        applname = spec["SRC"]
        cfgname = spec.get("CFG", applname)
        print(f"== {test} ==", flush=True)

        cfg_cmd = [
            "cmake", "--preset", "Debug", "-B", build_dir,
            f"-DASP3_APPLDIR={os.path.join(CORE, 'test')}",
            f"-DASP3_APPLNAME={applname}",
            f"-DASP3_APPCFGNAME={cfgname}",
            f"-DASP3_EXTRA_APP_C_FILES={os.path.join(CORE, 'syssvc', 'test_svc.c')}",
        ]
        log = os.path.join(logs, f"{test}.build.log")
        if not (run(cfg_cmd, log, cwd=board_dir) and
                run(["cmake", "--build", build_dir],
                    log.replace(".build.", ".ninja."), cwd=board_dir)):
            results[test] = ("BUILD_FAIL", f"see {log}")
            print("   BUILD_FAIL", flush=True)
            continue

        if elf is None:
            elf = next(f for f in os.listdir(build_dir) if f.endswith(".elf"))
        elf_path = os.path.join(build_dir, elf)

        ser = open_serial(port)
        try:
            if not run([programmer, "-c", "port=SWD", "reset=HWrst",
                        "-w", elf_path, "-v", "-rst"],
                       os.path.join(logs, f"{test}.flash.log")):
                results[test] = ("FLASH_FAIL", "")
                print("   FLASH_FAIL", flush=True)
                continue
            with open(os.path.join(logs, f"{test}.serial.log"), "wb") as slog:
                verdict, detail = judge_serial(test, ser,
                                               time.time() + args.run_timeout, slog)
        finally:
            ser.close()
        results[test] = (verdict, detail)
        print(f"   {verdict} {detail}", flush=True)
    return summary(results)


def summary(results):
    print("\n==== summary ====")
    counts = {}
    for test, (verdict, detail) in results.items():
        counts[verdict] = counts.get(verdict, 0) + 1
        print(f"{verdict:10s} {test:10s} {detail}")
    print(", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
          f"/ total={len(results)}")
    return 0 if set(counts) <= {"PASS", "SKIP"} else 1


if __name__ == "__main__":
    sys.exit(main())

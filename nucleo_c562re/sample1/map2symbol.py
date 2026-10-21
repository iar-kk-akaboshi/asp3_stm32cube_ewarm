#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Extract ENTRY LIST symbols from an EWARM map file
#
#  Copyright (C) 2026 by IAR Systems KK, JAPAN
#  Copyright (C) 2015-2026 by Embedded and Real-Time Systems Laboratory
#              Graduate School of Information Science, Nagoya Univ., JAPAN
#
#  上記著作権者は，以下の(1)〜(4)の条件を満たす場合に限り，本ソフトウェ
#  ア（本ソフトウェアを改変したものを含む．以下同じ）を使用・複製・改
#  変・再配布（以下，利用と呼ぶ）することを無償で許諾する．
#  (1) 本ソフトウェアをソースコードの形で利用する場合には，上記の著作
#      権表示，この利用条件および下記の無保証規定が，そのままの形でソー
#      スコード中に含まれていること．
#  (2) 本ソフトウェアを，ライブラリ形式など，他のソフトウェア開発に使
#      用できる形で再配布する場合には，再配布に伴うドキュメント（利用
#      者マニュアルなど）に，上記の著作権表示，この利用条件および下記
#      の無保証規定を掲載すること．
#  (3) 本ソフトウェアを，機器に組み込むなど，他のソフトウェア開発に使
#      用できない形で再配布する場合には，次のいずれかの条件を満たすこ
#      と．
#    (a) 再配布に伴うドキュメント（利用者マニュアルなど）に，上記の著
#        作権表示，この利用条件および下記の無保証規定を掲載すること．
#    (b) 再配布の形態を，別に定める方法によって，TOPPERSプロジェクトに
#        報告すること．
#  (4) 本ソフトウェアの利用により直接的または間接的に生じるいかなる損
#      害からも，上記著作権者およびTOPPERSプロジェクトを免責すること．
#      また，本ソフトウェアのユーザまたはエンドユーザからのいかなる理
#      由に基づく請求からも，上記著作権者およびTOPPERSプロジェクトを
#      免責すること．
#
#  本ソフトウェアは，無保証で提供されているものである．上記著作権者お
#  よびTOPPERSプロジェクトは，本ソフトウェアに関して，特定の使用目的
#  に対する適合性も含めて，いかなる保証も行わない．また，本ソフトウェ
#  アの利用により直接的または間接的に生じたいかなる損害に関しても，そ
#  の責任を負わない．
#
"""Extract ENTRY LIST symbols from an EWARM map file.

Usage:
    map2symbol.py <input.map> <output.txt>
"""

from __future__ import annotations

import re
import sys


ADDRESS_RE = re.compile(r"0x[0-9A-Fa-f']+")


def extract_normalized_address(line: str) -> str | None:
    """Return normalized hex digits (without 0x and apostrophes) or None."""
    match = ADDRESS_RE.search(line)
    if not match:
        return None

    token = match.group(0)[2:].replace("'", "")
    if not token:
        return None
    return token.lower()


def extract_symbol_token(line: str) -> str:
    """Extract first non-space token from the line."""
    parts = line.strip().split()
    return parts[0] if parts else ""


def parse_entry_list(lines: list[str]) -> list[tuple[str, str]]:
    """Parse ENTRY LIST section and return list of (address_hex, symbol)."""
    in_entry_list = False
    pending_symbol = ""
    result: list[tuple[str, str]] = []

    for raw_line in lines:
        line = raw_line.rstrip("\r\n")
        trimmed = line.strip()

        if not in_entry_list:
            if "*** ENTRY LIST" in line:
                in_entry_list = True
            continue

        if trimmed.startswith("["):
            break

        if (
            not trimmed
            or trimmed.startswith("Entry")
            or trimmed.startswith("-----")
            or trimmed.startswith("*")
        ):
            continue

        address_hex = extract_normalized_address(line)
        if address_hex is not None:
            symbol = pending_symbol if pending_symbol else extract_symbol_token(line)
            pending_symbol = ""
            if symbol:
                result.append((address_hex, symbol))
            continue

        # Long symbol names can be split as:
        # <symbol-only-line>
        # <indented-address-line>
        if trimmed and (" " not in trimmed and "\t" not in trimmed):
            pending_symbol = trimmed

    return result


def convert_map_to_symbol(input_path: str, output_path: str) -> None:
    with open(input_path, "r", encoding="utf-8", errors="replace") as in_fp:
        lines = in_fp.readlines()

    entries = parse_entry_list(lines)

    with open(output_path, "w", encoding="utf-8", newline="\n") as out_fp:
        for address_hex, symbol in entries:
            addr_value = int(address_hex, 16)
            out_fp.write(f"{addr_value:08x}\tR\t{symbol}\n")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: map2symbol.py <input.map> <output.txt>", file=sys.stderr)
        return 1

    input_path = argv[1]
    output_path = argv[2]

    try:
        convert_map_to_symbol(input_path, output_path)
    except OSError as exc:
        print(f"File error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

# 使い方

## 対応ボードと検証状況
ここでは評価ボード NUCLEO-H563ZIに関する説明を行います。
| ボード | MCU | ターゲット名 | 実機検証|
|---|---|---|---|
| NUCLEO-H563ZI | STM32H563ZI（Cortex-M33） | `stm32h563_nucleo` | sample1・test_porting 6/6・testexec 32 PASS （2026-06-12） |



## 対応コンパイラ
IAR Embedded Workbench for ARM（EWARM）を使用。
今回使用したバージョンは9.70.4になります。

| ツール | コマンド名 | 
|---|---|
|Cコンパイラ | iccarm.exe |
|アセンブラ |  iasmarm.exe |
|リンカ     |  ilinkarm.exe |
|SREC生成  |  ielftool.exe |

これらのインストールパスをsample1/cmake/EWARM.cmakeにて登録しています。EWARMのバージョンが異なる場合やインストールパスが異なる場合には、こちらを変更してください。
![sample1/cmake/EWARM.cmake](../../images/iar_EWARM.cmake.png)



またTOPPERS/ASP3ではGCCのnmの出力が必要ですが(cfg1_out.syms)、EWARMではMAPファイルから同形式の出力をするためのmap2symbol.pyというスクリプトを用意しています。
このスクリプトはsample1フォルダ直下にmap2symbol.pyとしておいています。

## その他使用ツール
| ツール | コマンド名 | 
|---|---|
|STM32CubeProg | EWARMで書き込む場合は不要。インストールしてPATH設定をしてください。|
|STM32CubeMX | 設定ファイルH563ZI.iocからコードを生成します。|
|CMake |  インストールしてPATHに設定してください。|
|PYTHON     |インストールしてPATHに設定してください。 |
|Ninja  |  EWARMにインストールしたものが利用できます。EWARMインストールフォルダの\common\binにあるので、ここもPATH設定してください。 |



## ディレクトリ構成

```
asp3_stm32cube_ewarm/
├── asp3
│   ├── CMakeLists.txt			# EWARM向けCMake設定
│   ├── arch/arm_iar_iccarm/stm32h5xx_stm32cube	# チップ層（H5共通）
│   ├── asp3_core			# カーネル本体（git submodule・無変更）
│   ├── asp3_stm32cube.cmake 	# glue（ASP3_TARGET_DIR 等の解決）
│   └── target/stm32h533_nucleo	# NUCLEO-H563ZI ターゲット依存部
├── docs			 	# 検証状況・残課題
├── nucleo_c562re/sample1		# CubeMX2 プロジェクト（C562RE.ioc2 が正本）
├── nucleo_h563zi/sample1		# CubeMX プロジェクト（H563ZI.ioc が正本）
└── scripts/testexec_stm32.py	# 実機向け機能テストランナー
```




## ビルド方法
### 0. クローン
```bash
git clone --recursive https://github.com/iar-kk-akaboshi/asp3_stm32cube_ewarm.git
```

### 1. STM32CubeMX2 でコード生成

下記の URL から STM32CubeMX2 をダウンロードし、インストールします。STM32CubeMXは使えませんので注意してください。

<https://www.st.com/ja/development-tools/stm32cubemx.html>

`nucleo_C562re/sample1/C562RE.ioc2`を STM32CubeMX2 で開きます。
1.[Project Setting]をクリックし
2.[Format]をCMake
3.[MCake Toolchain]をGCC
4.[Destination]がsample1フォルダを設定していることを確認し、
5.[Generate IDE project] ボタンを押下します。

![STM32 CubeMX2(a)](../../images/CubeMX2_stepA.png)

すると、sample1にあったファイルと同じ名称があると以下の確認画面が表示されます。
ここに表示されたファイルのOptionはすべて[Don't generate]に変更し、すべて変更したら[Apply & Continue]を押下します。

![STM32 CubeMX2(b)](../../images/CubeMX2_stepB.png)


ビルドに必要なコードが生成されます。


### 2. コマンドラインでビルド

```bash
cd nucleo_c563re/sample1  
cmake --preset debug_GCC_NUCLEO-C562RE 
cmake --build build/debug_GCC_NUCLEO-C562RE 

```

## 実行・デバッグ

### コマンドラインで書込み

```Command Prompt
STM32_Programmer_CLI -c port=SWD reset=HWrst -w build/debug_GCC_NUCLEO-C562RE/C562RE.elf -v -rst
```

シリアル（ST-LINK Virtual COM Port・115200 8N1）に sample1 のバナーと
`task1 is running` が出力されます。`r` を送ると task1→2→3 が切り替わります。


## テスト

アプリは `-D` 指定で差し替えられます（既定は sample1）。

```bash
# 移植検証テスト（TAP 6項目）
CORE=$PWD/../asp3/asp3_core
cmake --preset Debug -B build/TestPorting \
  -DASP3_APPLDIR=$CORE/test/porting -DASP3_APPLNAME=test_porting \
  -DASP3_EXTRA_APP_C_FILES=$CORE/test/porting/tap.c
cmake --build build/TestPorting

# 機能テスト全件（実機・リポジトリルートで）
python3 scripts/testexec_stm32.py --board nucleo_c563re
```

結果の見方・既知の非PASS は [docs/verification.md](docs/verification.md) を参照。

## ドキュメント
ここは元のasp3_stm32ubeのまま
| 内容 | 場所 |
|---|---|
| 実機検証ホストPCの初期セットアップ（udev・FW・CubeMX初回） | [docs/host-setup.md](docs/host-setup.md) |
| 検証状況・テスト再実行手順 | [docs/verification.md](docs/verification.md) |
| 残課題 | [docs/TODO.md](docs/TODO.md) |
| 移植の経緯・root cause 解析（正本） | `asp3/asp3_core/docs/dev/stm32-integration.md` |
| 作業ガイド（新ボード追加・デバッグ・落とし穴） | `.claude/skills/porting-asp3-to-stm32/` |



## 制限事項

- TECS には対応していません（asp3_core は TECS レス方針）。
- TrustZone（TZEN 有効）構成は未対応です。
- CubeMX 生成物に依存するため CI ではビルドしていません（実機環境で検証）。

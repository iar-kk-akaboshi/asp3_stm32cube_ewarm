# TOPPERS/ASP3 Core の STM32 CubeMX+ IAR Embedded Workbench for ARM(EWARM) 向け環境

本ドキュメントはasp3_stm32版をベースに記述してあります。差分は入れたつもりですが、大きな変更が無い場合はそのまま利用している部分もある点はご容赦ください。

[TOPPERS/ASP3 Core](https://github.com/exshonda/asp3_core)（TECSレス・Python cfg 版 ASP3）を、
STM32CubeMX、もしくはSTM32CubeM2が生成する HAL プロジェクトと協調動作させる環境です。
カーネル本体は git submodule（`asp3/asp3_core`）として取り込み、STM32 固有部
（チップ層・ターゲット依存部）を本リポジトリで管理します
（[asp3_pico_sdk](https://github.com/exshonda/asp3_pico_sdk)／
[asp3_fsp](https://github.com/exshonda/asp3_fsp) と同方式）。

## 対応ボードと検証状況

| ボード | MCU | ターゲット名 | 実機検証|
|---|---|---|---|
| NUCLEO-H563ZI | STM32H563ZI（Cortex-M33） | `stm32h563_nucleo` | sample1・test_porting 6/6・testexec 32 PASS （2026-06-12） |
| NUCLEO-C562RE | STM32C562RE（Cortex-M33） | `stm32c562_nucleo` | sample1・test_porting 6/6・testexec 32 PASS （2026-10-15）|


## 対応コンパイラ
IAR Embedded Workbench for ARM（EWARM）を使用。
今回使用したバージョンは9.70.4になります。

| ツール | コマンド名 | 
|---|---|
|Cコンパイラ | iccarm.exe |
|アセンブラ |  iasmarm.exe |
|リンカ     |  ilinkarm.exe |
|SREC生成  |  ielftool.exe |


## 関連ツール
| ツール | コマンド名 | 
|---|---|
|STM32CubeProg | EWARMで書き込む場合は不要。インストールしてPATH設定をしてください。|
|STM32CubeMX  |NUCLEO-H563ZIで使用します | 
|STM32CubeMX2  |NUCLEO-C562RE使用します | 
|CMake |  インストールしてPATHに設定してください。|
|PYTHON     |インストールしてPATHに設定してください。 |
|Ninja  |  EWARMにインストールしたものが利用できます。EWARMインストールフォルダの\common\binにあるので、ここもPATH設定してください。 |



## ディレクトリ構成

```
asp3_stm32cube_ewarm/
├── asp3
│   ├── CMakeLists.txt			# EWARM向けCMake設定
│   ├── arch/arm_iar_iccarm/stm32c5xx_stm32cube	# チップ層（C5共通）
│   ├── arch/arm_iar_iccarm/stm32h5xx_stm32cube	# チップ層（H5共通）
│   ├── asp3_core			# カーネル本体（git submodule・無変更）
│   ├── asp3_stm32cube.cmake 	# glue（ASP3_TARGET_DIR 等の解決）
│   ├── target/stm32c562_nucleo	# NUCLEO-C563RE ターゲット依存部
│   └── target/stm32h533_nucleo	# NUCLEO-H563ZI ターゲット依存部
├── docs			 	# 検証状況・残課題
├── nucleo_c562re/sample1		# CubeMX2 プロジェクト（C562RE.ioc2 が正本）
├── nucleo_h563zi/sample1		# CubeMX プロジェクト（H563ZI.ioc が正本）
└── scripts/testexec_stm32.py	# 実機向け機能テストランナー
```

## ビルド方法
ビルド方法については各ボードのsample1/Readme.mdを参照ください。


## 制限事項

- TECS には対応していません（asp3_core は TECS レス方針）。
- TrustZone（TZEN 有効）構成は未対応です。
- CubeMX 生成物に依存するため CI ではビルドしていません（実機環境で検証）。

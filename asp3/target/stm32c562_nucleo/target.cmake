#
#  ターゲット依存部のCMake定義（NUCLEO-C562RE / STM32C562 + STM32CubeC5）
#
#  外部（SDK）ターゲットのパス解決規約（asp3_core PORTING_GUIDE「外部ターゲット」）：
#   - 共通arch（arch/arm_iar_iccarm/common）・チップ依存部（stm32c5xx_stm32cube）・
#     ターゲット依存部はいずれも本リポジトリ側＝CMAKE_CURRENT_LIST_DIR 相対
#
set(ARCHDIR ${CMAKE_CURRENT_LIST_DIR}/../../arch/arm_iar_iccarm)
get_filename_component(CHIPDIR ${CMAKE_CURRENT_LIST_DIR}/../../arch/arm_iar_iccarm/stm32c5xx_stm32cube ABSOLUTE)
set(TARGETDIR ${CMAKE_CURRENT_LIST_DIR})

#
#  コンフィギュレーション関連（Ruby .trb → Python .py へ変換済み）
#
list(APPEND ASP3_CFG_FILES
    ${TARGETDIR}/target_kernel.cfg
)

list(APPEND ASP3_KERNEL_CFG_TRB_FILES
    ${TARGETDIR}/target_kernel.py
)

list(APPEND ASP3_CHECK_TRB_FILES
    ${TARGETDIR}/target_check.py
)

#
#  インクルードディレクトリ
#
#  STM32CubeMX2（CMSIS-Toolbox ベース）が生成するプロジェクトの構成に合わせる．
#  classic CubeMX の Core/ + Drivers/ ではなく，CMSIS パックを展開した
#  stm32c5xx_dfp（CMSIS デバイスヘッダ）・stm32c5xx_drivers（HAL2 と LL）・
#  arch/cmsis（CMSIS Core）・generated/hal（mx_*.c の生成初期化）に分かれる．
#
#  C5 ターゲットは HAL2 の API には依存せず，LL とレジスタ直接操作＋CMSIS
#  デバイスヘッダ（stm32c5xx.h）だけを使う．
#
list(APPEND ASP3_INCLUDE_DIRS
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/generated/hal
    ${CMAKE_SOURCE_DIR}/stm32c5xx_dfp/Include
    ${CMAKE_SOURCE_DIR}/stm32c5xx_drivers/hal
    ${CMAKE_SOURCE_DIR}/stm32c5xx_drivers/ll
    ${CMAKE_SOURCE_DIR}/stm32c5xx_drivers/utils
    ${CMAKE_SOURCE_DIR}/arch/cmsis/CMSIS/Core/Include
    ${TARGETDIR}
)

list(APPEND ASP3_COMPILE_DEFS
    USE_FULL_LL_DRIVER
    USE_HAL_DRIVER
    STM32C562xx
    $<$<CONFIG:Debug>:DEBUG>
    USE_TIM_AS_HRT
    TOPPERS_FPU_ENABLE
    TOPPERS_FPU_LAZYSTACKING
    TOPPERS_FPU_CONTEXT
)

#
#  Cortex-M33 + FPU（fpv5-sp-d16 / hard）— STM32C5 は単精度FPU付き Cortex-M33．
#  asp3 ライブラリと cfg1_out（オフセット抽出用ELF）に適用される．
#
list(APPEND ASP3_COMPILE_OPTIONS
    ${CPU_FLAGS}
    $<$<COMPILE_LANGUAGE:C>:-e>
)

#
#  cfg1_out（使い捨てELF）の最小リンク：arch（Cortex-M33/fpv5-sp-d16）＋ crt0回避．
#  CubeMX 実リンカスクリプトは不要（nm でのシンボル値抽出のみ）．
#
list(APPEND ASP3_LINK_OPTIONS
    #  未参照シンボル（TOPPERS_magic_number 等）を cfg1_out で消さない
    --no_remove
)

#
#  ターゲット依存部のソース（いずれも非TECS版）
#
list(APPEND ASP3_TARGET_C_FILES
    ${TARGETDIR}/target_kernel_impl.c
    ${TARGETDIR}/target_timer.c
    ${TARGETDIR}/target_serial.c
)

#
#  アーキ依存部（チップ層）のインクルード
#
include(${CHIPDIR}/arch.cmake)

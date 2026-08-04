

# EWARM setting
# 
set(TOOLCHAIN_FOLDER                c:/iar/ewarm-9.70.4/arm/bin)

set(CMAKE_C_COMPILER                ${TOOLCHAIN_FOLDER}/iccarm.exe)
set(CMAKE_ASM_COMPILER              ${TOOLCHAIN_FOLDER}/iasmarm.exe)
set(CMAKE_CXX_COMPILER              ${TOOLCHAIN_FOLDER}/iccarm.exe)
set(CMAKE_LINKER                    ${TOOLCHAIN_FOLDER}/ilinkarm.exe)
set(CMAKE_OBJCOPY                   ${TOOLCHAIN_FOLDER}/ielftool.exe)
set(CMAKE_PYTHON_NM                  map2symbol.py)
set(CMAKE_SIZE                      ${TOOLCHAIN_PREFIX}size)


set(CMAKE_EXECUTABLE_SUFFIX_ASM     ".elf")
set(CMAKE_EXECUTABLE_SUFFIX_C       ".elf")
set(CMAKE_EXECUTABLE_SUFFIX_CXX     ".elf")

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

# MCU specific flags
set(TARGET_FLAGS "--cpu=Cortex-M33.no_dsp.no_se --fpu=VFPv5_sp ")

set(CMAKE_C_FLAGS  "${TARGET_FLAGS}")



# The cyclomatic-complexity parameter must be defined for the Cyclomatic complexity feature in STM32CubeIDE to work.
# However, most GCC toolchains do not support this option, which causes a compilation error; for this reason, the feature is disabled by default.
# set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fcyclomatic-complexity")

set(CMAKE_C_FLAGS_DEBUG "-Ohz  --debug --endian=little --text_out utf8 --source_encoding utf8 --utf8_text_in ")
set(CMAKE_C_FLAGS_RELEASE "-Ohs  --debug --endian=little --text_out utf8 --source_encoding utf8 --utf8_text_in ")
set(CMAKE_CXX_FLAGS_DEBUG "--c++ -Ol -Ol --no_cse --no_unroll --no_inline --no_code_motion --no_tbaa --no_clustering --no_scheduling  -e  --debug --endian=little ")
set(CMAKE_CXX_FLAGS_RELEASE "c-++ -Oh  -e  --debug --endian=little ")


set(CMAKE_ASM_FLAGS "--cpu=Cortex-M33.no_dsp.no_se --fpu=VFPv5_sp --endian little --source_encoding utf8   ")




set(CMAKE_EXE_LINKER_FLAGS "${TARGET_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} --config \"${CMAKE_SOURCE_DIR}/stm32h563xx_flash.icf\"")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ")
set(TOOLCHAIN_LINK_LIBRARIES "")

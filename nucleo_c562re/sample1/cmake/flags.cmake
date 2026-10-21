# file-format: 1.0.0
if(CMAKE_BUILD_TYPE STREQUAL "debug_GCC_NUCLEO-C562RE")
  set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES SUFFIX ".elf")
  target_compile_options(${CMAKE_PROJECT_NAME} PUBLIC ${CPU_FLAGS})
  target_compile_options(${CMAKE_PROJECT_NAME} PUBLIC -Ohz --vla --dlib_config full ${CC_SECURE})
  target_include_directories(${CMAKE_PROJECT_NAME} PUBLIC . arch/cmsis/CMSIS/Core/Include generated/hal stm32c5xx_dfp/Include stm32c5xx_drivers/hal stm32c5xx_drivers/ll stm32c5xx_drivers/timebases user_modifiable/_debug_GCC_NUCLEO-C562RE)
  target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC STM32C562xx _RTE_)
  target_link_options(${CMAKE_PROJECT_NAME} PUBLIC --map=${CMAKE_PROJECT_NAME}.map --config ${CMAKE_SOURCE_DIR}/stm32c562xe_flash.icf ${CC_SECURE})
  set(LINK_CPU_FLAGS ${CPU_FLAGS})
  list(FILTER LINK_CPU_FLAGS EXCLUDE REGEX "^--endian")
  target_link_options(${CMAKE_PROJECT_NAME} PUBLIC ${LINK_CPU_FLAGS})
endif()

# Clean .map and .elf file
set_property(DIRECTORY APPEND PROPERTY ADDITIONAL_CLEAN_FILES "${CMAKE_SOURCE_DIR}/build/${CMAKE_BUILD_TYPE}/${CMAKE_PROJECT_NAME}.map")
set_property(DIRECTORY APPEND PROPERTY ADDITIONAL_CLEAN_FILES "${CMAKE_SOURCE_DIR}/build/${CMAKE_BUILD_TYPE}/${CMAKE_PROJECT_NAME}.elf")
kst_init(${kst_binary_name} core)

kst_include_directories(widgets)

kst_files_ignore(stdinsource timezones)

if(WIN32 OR APPLE OR QNX OR ${CMAKE_SYSTEM_NAME} MATCHES "FreeBSD")
	kst_files_ignore(sysinfo psversion)
else()
    if(NOT kst_clang)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -lrt")
    endif()
endif()

kst_files_find(src/libkst)

kst_dont_merge(sysinfo.c psversion.c)

kst_add_library(SHARED)

kst_link()

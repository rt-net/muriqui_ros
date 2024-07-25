cmake_minimum_required(VERSION 3.8)
project(muriqui_hardware)

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

add_compile_options(-g)

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rt_manipulators_cpp REQUIRED)
find_package(yaml_cpp_vendor REQUIRED)

set(LIBRARY_NAME "muriqui_hardware")
add_library(
  ${LIBRARY_NAME}
  SHARED
  src/muriqui_hardware.cpp
)
target_include_directories(
  ${LIBRARY_NAME}
  PRIVATE
  include
)
target_link_libraries(
  ${LIBRARY_NAME}
)
ament_target_dependencies(
  ${LIBRARY_NAME}
  hardware_interface
  pluginlib
  rclcpp
  rt_manipulators_cpp
)
pluginlib_export_plugin_description_file(hardware_interface muriqui_hardware.xml)
install(TARGETS
  ${LIBRARY_NAME}
  DESTINATION lib
)

add_executable(create_symbolic_links src/create_symbolic_links.cpp)
ament_target_dependencies(create_symbolic_links
  ament_index_cpp
  rclcpp
  rt_manipulators_cpp
)

install(TARGETS
  create_symbolic_links
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY include/
  DESTINATION include
)

install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}/
)

ament_python_install_package(${PROJECT_NAME})
install(PROGRAMS
  ${PROJECT_NAME}/muriqui_board_node.py
  ${PROJECT_NAME}/muriqui_comm.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)  # Skip copyright checks
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_muriqui_comm test/test_muriqui_comm.py)
endif()

ament_export_include_directories(
  include
)
ament_export_libraries(
  ${LIBRARY_NAME}
)
ament_export_dependencies(
  hardware_interface
  pluginlib
  rclcpp
  rt_manipulators_cpp
)

ament_package()

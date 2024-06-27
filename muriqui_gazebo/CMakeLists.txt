cmake_minimum_required(VERSION 3.8)
project(muriqui_gazebo)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  launch
  worlds
  gui
  DESTINATION share/${PROJECT_NAME}/
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)  # Skip copyright checks
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
cmake_minimum_required(VERSION 3.8)
project(muriqui_tools)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  scripts
  rules
  DESTINATION lib/${PROJECT_NAME}/
)

ament_package()

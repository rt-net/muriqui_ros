// Copyright 2024 RT Corporation

#include <iostream>
#include <map>
#include <streambuf>
#include <vector>

#include <cstdlib>

#include "ament_index_cpp/get_package_share_directory.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rt_manipulators_cpp/hardware.hpp"

using USBDeivce = std::string;
using GroupName = std::string;
using GroupNames = std::vector<GroupName>;
using HardwareSharedPtr = std::shared_ptr<rt_manipulators_cpp::Hardware>;
using USBHardwareMap = std::map<USBDeivce, HardwareSharedPtr>;
using USBGroupMap = std::map<USBDeivce, GroupName>;

void disable_cerr()
{
  std::cerr.setstate(std::ios_base::failbit);
}

void enable_cerr()
{
  std::cerr.clear();
}


std::vector<USBDeivce> search_usb_devices(const int min, const int max)
{
  std::vector<USBDeivce> active_device_list;

  for (auto i = min; i <= max; i++) {
    const auto device = "/dev/ttyUSB" + std::to_string(i);
    const auto command = "ls " + device + " 2> /dev/null";
    if (system(command.c_str()) == 0) {
      active_device_list.push_back(device);
    }
  }
  return active_device_list;
}


bool has_correct_joints(
  const std::shared_ptr<rt_manipulators_cpp::Hardware> & hardware,
  const int baudrate,
  const std::string & config_file_path)
{
  bool result = true;
  disable_cerr();
  try {
    if (!hardware->connect(baudrate)) {
      result = false;
    }

    if (!hardware->load_config_file(config_file_path)) {
      result = false;
    }
  } catch (const std::exception & e) {
    result = false;
  }
  enable_cerr();

  hardware->disconnect();
  return result;
}

USBGroupMap pair_usb_with_group(
  const GroupNames & group_names, const std::string & config_file_dir,
  const int baudrate, const std::vector<USBDeivce> & usb_devices,
  USBHardwareMap & hardware_list)
{
  USBGroupMap usb_group_map;
  auto usb_devices_copy = usb_devices;

  for (const auto & group : group_names) {
    const auto config_file_path = config_file_dir + "/" + group + ".yaml";
    std::cout << "---------------" << std::endl;
    std::cout << "Processing " << group << std::endl;
    std::cout << "config_file_path: " << config_file_path << std::endl;

    for (auto it = usb_devices_copy.begin(); it != usb_devices_copy.end(); it++) {
      std::cout << "----- Checking " << *it << std::endl;

      if (has_correct_joints(hardware_list[*it], baudrate, config_file_path)) {
        usb_group_map[*it] = group;
        usb_devices_copy.erase(it);
        break;
      }
    }
  }

  return usb_group_map;
}


bool input_is_yes(const std::string & message)
{
  std::vector<std::string> yes_list = {"y", "Y", "yes", "Yes", "YES"};
  std::string input;
  std::cout << message << " [y/n]: ";
  std::cin >> input;
  return std::find(yes_list.begin(), yes_list.end(), input) != yes_list.end();
}


std::string remove_prefix(std::string str, const std::string & prefix)
{
  if (str.substr(0, prefix.size()) == prefix) {
    return str.substr(prefix.size());
  }
  return str;
}


void create_symbolic_links(const USBGroupMap & usb_group_map)
{
  for (const auto & [usb_device, group] : usb_group_map) {
    const auto unlink_command = "sudo unlink /dev/muriqui_" + group + " 2> /dev/null";
    system(unlink_command.c_str());

    const auto link_command = "sudo ln -s " + usb_device + " /dev/muriqui_" + group;
    system(link_command.c_str());
  }
}


void set_latency_timer_to_1(const USBGroupMap & usb_group_map)
{
  for (const auto & [usb_device, group] : usb_group_map) {
    const auto ttyUSB = remove_prefix(usb_device, "/dev/");
    const auto device_path = "/sys/bus/usb-serial/devices/" + ttyUSB + "/latency_timer";
    const auto permission_command = "sudo chmod a+rw " + device_path;
    system(permission_command.c_str());

    const auto set_latency_timer_command = "sudo echo 1 > " + device_path;
    system(set_latency_timer_command.c_str());
  }
}


int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::NodeOptions node_options;
  node_options.allow_undeclared_parameters(true);
  node_options.automatically_declare_parameters_from_overrides(true);

  auto node = std::make_shared<rclcpp::Node>("create_symbolic_links", node_options);

  int search_usb_min_number = 0;
  int search_usb_max_number = 30;
  std::vector<std::string> group_names = {
    "right_arm", "right_leg",
    "left_arm", "left_leg",
    "neck"
  };
  std::string config_file_dir = ament_index_cpp::get_package_share_directory(
    "muriqui_hardware") + "/config";
  int baudrate = 4000000;

  node->get_parameter("search_usb_min_number", search_usb_min_number);
  node->get_parameter("search_usb_max_number", search_usb_max_number);
  node->get_parameter("group_names", group_names);
  node->get_parameter("config_file_dir", config_file_dir);
  node->get_parameter("baudrate", baudrate);

  std::cout << "Search USB devices: " << std::endl;
  const auto usb_devices = search_usb_devices(search_usb_min_number, search_usb_max_number);

  if (usb_devices.size() < group_names.size()) {
    std::cerr << "Not enough USB devices found. Exiting." << std::endl;
    rclcpp::shutdown();
    return 1;
  }

  USBHardwareMap usb_hardware_map;
  for (const auto & usb_device : usb_devices) {
    usb_hardware_map[usb_device] = std::make_shared<rt_manipulators_cpp::Hardware>(usb_device);
  }

  const auto usb_group_map = pair_usb_with_group(
    group_names, config_file_dir, baudrate, usb_devices, usb_hardware_map);

  std::cout << "---------------" << std::endl;
  std::cout << "The following symbolic links are proposed to be created." << std::endl;
  for (const auto & pair : usb_group_map) {
    std::cout << "USB device: " << pair.first << " to /dev/muriqui_" << pair.second << std::endl;
  }

  if (usb_group_map.size() != group_names.size()) {
    std::cerr << "The size of USB devices is not equal to group names. Exiting." << std::endl;
    rclcpp::shutdown();
    return 1;
  }

  if (!input_is_yes("Do you want to create symbolic links?")) {
    std::cout << "Cancel. Exiting." << std::endl;
    rclcpp::shutdown();
    return 0;
  }

  create_symbolic_links(usb_group_map);
  set_latency_timer_to_1(usb_group_map);

  for (auto & hardware : usb_hardware_map) {
    hardware.second->disconnect();
  }
  std::cout << "Finish." << std::endl;
  rclcpp::shutdown();

  return 0;
}

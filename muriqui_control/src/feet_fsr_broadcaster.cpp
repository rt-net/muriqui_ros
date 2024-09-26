// Copyright 2024 RT Corporation

#include "muriqui_control/feet_fsr_broadcaster.hpp"

namespace feet_fsr_broadcaster
{
controller_interface::CallbackReturn FeetFSRBroadcaster::on_init()
{
  param_names_ = {
    "r_front_right", "r_front_left", "r_rear_right", "r_rear_left",
    "l_front_right", "l_front_left", "l_rear_right", "l_rear_left"};

  try {
    // Declare ROS parameters
    for (const auto & param_name : param_names_) {
      auto_declare<std::string>("interface_names." + param_name, std::string());
      auto_declare<std::string>("frame_ids." + param_name, std::string());
    }
  } catch (const std::exception & e) {
    fprintf(stderr, "Exception thrown during init stage with message: %s \n", e.what());
    return controller_interface::CallbackReturn::ERROR;
  }

  return controller_interface::CallbackReturn::SUCCESS;
}

controller_interface::CallbackReturn FeetFSRBroadcaster::on_configure(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  try {
    for (const auto & param_name : param_names_) {
      const auto full_param_name = "interface_names." + param_name;
      auto interface_name = get_node()->get_parameter(full_param_name).as_string();

      if (interface_name.empty()) {
        RCLCPP_ERROR(get_node()->get_logger(), "Parameter '%s' is empty", full_param_name.c_str());
        return controller_interface::CallbackReturn::ERROR;
      }
      interface_to_param_[interface_name] = param_name;

      wrench_stamped_publishers_[param_name] =
        get_node()->create_publisher<WrenchStampedMsg>(
        "~/" + param_name,
        rclcpp::SystemDefaultsQoS());
      realtime_publishers_[param_name] = std::make_unique<WrenchStampedPublisher>(
        wrench_stamped_publishers_[param_name]);
    }
  } catch (const std::exception & e) {
    fprintf(
      stderr, "Exception thrown at configuration stage with message : %s \n",
      e.what());
    return LifecycleNodeInterface::CallbackReturn::ERROR;
  }

  for (const auto & param_name : param_names_) {
    realtime_publishers_[param_name]->lock();
    const auto frame_id = get_node()->get_parameter("frame_ids." + param_name).as_string();
    realtime_publishers_[param_name]->msg_.header.frame_id = frame_id;
    realtime_publishers_[param_name]->msg_.wrench.force.z = 0.0;
    realtime_publishers_[param_name]->unlock();
  }

  return LifecycleNodeInterface::CallbackReturn::SUCCESS;
}


controller_interface::InterfaceConfiguration FeetFSRBroadcaster::command_interface_configuration()
const
{
  controller_interface::InterfaceConfiguration config;
  config.type = controller_interface::interface_configuration_type::NONE;

  return config;
}

controller_interface::InterfaceConfiguration FeetFSRBroadcaster::state_interface_configuration()
const
{
  controller_interface::InterfaceConfiguration config;
  config.type = controller_interface::interface_configuration_type::INDIVIDUAL;
  for (const auto & [interface_name, param_name] : interface_to_param_) {
    config.names.push_back(interface_name);
  }

  return config;
}

controller_interface::CallbackReturn FeetFSRBroadcaster::on_activate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  try {
    for (size_t i = 0; i < state_interfaces_.size(); i++) {
      param_to_handle_[interface_to_param_[state_interfaces_[i].get_name()]] = i;
    }
  } catch (const std::exception & e) {
    fprintf(
      stderr, "Exception thrown at activation stage with message : %s \n",
      e.what());
    return LifecycleNodeInterface::CallbackReturn::ERROR;
  }

  return LifecycleNodeInterface::CallbackReturn::SUCCESS;
}

controller_interface::CallbackReturn FeetFSRBroadcaster::on_deactivate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  return LifecycleNodeInterface::CallbackReturn::SUCCESS;
}

controller_interface::return_type FeetFSRBroadcaster::update(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  for (const auto & param_name : param_names_) {
    if (realtime_publishers_[param_name] && realtime_publishers_[param_name]->trylock()) {
      realtime_publishers_[param_name]->msg_.header.stamp = get_node()->now();
      realtime_publishers_[param_name]->msg_.wrench.force.z =
        state_interfaces_[param_to_handle_[param_name]].get_value();
      realtime_publishers_[param_name]->unlockAndPublish();
    }
  }

  return controller_interface::return_type::OK;
}

}  // namespace feet_fsr_broadcaster

#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(
  feet_fsr_broadcaster::FeetFSRBroadcaster, controller_interface::ControllerInterface)

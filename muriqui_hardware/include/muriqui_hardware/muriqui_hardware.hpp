// Copyright 2024 RT Corporation


#ifndef MURIQUI_HARDWARE__MURIQUI_HARDWARE_HPP_
#define MURIQUI_HARDWARE__MURIQUI_HARDWARE_HPP_

#include <map>
#include <memory>
#include <string>
#include <vector>

#include "muriqui_hardware/visibility_control.h"
#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/macros.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rt_manipulators_cpp/hardware.hpp"
#include "rclcpp_lifecycle/state.hpp"

using hardware_interface::return_type;
using hardware_interface::CallbackReturn;

namespace muriqui_hardware
{
class MuriquiHardware : public
  hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(MuriquiHardware)

  MURIQUI_HARDWARE_PUBLIC
  ~MuriquiHardware();

  MURIQUI_HARDWARE_PUBLIC
  CallbackReturn on_init(const hardware_interface::HardwareInfo & info) override;

  MURIQUI_HARDWARE_PUBLIC
  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;

  MURIQUI_HARDWARE_PUBLIC
  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

  MURIQUI_HARDWARE_PUBLIC
  CallbackReturn on_activate(const rclcpp_lifecycle::State & previous_state) override;

  MURIQUI_HARDWARE_PUBLIC
  CallbackReturn on_deactivate(const rclcpp_lifecycle::State & previous_state) override;

  MURIQUI_HARDWARE_PUBLIC
  return_type read(const rclcpp::Time & time, const rclcpp::Duration & period) override;

  MURIQUI_HARDWARE_PUBLIC
  return_type write(const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  bool communication_timeout();
  double fsr_voltage_to_force(double voltage) const;

  std::shared_ptr<rt_manipulators_cpp::Hardware> hardware_;
  double timeout_seconds_;

  std::map<std::string, double> hw_position_commands_;
  std::map<std::string, double> hw_position_states_;
  std::map<std::string, double> hw_velocity_states_;
  std::map<std::string, double> hw_effort_states_;

  double hw_fsr_front_right_ = 0.0;
  double hw_fsr_front_left_ = 0.0;
  double hw_fsr_rear_left_ = 0.0;
  double hw_fsr_rear_right_ = 0.0;

  std::map<std::string, double> current_to_effort_;
  bool has_fsr_sensor_ = false;
  std::string fsr_front_joint_name_;
  std::string fsr_rear_joint_name_;

  rclcpp::Clock steady_clock_;
  rclcpp::Time prev_comm_timestamp_;
  bool timeout_has_printed_;
};
}  // namespace muriqui_hardware

#endif  // MURIQUI_HARDWARE__MURIQUI_HARDWARE_HPP_

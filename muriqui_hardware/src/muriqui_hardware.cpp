// Copyright 2024 RT Corporation

#include <yaml-cpp/yaml.h>

#include <limits>
#include <memory>
#include <string>
#include <vector>

#include "muriqui_hardware/muriqui_hardware.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"


namespace muriqui_hardware
{
static rclcpp::Logger LOGGER = rclcpp::get_logger("MuriquiHardware");
constexpr auto GROUP_NAME = "group";

MuriquiHardware::~MuriquiHardware()
{
  if (hardware_) {
    hardware_->disconnect();
  }
}

CallbackReturn MuriquiHardware::on_init(
  const hardware_interface::HardwareInfo & info)
{
  if (hardware_interface::SystemInterface::on_init(info) != CallbackReturn::SUCCESS) {
    return CallbackReturn::ERROR;
  }

  for (const auto & joint : info_.joints) {
    hw_position_commands_[joint.name] = std::numeric_limits<double>::quiet_NaN();
    hw_position_states_[joint.name] = std::numeric_limits<double>::quiet_NaN();
    hw_velocity_states_[joint.name] = std::numeric_limits<double>::quiet_NaN();
    hw_effort_states_[joint.name] = std::numeric_limits<double>::quiet_NaN();

    // Load joint parameters
    if (joint.parameters.at("current_to_effort") != "") {
      current_to_effort_[joint.name] = std::stod(joint.parameters.at("current_to_effort"));
    } else {
      RCLCPP_ERROR(
        LOGGER, "Joint '%s' does not have 'current_to_effort' parameter.",
        joint.name.c_str());
      return CallbackReturn::ERROR;
    }
  }

  for (const auto & joint : info_.joints) {
    if (joint.command_interfaces.size() != 1) {
      RCLCPP_FATAL(
        LOGGER,
        "Joint '%s' has %ld command interfaces. 1 expected.",
        joint.name.c_str(), joint.command_interfaces.size());
      return CallbackReturn::ERROR;
    }

    if (!(joint.command_interfaces[0].name == hardware_interface::HW_IF_POSITION)) {
      RCLCPP_FATAL(
        LOGGER,
        "Joint '%s' has %s command interface. Expected %s, %s, or %s.", joint.name.c_str(),
        joint.command_interfaces[0].name.c_str(), hardware_interface::HW_IF_POSITION,
        hardware_interface::HW_IF_VELOCITY, hardware_interface::HW_IF_ACCELERATION);
      return CallbackReturn::ERROR;
    }

    if (joint.state_interfaces.size() < 1) {
      RCLCPP_FATAL(
        LOGGER,
        "Joint '%s'has %ld state interfaces. At least 1 expected.",
        joint.name.c_str(), joint.state_interfaces.size());
      return CallbackReturn::ERROR;
    }

    for (const auto & state_interface : joint.state_interfaces) {
      if (!(state_interface.name == hardware_interface::HW_IF_POSITION ||
        state_interface.name == hardware_interface::HW_IF_VELOCITY ||
        state_interface.name == hardware_interface::HW_IF_EFFORT))
      {
        RCLCPP_FATAL(
          LOGGER,
          "Joint '%s' has %s state interface. Expected %s, %s, or %s.", joint.name.c_str(),
          joint.state_interfaces[0].name.c_str(), hardware_interface::HW_IF_POSITION,
          hardware_interface::HW_IF_VELOCITY, hardware_interface::HW_IF_EFFORT);
        return CallbackReturn::ERROR;
      }
    }
  }

  for (const auto & sensor : info_.sensors) {
    // Load sensor parameters
    if (sensor.parameters.at("front_joint") != "") {
      fsr_front_joint_name_ = sensor.parameters.at("front_joint");
    } else {
      RCLCPP_ERROR(
        LOGGER, "Sensor '%s' does not have 'front_joint' parameter.",
        sensor.name.c_str());
      return CallbackReturn::ERROR;
    }

    if (sensor.parameters.at("rear_joint") != "") {
      fsr_rear_joint_name_ = sensor.parameters.at("rear_joint");
    } else {
      RCLCPP_ERROR(
        LOGGER, "Sensor '%s' does not have 'rear_joint' parameter.",
        sensor.name.c_str());
      return CallbackReturn::ERROR;
    }

    has_fsr_sensor_ = true;
  }

  const auto port_name = info_.hardware_parameters["port_name"];
  const auto baudrate = std::stoi(info_.hardware_parameters["baudrate"]);
  const auto config_file_path = info_.hardware_parameters["manipulator_config_file_path"];
  hardware_ = std::make_shared<rt_manipulators_cpp::Hardware>(port_name);

  if (!hardware_->connect(baudrate)) {
    RCLCPP_ERROR(LOGGER, "Failed to connect a robot.");
    return CallbackReturn::ERROR;
  }

  if (!hardware_->load_config_file(config_file_path)) {
    RCLCPP_ERROR(LOGGER, "Failed to read a config file.");
    return CallbackReturn::ERROR;
  }

  // Load PID gains from config file and set them to the joints.
  YAML::Node config = YAML::LoadFile(config_file_path);
  for (const auto & joint : info_.joints) {
    if (!config[joint.name]) {
      continue;
    }

    YAML::Node params = config[joint.name];
    if (!params["pos_p"] || !params["pos_i"] || !params["pos_d"]) {
      continue;
    }

    if (!hardware_->write_position_pid_gain(
        joint.name,
        params["pos_p"].as<int>(),
        params["pos_i"].as<int>(),
        params["pos_d"].as<int>()))
    {
      RCLCPP_ERROR(LOGGER, "Failed to set PID gain to joint '%s'.", joint.name.c_str());
      return CallbackReturn::ERROR;
    }
  }

  timeout_seconds_ = std::stod(info_.hardware_parameters["timeout_seconds"]);
  steady_clock_ = rclcpp::Clock(RCL_STEADY_TIME);

  return CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface>
MuriquiHardware::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;
  for (const auto & joint : info_.joints) {
    state_interfaces.emplace_back(
      hardware_interface::StateInterface(
        joint.name, hardware_interface::HW_IF_POSITION, &hw_position_states_[joint.name]));

    state_interfaces.emplace_back(
      hardware_interface::StateInterface(
        joint.name, hardware_interface::HW_IF_VELOCITY, &hw_velocity_states_[joint.name]));

    state_interfaces.emplace_back(
      hardware_interface::StateInterface(
        joint.name, hardware_interface::HW_IF_EFFORT, &hw_effort_states_[joint.name]));
  }

  for (const auto & sensor : info_.sensors) {
    state_interfaces.emplace_back(
      hardware_interface::StateInterface(sensor.name, "front_right", &hw_fsr_front_right_));
    state_interfaces.emplace_back(
      hardware_interface::StateInterface(sensor.name, "front_left", &hw_fsr_front_left_));
    state_interfaces.emplace_back(
      hardware_interface::StateInterface(sensor.name, "rear_left", &hw_fsr_rear_left_));
    state_interfaces.emplace_back(
      hardware_interface::StateInterface(sensor.name, "rear_right", &hw_fsr_rear_right_));
  }

  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface>
MuriquiHardware::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;
  for (const auto & joint : info_.joints) {
    command_interfaces.emplace_back(
      hardware_interface::CommandInterface(
        joint.name, hardware_interface::HW_IF_POSITION, &hw_position_commands_[joint.name]));
  }

  return command_interfaces;
}

CallbackReturn MuriquiHardware::on_activate(const rclcpp_lifecycle::State & /*previous_state*/)
{
  // Set current timestamp to disable the communication timeout.
  prev_comm_timestamp_ = steady_clock_.now();
  timeout_has_printed_ = false;

  // Set present joint positions to hw_position_commands for safe start-up.
  read(prev_comm_timestamp_, rclcpp::Duration::from_seconds(0));
  for (const auto & joint : info_.joints) {
    const auto present_position = hw_position_states_[joint.name];
    auto limit_min = present_position;
    auto limit_max = present_position;
    for (const auto & interface : joint.command_interfaces) {
      if (interface.name == "position") {
        limit_min = std::stod(interface.min);
        limit_max = std::stod(interface.max);
      }
    }
    hw_position_commands_[joint.name] = std::clamp(present_position, limit_min, limit_max);
  }
  write(prev_comm_timestamp_, rclcpp::Duration::from_seconds(0));

  if (!hardware_->torque_on(GROUP_NAME)) {
    RCLCPP_ERROR(LOGGER, "Failed to set torque on.");
    return CallbackReturn::ERROR;
  }

  return CallbackReturn::SUCCESS;
}

CallbackReturn MuriquiHardware::on_deactivate(const rclcpp_lifecycle::State & /*previous_state*/)
{
  return CallbackReturn::SUCCESS;
}

return_type MuriquiHardware::read(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  if (communication_timeout()) {
    if (!timeout_has_printed_) {
      RCLCPP_ERROR(LOGGER, "Communication timeout!");
      timeout_has_printed_ = true;
    }
    return return_type::ERROR;
  }

  if (!hardware_->sync_read(GROUP_NAME)) {
    RCLCPP_ERROR(LOGGER, "Failed to sync read from servo motors.");
    RCLCPP_ERROR(LOGGER, "  Joints: ");
    for (const auto & joint : info_.joints) {
      RCLCPP_ERROR(LOGGER, "    %s", joint.name.c_str());
    }
    // Keep communication even if sync_read fails.
    // Return OK to avoid setting uncertain data in following processes.
    return return_type::OK;
  }

  for (const auto & joint : info_.joints) {
    hardware_->get_position(joint.name, hw_position_states_[joint.name]);
  }

  for (const auto & joint : info_.joints) {
    hardware_->get_velocity(joint.name, hw_velocity_states_[joint.name]);
  }

  double current;
  for (const auto & joint : info_.joints) {
    hardware_->get_current(joint.name, current);
    hw_effort_states_[joint.name] = current * current_to_effort_[joint.name];
  }

  if (has_fsr_sensor_) {
    double voltage_front_right, voltage_front_left, voltage_rear_left, voltage_rear_right;
    auto result =
      hardware_->get_external_port_voltage(fsr_front_joint_name_, 1, voltage_front_right) &&
      hardware_->get_external_port_voltage(fsr_front_joint_name_, 2, voltage_front_left) &&
      hardware_->get_external_port_voltage(fsr_rear_joint_name_, 1, voltage_rear_left) &&
      hardware_->get_external_port_voltage(fsr_rear_joint_name_, 2, voltage_rear_right);

    if (!result) {
      RCLCPP_ERROR(LOGGER, "Failed to read FSR sensor's data.");
    } else {
      hw_fsr_front_right_ = fsr_voltage_to_force(voltage_front_right);
      hw_fsr_front_left_ = fsr_voltage_to_force(voltage_front_left);
      hw_fsr_rear_left_ = fsr_voltage_to_force(voltage_rear_left);
      hw_fsr_rear_right_ = fsr_voltage_to_force(voltage_rear_right);
    }
  }

  prev_comm_timestamp_ = steady_clock_.now();
  return return_type::OK;
}

return_type MuriquiHardware::write(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  if (communication_timeout()) {
    if (!timeout_has_printed_) {
      RCLCPP_ERROR(LOGGER, "Communication timeout!");
      timeout_has_printed_ = true;
    }
    return return_type::ERROR;
  }

  for (const auto & joint : info_.joints) {
    hardware_->set_position(joint.name, hw_position_commands_[joint.name]);
  }

  if (!hardware_->sync_write(GROUP_NAME)) {
    RCLCPP_ERROR(LOGGER, "Failed to sync write to servo motors.");
    RCLCPP_ERROR(LOGGER, "  Joints: ");
    for (const auto & joint : info_.joints) {
      RCLCPP_ERROR(LOGGER, "    %s", joint.name.c_str());
    }
  }
  // Do not update timestamp here
  // because sync_write does not return an error when Motor power is off
  return return_type::OK;
}

bool MuriquiHardware::communication_timeout()
{
  if (steady_clock_.now().seconds() - prev_comm_timestamp_.seconds() >= timeout_seconds_) {
    return true;
  } else {
    return false;
  }
}

double MuriquiHardware::fsr_voltage_to_force(double voltage) const
{
  constexpr double R_LOWER = 1.5;  // kOhm
  constexpr double VCC = 3.3;  // V
  constexpr double FSR_EXPONENT = -1.0 / 0.699;
  constexpr double FSR_COEFFICIENT = 1.0 / 153.18;
  constexpr double WEIGHT_TO_FORCE = 1.0E-03 * 9.81;  // kgf to N

  if (voltage == 0.0) {
    return 0.0;
  }

  double resistance = R_LOWER * (VCC / voltage - 1.0);
  double weight = std::pow(FSR_COEFFICIENT * resistance, FSR_EXPONENT);
  return weight * WEIGHT_TO_FORCE;
}

}  // namespace muriqui_hardware

#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(
  muriqui_hardware::MuriquiHardware,
  hardware_interface::SystemInterface)

// Copyright 2024 RT Corporation

#ifndef MURIQUI_CONTROL__FEET_FSR_BROADCASTER_HPP_
#define MURIQUI_CONTROL__FEET_FSR_BROADCASTER_HPP_

#include <map>
#include <memory>
#include <string>
#include <vector>

#include "controller_interface/controller_interface.hpp"
#include "geometry_msgs/msg/wrench_stamped.hpp"
#include "realtime_tools/realtime_publisher.h"

namespace feet_fsr_broadcaster
{

using WrenchStampedMsg = geometry_msgs::msg::WrenchStamped;
using WrenchStampedPublisher = realtime_tools::RealtimePublisher<WrenchStampedMsg>;

class FeetFSRBroadcaster : public controller_interface::ControllerInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(FeetFSRBroadcaster)

  CallbackReturn on_init() override;

  CallbackReturn on_configure(const rclcpp_lifecycle::State & previous_state) override;

  controller_interface::InterfaceConfiguration command_interface_configuration() const override;

  controller_interface::InterfaceConfiguration state_interface_configuration() const override;

  CallbackReturn on_activate(const rclcpp_lifecycle::State & previous_state) override;

  CallbackReturn on_deactivate(const rclcpp_lifecycle::State & previous_state) override;

  controller_interface::return_type update(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

protected:
  std::map<std::string, rclcpp::Publisher<WrenchStampedMsg>::SharedPtr> wrench_stamped_publishers_;
  std::map<std::string, std::unique_ptr<WrenchStampedPublisher>> realtime_publishers_;

private:
  std::vector<std::string> param_names_;
  std::map<std::string, std::string> interface_to_param_;
  std::map<std::string, unsigned int> param_to_handle_;
};

}  // namespace feet_fsr_broadcaster

#endif  // MURIQUI_CONTROL__FEET_FSR_BROADCASTER_HPP_

FROM ros:humble-ros-base
WORKDIR /ros2_ws
COPY ros2_ws/src ./src
RUN . /opt/ros/humble/setup.sh && colcon build
ENV FAULT_MODE=false
CMD ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 run my_robot_app sensor_node"]

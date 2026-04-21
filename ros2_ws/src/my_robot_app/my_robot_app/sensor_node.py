#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random
import os

class SensorNode(Node):
    def __init__(self):
        super().__init__('sensor_node')
        self.publisher = self.create_publisher(Float32, 'sensor/temperature', 10)
        self.timer = self.create_timer(2.0, self.publish_reading)
        self.fault_mode = os.environ.get("FAULT_MODE", "false") == "true"

    def publish_reading(self):
        msg = Float32()
        msg.data = 999.9 if self.fault_mode else round(random.uniform(20.0, 25.0), 2)
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(SensorNode())

if __name__ == '__main__':
    main()

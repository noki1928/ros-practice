import signal

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from turtlesim_msgs.msg import Pose


def sensor_qos(depth: int = 10) -> QoSProfile:
    return QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=depth,
        reliability=ReliabilityPolicy.BEST_EFFORT,
    )


class PoseRelay(Node):

    def __init__(self) -> None:
        super().__init__('pose_relay')

        self.publisher = self.create_publisher(
            Pose,
            'sensor_pose',
            sensor_qos(),
        )

        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.on_pose,
            10,
        )

        self.get_logger().info(
            f'Relaying /turtle1/pose to {self.publisher.topic_name} '
            'with best_effort reliability'
        )

    def on_pose(self, message: Pose) -> None:
        self.publisher.publish(message)


def main(args=None) -> None:
    rclpy.init(args=args)

    node = PoseRelay()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        # Ctrl+C reaches the node twice (terminal and launch); ignore the
        # second SIGINT so it does not interrupt cleanup.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

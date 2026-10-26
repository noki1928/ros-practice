import signal

import rclpy
from rclpy.event_handler import (
    QoSRequestedIncompatibleQoSInfo,
    SubscriptionEventCallbacks,
)
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import (
    HistoryPolicy,
    QoSPolicyKind,
    QoSProfile,
    ReliabilityPolicy,
)
from turtlesim_msgs.msg import Pose

RELIABILITY = {
    'reliable': ReliabilityPolicy.RELIABLE,
    'best_effort': ReliabilityPolicy.BEST_EFFORT,
}


def listener_qos(reliability: str, depth: int = 10) -> QoSProfile:
    if reliability not in RELIABILITY:
        raise ValueError(
            'reliability must be one of: ' + ', '.join(RELIABILITY)
        )

    return QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=depth,
        reliability=RELIABILITY[reliability],
    )


class SensorListener(Node):

    def __init__(self) -> None:
        super().__init__('sensor_listener')

        self.declare_parameter('reliability', 'best_effort')
        self.declare_parameter('report_period', 2.0)

        self.reliability = self.get_parameter('reliability').value
        report_period = self.get_parameter('report_period').value

        self.received = 0
        self.received_in_period = 0

        self.subscription = self.create_subscription(
            Pose,
            'sensor_pose',
            self.on_pose,
            listener_qos(self.reliability),
            event_callbacks=SubscriptionEventCallbacks(
                incompatible_qos=self.on_incompatible_qos,
            ),
        )

        self.timer = self.create_timer(report_period, self.report)

        self.get_logger().info(
            f'Listening on {self.subscription.topic_name} '
            f'with {self.reliability} reliability'
        )

    def on_pose(self, message: Pose) -> None:
        self.received += 1
        self.received_in_period += 1

    def on_incompatible_qos(
        self,
        event: QoSRequestedIncompatibleQoSInfo,
    ) -> None:
        policy = QoSPolicyKind(event.last_policy_kind).name
        self.get_logger().warning(
            f'Incompatible QoS with publisher on '
            f'{self.subscription.topic_name}: policy {policy}, '
            f'total {event.total_count}'
        )

    def report(self) -> None:
        self.get_logger().info(
            f'received {self.received_in_period} messages in period, '
            f'{self.received} total'
        )
        self.received_in_period = 0


def main(args=None) -> None:
    rclpy.init(args=args)

    node = SensorListener()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        # Ctrl+C reaches the node twice (terminal and launch); ignore the
        # second SIGINT so it does not interrupt cleanup.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    finally:
        # Shutting down first stops the global executor, which releases the
        # node handles; otherwise destroy_node() may wait for them forever.
        rclpy.try_shutdown()
        node.destroy_node()


if __name__ == '__main__':
    main()

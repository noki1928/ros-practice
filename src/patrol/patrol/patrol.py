import math
import signal

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import SetParametersResult
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from turtlesim_msgs.msg import Pose


def validate_parameters(
    linear_speed: float,
    turn_rate: float,
    publish_hz: float,
) -> str:
    if not all(math.isfinite(value) for value in (
        linear_speed, turn_rate, publish_hz,
    )):
        return 'All parameter values must be finite'

    if not 0.0 <= linear_speed <= 1.0:
        return 'linear_speed must be between 0 and 1'

    if not -1.0 <= turn_rate <= 1.0:
        return 'turn_rate must be between -1 and 1'

    if not 1.0 <= publish_hz <= 30.0:
        return 'publish_hz must be between 1 and 30'

    return ''


def command_for_pose(
    pose: Pose | None,
    linear_value: float = 0.5,
    angular_value: float = 0.3,
) -> Twist:
    if pose is None:
        return Twist()

    command = Twist()
    command.linear.x = linear_value
    command.angular.z = angular_value

    return command


class Patrol(Node):

    def __init__(self) -> None:
        super().__init__('patrol')

        self.latest_pose: Pose | None = None

        self.declare_parameter('linear_speed', 0.5)
        self.declare_parameter('turn_rate', 0.3)
        self.declare_parameter('publish_hz', 10.0)

        self.linear_speed = self.get_parameter('linear_speed').value
        self.turn_rate = self.get_parameter('turn_rate').value
        self.publish_hz = self.get_parameter('publish_hz').value

        reason = validate_parameters(
            self.linear_speed,
            self.turn_rate,
            self.publish_hz,
        )
        if reason:
            raise ValueError(reason)

        self.pose_sub = self.create_subscription(
            Pose,
            'turtle1/pose',
            self.on_pose,
            10,
        )

        self.publisher = self.create_publisher(
            Twist,
            'turtle1/cmd_vel',
            10,
        )

        self.timer = self.create_timer(
            1.0 / self.publish_hz,
            self.tick,
        )

        self.add_on_set_parameters_callback(self.on_parameters)

    def on_parameters(self, parameters) -> SetParametersResult:
        candidate = {
            'linear_speed': self.linear_speed,
            'turn_rate': self.turn_rate,
            'publish_hz': self.publish_hz,
        }

        for parameter in parameters:
            if parameter.name in candidate:
                value = parameter.value

                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                ):
                    return SetParametersResult(
                        successful=False,
                        reason=f'{parameter.name} must be a number',
                    )

                candidate[parameter.name] = float(value)

        reason = validate_parameters(
            candidate['linear_speed'],
            candidate['turn_rate'],
            candidate['publish_hz'],
        )

        if reason:
            return SetParametersResult(
                successful=False,
                reason=reason,
            )

        if candidate['publish_hz'] != self.publish_hz:
            new_period = 1.0 / candidate['publish_hz']

            self.timer.cancel()
            self.destroy_timer(self.timer)
            self.timer = self.create_timer(new_period, self.tick)

        self.linear_speed = candidate['linear_speed']
        self.turn_rate = candidate['turn_rate']
        self.publish_hz = candidate['publish_hz']

        return SetParametersResult(successful=True)

    def on_pose(self, message: Pose) -> None:
        self.latest_pose = message

    def tick(self) -> None:
        command = command_for_pose(
            self.latest_pose,
            self.linear_speed,
            self.turn_rate,
        )
        self.publisher.publish(command)


def main(args=None) -> None:
    rclpy.init(args=args)

    node = Patrol()

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

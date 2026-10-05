from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim_msgs.msg import Pose


def command_for_pose(pose: Pose | None) -> Twist:
    if pose is None:
        return Twist()

    command = Twist()
    command.linear.x = 0.5
    command.angular.z = 0.3

    return command


class Patrol(Node):

    def __init__(self) -> None:
        super().__init__('patrol')

        self.latest_pose: Pose | None = None

        self.pose_sub = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.on_pose,
            10,
        )

        self.publisher = self.create_publisher(
            Twist,
            'cmd_vel',
            10,
        )

        self.timer = self.create_timer(0.1, self.tick)

    def on_pose(self, message: Pose) -> None:
        self.latest_pose = message

    def tick(self) -> None:
        command = command_for_pose(self.latest_pose)
        self.publisher.publish(command)


def main(args=None) -> None:
    rclpy.init(args=args)

    node = Patrol()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

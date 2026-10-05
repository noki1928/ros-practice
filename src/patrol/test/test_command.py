from geometry_msgs.msg import Twist
from patrol.patrol import command_for_pose
from turtlesim_msgs.msg import Pose


def test_command_without_pose_is_zero_twist():
    command = command_for_pose(None)

    assert isinstance(command, Twist)
    assert command.linear.x == 0.0
    assert command.linear.y == 0.0
    assert command.linear.z == 0.0
    assert command.angular.x == 0.0
    assert command.angular.y == 0.0
    assert command.angular.z == 0.0


def test_command_with_pose_has_expected_velocity():
    pose = Pose()

    command = command_for_pose(pose)

    assert command.linear.x == 0.5
    assert command.linear.y == 0.0
    assert command.linear.z == 0.0
    assert command.angular.x == 0.0
    assert command.angular.y == 0.0
    assert command.angular.z == 0.3

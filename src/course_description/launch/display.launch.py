import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share = get_package_share_directory('course_description')

    robot_description = ParameterValue(
        Command(['xacro ', LaunchConfiguration('model')]),
        value_type=str,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'model',
            default_value=os.path.join(share, 'urdf', 'vehicle.urdf.xacro'),
            description='Xacro file of the robot description',
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='true',
            description='Start RViz with the vehicle configuration',
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', os.path.join(share, 'rviz', 'vehicle.rviz')],
            condition=IfCondition(LaunchConfiguration('rviz')),
        ),
    ])

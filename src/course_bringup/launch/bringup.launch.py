from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    GroupAction,
    LogInfo,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushROSNamespace


def recorder(context):
    namespace = LaunchConfiguration('namespace').perform(context).strip('/')
    topic = '/' + '/'.join(part for part in (namespace, 'sensor_pose') if part)

    return [
        LogInfo(
            msg=['Recording ', topic, ' to ', LaunchConfiguration('bag_dir')],
            condition=IfCondition(LaunchConfiguration('record')),
        ),
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '--storage', 'mcap',
                '--output', LaunchConfiguration('bag_dir'),
                '--topics', topic,
            ],
            output='screen',
            name='bag_record',
            condition=IfCondition(LaunchConfiguration('record')),
        ),
    ]


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    subscriber_reliability = LaunchConfiguration('subscriber_reliability')

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='robot_a',
            description='Namespace for patrol, pose_relay and sensor_listener',
        ),
        DeclareLaunchArgument(
            'record',
            default_value='false',
            description='Record sensor_pose with ros2 bag record (MCAP)',
        ),
        DeclareLaunchArgument(
            'bag_dir',
            default_value='bags/pr05',
            description='Output directory for ros2 bag record; must not exist',
        ),
        DeclareLaunchArgument(
            'subscriber_reliability',
            default_value='best_effort',
            choices=['reliable', 'best_effort'],
            description='Reliability policy of sensor_listener',
        ),
        LogInfo(msg=[
            'namespace=', namespace,
            ' record=', LaunchConfiguration('record'),
            ' subscriber_reliability=', subscriber_reliability,
        ]),
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen',
        ),
        GroupAction([
            PushROSNamespace(namespace),
            Node(
                package='patrol',
                executable='patrol',
                name='patrol',
                output='screen',
                remappings=[
                    ('turtle1/pose', '/turtle1/pose'),
                    ('turtle1/cmd_vel', '/turtle1/cmd_vel'),
                ],
            ),
            Node(
                package='course_bringup',
                executable='pose_relay',
                name='pose_relay',
                output='screen',
            ),
            Node(
                package='course_bringup',
                executable='sensor_listener',
                name='sensor_listener',
                output='screen',
                parameters=[{'reliability': subscriber_reliability}],
            ),
        ]),
        OpaqueFunction(function=recorder),
    ])

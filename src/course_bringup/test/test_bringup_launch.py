import os
import re
import unittest

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
import launch_testing
import launch_testing.actions
import launch_testing.asserts
import pytest


@pytest.mark.launch_test
def generate_test_description():
    launch_file = os.path.join(
        get_package_share_directory('course_bringup'),
        'launch',
        'bringup.launch.py',
    )

    return LaunchDescription([
        SetEnvironmentVariable('QT_QPA_PLATFORM', 'offscreen'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(launch_file),
            launch_arguments={
                'namespace': 'robot_a',
                'record': 'false',
                'subscriber_reliability': 'best_effort',
            }.items(),
        ),
        launch_testing.actions.ReadyToTest(),
    ])


class TestDelivery(unittest.TestCase):

    def test_listener_receives_best_effort_stream(self, proc_output):
        proc_output.assertWaitFor(
            'Listening on /robot_a/sensor_pose with best_effort',
            timeout=15,
        )
        proc_output.assertWaitFor(
            'Relaying /turtle1/pose to /robot_a/sensor_pose',
            timeout=15,
        )
        proc_output.assertWaitFor(
            re.compile(r'received [1-9]\d* messages in period'),
            timeout=15,
        )


@launch_testing.post_shutdown_test()
class TestShutdown(unittest.TestCase):

    def test_processes_exit_cleanly(self, proc_info):
        launch_testing.asserts.assertExitCodes(
            proc_info,
            allowable_exit_codes=[0, -2, -15],
        )

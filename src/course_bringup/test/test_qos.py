from course_bringup.pose_relay import sensor_qos
from course_bringup.sensor_listener import listener_qos
import pytest
from rclpy.qos import ReliabilityPolicy


def test_relay_publishes_best_effort():
    qos = sensor_qos()

    assert qos.reliability == ReliabilityPolicy.BEST_EFFORT
    assert qos.depth == 10


@pytest.mark.parametrize('name, policy', [
    ('reliable', ReliabilityPolicy.RELIABLE),
    ('best_effort', ReliabilityPolicy.BEST_EFFORT),
])
def test_listener_reliability(name, policy):
    assert listener_qos(name).reliability == policy


@pytest.mark.parametrize('name', ['', 'Reliable', 'system_default'])
def test_listener_rejects_unknown_reliability(name):
    with pytest.raises(ValueError):
        listener_qos(name)

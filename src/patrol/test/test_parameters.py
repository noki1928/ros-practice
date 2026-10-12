from types import SimpleNamespace
from unittest.mock import Mock

from patrol.patrol import Patrol, validate_parameters
import pytest


@pytest.mark.parametrize('values', [
    (0.5, 0.3, 10.0),
    (0.8, 0.6, 5.0),
    (0.0, -1.0, 1.0),
    (1.0, 1.0, 30.0),
])
def test_valid_parameters(values):
    assert validate_parameters(*values) == ''


@pytest.mark.parametrize('values', [
    (-0.1, 0.3, 10.0),
    (1.1, 0.3, 10.0),
    (0.5, -1.1, 10.0),
    (0.5, 1.1, 10.0),
    (0.5, 0.3, 0.0),
    (0.5, 0.3, -1.0),
    (0.5, 0.3, 31.0),
    (float('nan'), 0.3, 10.0),
    (0.5, float('nan'), 10.0),
    (0.5, 0.3, float('nan')),
    (0.5, 0.3, float('inf')),
    (0.5, 0.3, float('-inf')),
])
def test_invalid_parameters(values):
    assert validate_parameters(*values)


def make_state():
    return SimpleNamespace(
        linear_speed=0.5,
        turn_rate=0.3,
        publish_hz=10.0,
        timer=Mock(),
        destroy_timer=Mock(),
        create_timer=Mock(),
        tick=Mock(),
    )


def test_frequency_change_replaces_timer():
    state = make_state()
    old_timer = state.timer
    result = Patrol.on_parameters(state, [
        SimpleNamespace(name='publish_hz', value=5.0),
    ])

    assert result.successful
    assert state.publish_hz == 5.0
    old_timer.cancel.assert_called_once_with()
    state.destroy_timer.assert_called_once_with(old_timer)
    state.create_timer.assert_called_once_with(0.2, state.tick)
    assert state.timer is state.create_timer.return_value


@pytest.mark.parametrize('value', [0.0, -1.0, float('nan'), True, '5'])
def test_rejected_frequency_preserves_state(value):
    state = make_state()
    old_timer = state.timer
    result = Patrol.on_parameters(state, [
        SimpleNamespace(name='linear_speed', value=0.8),
        SimpleNamespace(name='publish_hz', value=value),
    ])

    assert not result.successful
    assert result.reason
    assert (state.linear_speed, state.turn_rate, state.publish_hz) == (
        0.5, 0.3, 10.0,
    )
    assert state.timer is old_timer
    old_timer.cancel.assert_not_called()
    state.destroy_timer.assert_not_called()
    state.create_timer.assert_not_called()

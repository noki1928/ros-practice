from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from course_description import model
import pytest

XACRO = Path(__file__).resolve().parents[1] / 'urdf' / 'vehicle.urdf.xacro'

WHEELBASE = 0.80
TRACK_WIDTH = 0.62
WHEEL_RADIUS = 0.12
SENSOR_XYZ = (0.28, 0.0, 0.38)

EXPECTED_PARENTS = {
    'camera_link': 'base_link',
    'lidar_link': 'base_link',
    'imu_link': 'base_link',
    'front_left_knuckle': 'base_link',
    'front_right_knuckle': 'base_link',
    'front_left_wheel': 'front_left_knuckle',
    'front_right_wheel': 'front_right_knuckle',
    'rear_left_wheel': 'base_link',
    'rear_right_wheel': 'base_link',
}


@pytest.fixture(scope='module')
def urdf():
    return model.expand(XACRO)


def test_tree_has_single_root_base_link(urdf):
    assert model.roots(urdf) == ['base_link']


def test_tree_is_connected_and_acyclic(urdf):
    for link in model.links(urdf):
        path = model.chain(urdf, link)
        top = path[0].parent if path else link
        assert top == 'base_link', link


def test_links_are_unique(urdf):
    names = model.links(urdf)
    assert len(names) == len(set(names))


@pytest.mark.parametrize('child, parent', EXPECTED_PARENTS.items())
def test_expected_parent(urdf, child, parent):
    assert model.joints(urdf)[child].parent == parent


@pytest.mark.parametrize('sensor', ['camera_link', 'lidar_link', 'imu_link'])
def test_sensor_pose_in_base_link(urdf, sensor):
    assert model.position(urdf, 'base_link', sensor) == pytest.approx(
        SENSOR_XYZ,
    )
    assert model.joints(urdf)[sensor].kind == 'fixed'


@pytest.mark.parametrize('wheel, x, y', [
    ('front_left_wheel', WHEELBASE / 2, TRACK_WIDTH / 2),
    ('front_right_wheel', WHEELBASE / 2, -TRACK_WIDTH / 2),
    ('rear_left_wheel', -WHEELBASE / 2, TRACK_WIDTH / 2),
    ('rear_right_wheel', -WHEELBASE / 2, -TRACK_WIDTH / 2),
])
def test_wheel_position(urdf, wheel, x, y):
    assert model.position(urdf, 'base_link', wheel) == pytest.approx(
        (x, y, 0.0),
    )
    joint = model.joints(urdf)[wheel]
    assert joint.kind == 'continuous'


def test_wheel_radius_in_meters(urdf):
    root = ET.fromstring(urdf)
    radii = {
        float(cylinder.get('radius'))
        for cylinder in root.iter('cylinder')
    }
    assert radii == {WHEEL_RADIUS}


def test_links_with_geometry_have_visual_and_collision(urdf):
    for link in ET.fromstring(urdf).iter('link'):
        if link.find('visual') is not None:
            assert link.find('collision') is not None, link.get('name')


def test_inertia_is_physical(urdf):
    for link in ET.fromstring(urdf).iter('link'):
        inertial = link.find('inertial')
        assert inertial is not None, link.get('name')
        mass = float(inertial.find('mass').get('value'))
        tensor = inertial.find('inertia')
        ixx, iyy, izz = (
            float(tensor.get(key)) for key in ('ixx', 'iyy', 'izz')
        )
        assert mass > 0.0
        assert min(ixx, iyy, izz) > 0.0
        assert ixx + iyy >= izz
        assert ixx + izz >= iyy
        assert iyy + izz >= ixx


def test_check_urdf_accepts_model(urdf, tmp_path):
    check_urdf = shutil.which('check_urdf')
    if check_urdf is None:
        pytest.skip('check_urdf is not installed')
    path = tmp_path / 'vehicle.urdf'
    path.write_text(urdf)
    result = subprocess.run(
        [check_urdf, str(path)], capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr

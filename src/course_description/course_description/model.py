from dataclasses import dataclass
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import xacro

DEFAULT_XACRO = (
    Path(__file__).resolve().parents[1] / 'urdf' / 'vehicle.urdf.xacro'
)

Vector = tuple[float, float, float]
Matrix = tuple[Vector, Vector, Vector]


@dataclass(frozen=True)
class Joint:
    name: str
    kind: str
    parent: str
    child: str
    xyz: Vector
    rpy: Vector


def expand(path: Path = DEFAULT_XACRO) -> str:
    return xacro.process_file(str(path)).toprettyxml(indent='  ')


def _vector(text: str | None) -> Vector:
    values = [float(value) for value in (text or '0 0 0').split()]
    return values[0], values[1], values[2]


def links(urdf: str) -> list[str]:
    return [link.get('name') for link in ET.fromstring(urdf).iter('link')]


def joints(urdf: str) -> dict[str, Joint]:
    """Return joints of the URDF keyed by child link."""
    result = {}
    for element in ET.fromstring(urdf).findall('joint'):
        origin = element.find('origin')
        joint = Joint(
            name=element.get('name'),
            kind=element.get('type'),
            parent=element.find('parent').get('link'),
            child=element.find('child').get('link'),
            xyz=_vector(None if origin is None else origin.get('xyz')),
            rpy=_vector(None if origin is None else origin.get('rpy')),
        )
        if joint.child in result:
            raise ValueError(f'link {joint.child} has two parent joints')
        result[joint.child] = joint
    return result


def roots(urdf: str) -> list[str]:
    children = joints(urdf)
    return [link for link in links(urdf) if link not in children]


def chain(urdf: str, child: str) -> list[Joint]:
    """Return joints from the root down to the child link."""
    by_child = joints(urdf)
    result = []
    seen = {child}
    while child in by_child:
        joint = by_child[child]
        if joint.parent in seen:
            raise ValueError(f'cycle through link {joint.parent}')
        seen.add(joint.parent)
        result.append(joint)
        child = joint.parent
    return list(reversed(result))


def _rotation(rpy: Vector) -> Matrix:
    roll, pitch, yaw = rpy
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return (
        (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
        (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
        (-sp, cp * sr, cp * cr),
    )


def _apply(matrix: Matrix, vector: Vector) -> Vector:
    x, y, z = (sum(row[i] * vector[i] for i in range(3)) for row in matrix)
    return x, y, z


def _multiply(left: Matrix, right: Matrix) -> Matrix:
    rows = []
    for row in left:
        x, y, z = (
            sum(row[k] * right[k][col] for k in range(3)) for col in range(3)
        )
        rows.append((x, y, z))
    return rows[0], rows[1], rows[2]


def position(urdf: str, frame: str, child: str) -> Vector:
    """Return the origin of child expressed in frame at zero joint state."""
    path = chain(urdf, child)
    parents = [joint.parent for joint in path]
    if frame not in parents and frame != child:
        raise ValueError(f'{frame} is not an ancestor of {child}')
    path = path[parents.index(frame):] if frame != child else []

    rotation: Matrix = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    translation: Vector = (0.0, 0.0, 0.0)
    for joint in path:
        dx, dy, dz = _apply(rotation, joint.xyz)
        translation = (
            translation[0] + dx, translation[1] + dy, translation[2] + dz,
        )
        rotation = _multiply(rotation, _rotation(joint.rpy))
    return translation

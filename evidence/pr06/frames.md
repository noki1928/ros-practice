# PR06 — кадры и владельцы преобразований

Модель: `src/course_description/urdf/vehicle.urdf.xacro`, размеры из
`models/course_ackermann/model.sdf` (course kit `v1-w07`). Единицы СИ, оси
REP-103 (x вперёд, y влево, z вверх). Корень дерева — `base_link`; `map` и
`odom` в этой работе не публикуются.

Единственный издатель всех преобразований модели — `robot_state_publisher`
(запускается `display.launch.py`). Fixed-соединения он публикует один раз в
`/tf_static` (RELIABLE, TRANSIENT_LOCAL), подвижные — в `/tf` по сообщениям
`/joint_states`. Издателя `joint_states` в обязательной части нет, поэтому
преобразования колёс и поворотных кулаков в `/tf` не появляются; второго
издателя ни для одного преобразования нет.

| Соединение | Тип | Родитель → потомок | Ожидаемое преобразование (xyz, м; rpy, рад) | Канал | Владелец |
|---|---|---|---|---|---|
| `camera_joint` | fixed | `base_link` → `camera_link` | `0.28 0 0.38`, `0 0 0` | `/tf_static` | `robot_state_publisher` |
| `lidar_joint` | fixed | `base_link` → `lidar_link` | `0.28 0 0.38`, `0 0 0` | `/tf_static` | `robot_state_publisher` |
| `imu_joint` | fixed | `base_link` → `imu_link` | `0.28 0 0.38`, `0 0 0` | `/tf_static` | `robot_state_publisher` |
| `front_left_steering_joint` | revolute, ось z, ±0.55 | `base_link` → `front_left_knuckle` | `0.40 0.31 0`, угол руля | `/tf` | `robot_state_publisher` по `joint_states` |
| `front_right_steering_joint` | revolute, ось z, ±0.55 | `base_link` → `front_right_knuckle` | `0.40 -0.31 0`, угол руля | `/tf` | `robot_state_publisher` по `joint_states` |
| `front_left_wheel_joint` | continuous, ось y | `front_left_knuckle` → `front_left_wheel` | `0 0 0`, угол колеса | `/tf` | `robot_state_publisher` по `joint_states` |
| `front_right_wheel_joint` | continuous, ось y | `front_right_knuckle` → `front_right_wheel` | `0 0 0`, угол колеса | `/tf` | `robot_state_publisher` по `joint_states` |
| `rear_left_wheel_joint` | continuous, ось y | `base_link` → `rear_left_wheel` | `-0.40 0.31 0`, угол колеса | `/tf` | `robot_state_publisher` по `joint_states` |
| `rear_right_wheel_joint` | continuous, ось y | `base_link` → `rear_right_wheel` | `-0.40 -0.31 0`, угол колеса | `/tf` | `robot_state_publisher` по `joint_states` |

Параметры Xacro: `wheelbase=0.80`, `track_width=0.62`, `wheel_radius=0.12`,
`wheel_width=0.07`, кузов `1.05 × 0.52 × 0.22` с центром на `z=0.12`. Колёса
стоят в `(±wheelbase/2, ±track_width/2, 0)`.

## Дефект: неверный родитель `lidar_link`

Коммит `2c8aaf1` (сломанная версия): `lidar_joint` с родителем `camera_link`
и тем же смещением `0.28 0 0.38`. `check_urdf` дерево принимает, но лидар
оказывается в `base_link` на `0.56 0 0.76` вместо `0.28 0 0.38`.
`view_frames` показывает цепочку `base_link → camera_link → lidar_link`.
Тесты `test_expected_parent[lidar_link-base_link]` и
`test_sensor_pose_in_base_link[lidar_link]` падают.

Коммит `149786d` (исправление): родитель снова `base_link`, тесты проходят,
`tf2_echo base_link lidar_link` даёт `0.28 0 0.38`.

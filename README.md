# ROS Practice

## PR03: Нода patrol — поза и команда

Пакет `src/patrol` подписывается на `/turtle1/pose`, сохраняет последнюю позу
и публикует `geometry_msgs/msg/Twist` каждые 0,1 с. Без позы публикуется
нулевая команда; после получения позы — `linear.x=0.5`, `angular.z=0.3`.
Для Lyrical тип позы `turtlesim_msgs/msg/Pose`; для Jazzy —
`turtlesim/msg/Pose`.

### Сборка и запуск

Из корня репозитория в терминале, где подключена базовая ROS:

```bash
colcon build --symlink-install
source install/setup.bash  # для Zsh: source install/setup.zsh
```

Запустите turtlesim в терминале A, в B — patrol с remap:

```bash
ros2 launch turtle_bringup sim.launch.py
```

```bash
ros2 run patrol patrol --ros-args -r cmd_vel:=/turtle1/cmd_vel
```

Одинаковый `ROS_DOMAIN_ID` должен быть задан во всех терминалах. Проверьте
граф и частоту в терминале C:

```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic info /turtle1/pose --verbose
ros2 topic info /turtle1/cmd_vel --verbose
ros2 topic hz /turtle1/cmd_vel
```

Ожидаемая частота — около 10 Hz. Для проверки дефекта остановите patrol и
запустите его без remap:

```bash
ros2 run patrol patrol
ros2 topic info /cmd_vel --verbose
ros2 topic info /turtle1/cmd_vel --verbose
ros2 topic hz /cmd_vel
```

Издатель окажется на `/cmd_vel`, где нет подписчика turtlesim. Исправление —
остановить процесс и запустить его с `-r cmd_vel:=/turtle1/cmd_vel`. Проверьте,
что на `/turtle1/cmd_vel` есть издатель patrol и подписчик turtlesim. Тип
сообщения Twist одинаков, но полные имена топиков должны совпадать для
доставки. После опыта остановите patrol через `Ctrl+C` и дождитесь остановки
черепахи.

### Тесты и отчёт

```bash
colcon test --packages-select patrol --event-handlers console_direct+
colcon test-result --verbose
python3 .course-kit/v1/tools/check_practice.py PR03 --submission .
```

Запускайте тесты только для `patrol`: у `turtle_bringup` нет тестов. CI
собирает оба ROS-пакета и запускает проверки patrol в закреплённом образе
ROS 2 Lyrical. Демонстрация CLI и измерения записаны в `evidence/pr03/demo.md`;
локальные результаты тестов — в `evidence/pr03/tests.txt`.

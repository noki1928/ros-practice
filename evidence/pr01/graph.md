# PR01: окружение и граф ROS 2

## Источник наблюдений

Отчёт составлен по сохранённым выводам терминалов:

- `~/Desktop/a.txt` - запуск `turtlesim_node` в домене 24 и сообщения о
  выполнении команд поворота;
- `~/Desktop/b.txt` - запуск `turtle_teleop_key` и смена доменов 24/25/24;
- `~/Desktop/c.txt` - команды наблюдения, граф, тип, поза, частота и опыт с
  разными доменами.

## Исправный граф: ROS_DOMAIN_ID=24

Команды наблюдения:

```bash
source ~/ros_gz_ws/activate.zsh
export ROS_DOMAIN_ID=24
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
ros2 topic type /turtle1/pose
POSE_TYPE=$(ros2 topic type /turtle1/pose)
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose
```

Ноды:

| Нода | Роль |
| --- | --- |
| `/turtlesim` | симулятор; принимает движение и публикует состояние черепахи |
| `/teleop_turtle` | считывает клавиатуру и отправляет команды управления |

Топики и типы, зафиксированные `ros2 topic list -t`:

| Топик | Тип | Назначение |
| --- | --- | --- |
| `/turtle1/cmd_vel` | `geometry_msgs/msg/Twist` | команда линейной и угловой скорости от teleop к симулятору |
| `/turtle1/color_sensor` | `turtlesim_msgs/msg/Color` | цвет под черепахой |
| `/turtle1/pose` | `turtlesim_msgs/msg/Pose` | положение, ориентация и скорость черепахи |
| `/parameter_events` | `rcl_interfaces/msg/ParameterEvent` | события параметров нод |
| `/rosout` | `rcl_interfaces/msg/Log` | журнал ROS |

`ros2 node info /turtlesim` подтвердил, что `/turtlesim` подписан на
`/turtle1/cmd_vel` и публикует `/turtle1/pose` и `/turtle1/color_sensor`.

Полученная поза:

```yaml
x: 5.544444561004639
y: 5.544444561004639
theta: 0.7903705835342407
linear_velocity: 0.0
angular_velocity: 0.0
```

Измерение `/turtle1/pose` работало около 90 секунд: последнее окно содержало
5632 сообщения. Итоговая частота - `62.500 Hz`; интервал сообщений был
`0.014-0.018 s`. Это соответствует ожидаемой частоте turtlesim около 60-62.5
Hz. Управление с клавиатуры подтверждено логом симулятора: в нём есть сообщения
`Rotation goal completed successfully`.

## Разрыв домена: ROS_DOMAIN_ID=25

Симулятор оставался запущенным в домене 24. `turtle_teleop_key` был остановлен,
а затем запущен в домене 25. В терминале наблюдения также установлен домен 25:

```bash
export ROS_DOMAIN_ID=25
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?"
```

Наблюдение: обнаружена только `/teleop_turtle`; `/turtlesim` отсутствует.
`/turtle1/pose` за пять секунд не пришёл, код завершения - `124`.

## Восстановление: ROS_DOMAIN_ID=24

`turtle_teleop_key` перезапущен в домене 24, затем домен 24 установлен в
терминале наблюдения. Теми же командами обнаружены `/teleop_turtle` и
`/turtlesim`; проверка позы завершилась с кодом `0`.

Причина: участники DDS обнаруживаются только внутри одного `ROS_DOMAIN_ID`.
Изменение переменной окружения влияет на новую ноду, но не перенастраивает уже
запущенный процесс. Поэтому для восстановления требовался перезапуск teleop в
домене 24; симулятор и установка ROS не менялись.

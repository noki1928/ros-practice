# ROS Practice

## PR02: Пакет и запуск turtlesim

Ветка `pr2`, пакет `src/turtle_bringup`, результаты `evidence/pr02/`.
Локально проверено с ROS 2 Lyrical; CI собирает пакет в закреплённом Jazzy.

### Подготовка и сборка

В новом терминале Zsh на этой машине подключите базовую ROS (без overlay
этого репозитория перед сборкой):

```zsh
export PATH="$HOME/ros2_lyrical/.pixi/envs/default/bin:$PATH"
export LD_LIBRARY_PATH="$HOME/ros2_lyrical/.pixi/envs/default/lib:${LD_LIBRARY_PATH:-}"
source ~/ros2_lyrical/install/setup.zsh
cd ~/progs/ros-practice
set -o pipefail
colcon build --symlink-install --packages-select turtle_bringup
```

На Ubuntu с пакетной установкой вместо этой активации используйте
`source /opt/ros/jazzy/setup.bash` (или Lyrical) в Bash.

### Запуск и проверка

В терминале A подключите базовую ROS, затем overlay:

```zsh
source install/setup.zsh
export ROS_DOMAIN_ID=24
ros2 pkg prefix turtle_bringup
ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
ros2 launch turtle_bringup sim.launch.py
```

В Bash используйте `install/setup.bash`. В B/C активируйте ту же среду и
домен. Перед опытом остановите старые turtlesim и teleop.

```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose --once
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 1.0}, angular: {z: 0.5}}'
ros2 topic echo /turtle1/pose --once
```

Для сбоя в B публикуйте тот же Twist в `/cmd_vel`:

```bash
ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /cmd_vel \
  geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'
```

В C сравните `ros2 topic info /cmd_vel --verbose` и
`ros2 topic info /turtle1/cmd_vel --verbose`. Остановите издателя `Ctrl+C`,
измените только `/cmd_vel` на `/turtle1/cmd_vel`, повторите публикацию и
проверку конечных точек. Остановите издателя, дождитесь остановки черепахи.
`Ctrl+C` в A должен завершить launch и запущенный им turtlesim.

Исходники на диске не запускают ноду: `colcon build` устанавливает пакет,
`source` добавляет его в поиск, а `ros2 launch` запускает процесс.
Одинакового типа недостаточно для доставки: должно совпадать имя топика.

### Проверка сдачи

```bash
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
python3 .course-kit/v1/tools/check_practice.py PR02 --submission .
```

Используется course kit `v1-w05`, SHA-256
`bca214e3de6f90f9513049dfa0f36fee65ad834da502dc3f3f8fb443517b5197`.
CI проверяет сборку, установку launch и комплектность evidence, без GUI.

## PR01: Environment and ROS 2 Graph

This practice uses ROS 2 Lyrical, `turtlesim`, and DDS domains 24 and 25.
ROS 2 has no central `roscore`: nodes discover each other automatically when
they use the same `ROS_DOMAIN_ID`.

### Prerequisites

Open three terminals. In each terminal, activate the ROS environment before
using `ros2`:

```bash
source ~/ros_gz_ws/activate.zsh
```

This command makes ROS 2, `turtlesim`, and the local overlay packages
available in the current terminal. It must be repeated for every newly opened
terminal.

### Start the simulator

In Terminal A, start `turtlesim` in domain 24:

```bash
source ~/ros_gz_ws/activate.zsh
export ROS_DOMAIN_ID=24
ros2 run turtlesim turtlesim_node
```

A simulator window opens. The process creates the `/turtlesim` node, subscribes
to `/turtle1/cmd_vel`, and publishes `/turtle1/pose`.

### Start keyboard control

In Terminal B, start the keyboard controller in the same domain:

```bash
source ~/ros_gz_ws/activate.zsh
export ROS_DOMAIN_ID=24
ros2 run turtlesim turtle_teleop_key
```

Keep focus in Terminal B and press the arrow keys to move the turtle. The
controller publishes `geometry_msgs/msg/Twist` messages to `/turtle1/cmd_vel`.
Press `q` to quit the controller, or `Ctrl+C` to stop it.

### Inspect the ROS graph

In Terminal C, inspect the nodes and topics in domain 24:

```bash
source ~/ros_gz_ws/activate.zsh
export ROS_DOMAIN_ID=24
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 node info /turtlesim
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose
```

Expected nodes are `/turtlesim` and `/teleop_turtle`. The last command measures
the pose publication rate; stop it with `Ctrl+C` after collecting enough
samples.

### Stop ROS nodes

Press `Ctrl+C` in each terminal where `turtlesim_node`, `turtle_teleop_key`, or
`ros2 topic hz` is running. Stopping a node does not affect commands in the
other terminals.

### Reproduce a domain split

Leave the simulator running in domain 24. In Terminal B, press `Ctrl+C` to stop
teleop, then restart it in a different domain:

```bash
export ROS_DOMAIN_ID=25
ros2 run turtlesim turtle_teleop_key
```

The controller cannot discover `/turtlesim`, so the turtle does not move. In
Terminal C, this confirms that only teleop is visible:

```bash
export ROS_DOMAIN_ID=25
ros2 node list --no-daemon --spin-time 2
timeout 5s ros2 topic echo /turtle1/pose turtlesim_msgs/msg/Pose --once
```

The topic command should time out because the simulator publishes its pose only
in domain 24.

### Restore communication

Press `Ctrl+C` to stop teleop in Terminal B and restart it in domain 24. Return
Terminal C to the same domain before inspecting the graph again:

```bash
# Terminal B
export ROS_DOMAIN_ID=24
ros2 run turtlesim turtle_teleop_key
```

```bash
# Terminal C
export ROS_DOMAIN_ID=24
ros2 node list --no-daemon --spin-time 2
ros2 topic echo /turtle1/pose --once
```

Both `/turtlesim` and `/teleop_turtle` should be visible, and pose messages
should arrive immediately.

### Common problems

- `ros2: command not found`: run `source ~/ros_gz_ws/activate.zsh` in that terminal.
- Turtle does not move: check that both Terminal A and Terminal B use the same
  `ROS_DOMAIN_ID`, then restart the teleop process.
- `/turtlesim` is missing from `ros2 node list`: verify that the simulator is
  still running and that Terminal C is in its domain.
- A changed `ROS_DOMAIN_ID` affects only processes started afterwards. Stop and
  restart a node after changing the variable.

### Validate evidence

```bash
python3 -m json.tool evidence/pr01/environment.json > /dev/null
python3 .course-kit/v1/tools/check_practice.py PR01 --submission .
```

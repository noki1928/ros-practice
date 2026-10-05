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

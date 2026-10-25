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

## PR04: Параметризуем движение

Параметры `patrol`: `linear_speed=0.5` (0–1 м/с), `turn_rate=0.3`
(−1–1 рад/с), `publish_hz=10.0` (1–30 Гц). Все значения должны быть конечными.
Нода публикует непосредственно в `/turtle1/cmd_vel`; remap из ПР03 не нужен.
При допустимой смене частоты старый таймер останавливается и уничтожается,
а новый получает период `1/publish_hz`. Недопустимый ввод не меняет состояние.

После активации ROS и сборки запустите turtlesim и `ros2 run patrol patrol`
в отдельных терминалах с одинаковым `ROS_DOMAIN_ID=24`. Проверки:

```bash
ros2 param get /patrol publish_hz
ros2 param set /patrol linear_speed 0.8
ros2 param set /patrol turn_rate 0.6
ros2 param set /patrol publish_hz 5.0
ros2 topic hz /turtle1/cmd_vel
ros2 param set /patrol publish_hz 0.0
ros2 param get /patrol publish_hz
ros2 topic hz /turtle1/cmd_vel
```

Локальные тесты запускайте из каталога пакета, чтобы линтер не проверял
старые копии исходников в `build/` (ROS должна быть активирована):

```bash
cd src/patrol
PYTHONPATH="$PWD:${PYTHONPATH:-}" python3 -m pytest test -q
```

CI собирает оба пакета в закреплённой ROS 2 Lyrical, проверяет синтаксис,
запускает тесты `patrol`, сохраняет XML-результаты и проверяет evidence PR04.
Команды и наблюдения: `evidence/pr04/parameters.md`; результаты тестов:
`evidence/pr04/tests.txt`; оставшиеся пункты: `evidence/pr04/checklist.md`.

Course checker требует сначала коммит реализации (включая тесты, CI,
`package.xml` и README), затем отдельный коммит только `evidence/pr04/`
и `AI_USAGE.md`. В `report.json` укажите полный SHA первого коммита.

## PR05: Launch, QoS и повтор записи

Пакет `src/course_bringup` поднимает систему одной командой:
`turtlesim` в корневом пространстве имён, а `patrol`, `pose_relay` и
`sensor_listener` — в `/<namespace>` (по умолчанию `/robot_a`).

- `patrol` теперь использует относительные имена `turtle1/pose` и
  `turtle1/cmd_vel`; без namespace (`ros2 run patrol patrol`) они совпадают с
  прежними абсолютными. В launch они переназначены на `/turtle1/pose` и
  `/turtle1/cmd_vel`.
- `pose_relay` читает `/turtle1/pose` и публикует `sensor_pose`
  (`/robot_a/sensor_pose`) с `best_effort`.
- `sensor_listener` подписан на `sensor_pose` с reliability из аргумента
  `subscriber_reliability`, раз в 2 с печатает число полученных сообщений и
  предупреждает о несовместимом QoS.
- Аргументы launch: `namespace`, `record` (`true` запускает
  `ros2 bag record` в MCAP через `IfCondition`), `bag_dir` (каталог не должен
  существовать), `subscriber_reliability` (`reliable` | `best_effort`).

```bash
ros2 launch course_bringup bringup.launch.py subscriber_reliability:=reliable
ros2 topic info -v /robot_a/sensor_pose
ros2 launch course_bringup bringup.launch.py record:=true bag_dir:=bags/pr05-after
ros2 bag info bags/pr05-after
ros2 run course_bringup sensor_listener --ros-args -r __ns:=/robot_a -p reliability:=reliable
ros2 bag play bags/pr05-after \
  --qos-profile-overrides-path src/course_bringup/config/qos-overrides.yaml
```

Без overrides `ros2 bag play` повторяет записанный `best_effort`, и
`reliable`-подписчик ничего не получает; `config/qos-overrides.yaml`
переводит повтор `/robot_a/sensor_pose` в `reliable`.

Ноды игнорируют повторный SIGINT во время очистки: при Ctrl+C сигнал приходит
и от терминала, и от `ros2 launch`. Launch-тест `test_bringup_launch.py`
поднимает систему без GUI (`QT_QPA_PLATFORM=offscreen`), ждёт доставки
`best_effort` и проверяет коды завершения процессов.

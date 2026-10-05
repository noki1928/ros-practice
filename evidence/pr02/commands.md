# PR02: выполненные команды и наблюдения

Опыт выполнен агентом OpenCode 2026-10-05 в локальной ROS 2 Lyrical,
Zsh, `ROS_DOMAIN_ID=24`, с графическим DISPLAY=:0. Teleop и старые
экземпляры turtlesim перед опытом отсутствовали. Проверка через CLI
не заменяет самостоятельную демонстрацию студентом окна симулятора.

## Linux, среда и сборка

```zsh
git switch pr2
pwd
ls -a
export PATH=/home/pavel/ros2_lyrical/.pixi/envs/default/bin:$PATH
export LD_LIBRARY_PATH=/home/pavel/ros2_lyrical/.pixi/envs/default/lib:${LD_LIBRARY_PATH:-}
source /home/pavel/ros2_lyrical/install/setup.zsh
printenv ROS_DISTRO
ros2 pkg prefix turtlesim
mkdir -p evidence/pr02
set -o pipefail
colcon build --symlink-install --packages-select turtle_bringup 2>&1 | tee evidence/pr02/build-empty.txt
source install/setup.zsh
ros2 pkg prefix turtle_bringup
```

Вывод: `lyrical`, базовый turtlesim в `/home/pavel/ros2_lyrical/install`,
новый пакет в `/home/pavel/progs/ros-practice/install/turtle_bringup`.
Первый лог получен до создания launch-файла. Пустой пакет найден, но
сборка и подключение среды не создают работающих нод.

После добавления launch в новом процессе с базовой ROS:

```zsh
colcon build --symlink-install --packages-select turtle_bringup 2>&1 | tee evidence/pr02/build.txt
source install/setup.zsh
ros2 pkg prefix turtle_bringup
ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
python3 -m py_compile src/turtle_bringup/launch/sim.launch.py
```

Обе сборки успешны; установлен `sim.launch.py`. `data_files` сохраняет
маркер ament, package.xml и устанавливает launch, а не только Python-модуль.

## Запуск и остановка

```zsh
export ROS_DOMAIN_ID=24
timeout --signal=INT --kill-after=5s 10s ros2 launch turtle_bringup sim.launch.py >evidence/pr02/launch.txt 2>&1 &
launch_pid=$!
sleep 3
ros2 node list --no-daemon --spin-time 2 >evidence/pr02/nodes-running.txt
wait $launch_pid
ros2 node list --no-daemon --spin-time 2 >evidence/pr02/nodes-stopped.txt
```

Использован ограниченный запуск: timeout отправляет SIGINT, тот же сигнал,
что `Ctrl+C`. Его статус 124 ожидаем. Во время запуска виден `/turtlesim`,
после остановки список пуст. В [launch.txt](launch.txt) есть
`user interrupted with ctrl-c (SIGINT)` и `process has finished cleanly`.
Первоначальная попытка послать SIGINT напрямую фоновому процессу Zsh
не завершила его; успешная повторная проверка выше использует timeout.

## Доставка одной команды

Повторный launch ограничен 65 секундами теми же параметрами timeout;
лог — [experiment-launch.txt](experiment-launch.txt). Последовательно:

```bash
ros2 interface show geometry_msgs/msg/Twist
ros2 topic type /turtle1/pose
ros2 topic echo /turtle1/pose --once
ros2 topic pub --once /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}'
sleep 2
ros2 topic echo /turtle1/pose --once
```

Ожидание: движение вперёд с поворотом против часовой стрелки;
начальный theta=0 направлен вдоль положительной x. Результаты:

| Этап | x | y | theta | Скорости (linear/angular) |
| --- | ---: | ---: | ---: | --- |
| Начало | 5.544445 | 5.544445 | 0 | 0 / 0 |
| После одной команды | 6.509309 | 5.796991 | 0.504000 | 0 / 0 |
| Ошибочный топик | 6.509309 | 5.796991 | 0.504000 | 0 / 0 |
| Исправленный топик, во время движения | 7.316675 | 8.455916 | 2.040000 | 1 / 0.5 |
| После остановки издателя | 5.000696 | 5.617521 | -0.275185 | 0 / 0 |

Полные исходные сообщения: `pose-before.txt`, `pose-after-once.txt`,
`pose-broken.txt`, `pose-fixed.txt`, `pose-stopped.txt`.
Без новых команд черепаха останавливается; одна публикация не задаёт
бесконечное движение.

## Сбой и исправление только имени

```zsh
timeout --signal=INT --kill-after=3s 12s ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}' >evidence/pr02/pub-broken.txt 2>&1 &
pub_pid=$!
sleep 2
ros2 topic info /cmd_vel --verbose
ros2 topic info /turtle1/cmd_vel --verbose
ros2 topic echo /turtle1/pose --once
wait $pub_pid
timeout --signal=INT --kill-after=3s 12s ros2 topic pub --rate 1 --wait-matching-subscriptions 0 /turtle1/cmd_vel geometry_msgs/msg/Twist '{linear: {x: 1.0}, angular: {z: 0.5}}' >evidence/pr02/pub-fixed.txt 2>&1 &
pub_pid=$!
sleep 2
ros2 topic info /turtle1/cmd_vel --verbose
ros2 topic echo /turtle1/pose --once
wait $pub_pid
sleep 2
ros2 topic echo /turtle1/pose --once
```

| Проверка | Издателей | Подписчиков | Конечные точки |
| --- | ---: | ---: | --- |
| `/cmd_vel` при сбое | 1 | 0 | `_ros2cli_11299` |
| `/turtle1/cmd_vel` при сбое | 0 | 1 | `turtlesim` |
| `/turtle1/cmd_vel` после исправления | 1 | 1 | `_ros2cli_11420`, `turtlesim` |

Полные выводы — `topic-broken.txt`, `topic-target-before.txt`,
`topic-fixed.txt`. В обоих случаях тип `geometry_msgs/msg/Twist`, домен,
скорость и частота не менялись. Discovery видит отдельные конечные точки,
но сообщения `/cmd_vel` не доставляются подписчику `/turtle1/cmd_vel`.
После изменения только полного имени появился общий топик и движение.
`--wait-matching-subscriptions 0` позволяет наблюдать работающего издателя
без подписчика; `--once` без этой настройки ждал бы подписчика.

Каталоги build/install/log исключены из Git, исходники и evidence сохранены.
Логи сборки записаны через `tee`; `pipefail` не скрывает ошибку colcon.
Команда `grep 'finished cleanly' evidence/pr02/launch.txt` подтвердила
чистое завершение процесса turtlesim. `pwd` вернул корень репозитория,
`ls -a` показал скрытые `.git`, `.github`, `.course-kit`.

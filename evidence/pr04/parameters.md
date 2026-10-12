# PR04 — параметры и воспроизведение дефекта

## Источник доказательств

Ниже приведены команды и выводы терминала, предоставленные студентом в чате.
Агент отдельно запустил синтаксическую проверку и открытые тесты; ROS-опыт
с черепахой выполнил студент. Результат облачного CI проверяется после push.

## Исправная версия: изменение параметров

```text
$ export ROS_DOMAIN_ID=24
$ ros2 param get /patrol publish_hz
Double value is: 10.0
$ ros2 param set /patrol linear_speed 0.8
Set parameter successful
$ ros2 param set /patrol turn_rate 0.6
Set parameter successful
$ ros2 param set /patrol publish_hz 5.0
Set parameter successful
$ ros2 param set /patrol linear_speed 1.0
Set parameter successful
$ ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz must be between 1 and 30
$ ros2 param get /patrol publish_hz
Double value is: 5.0
```

Измерение после отказа (выдержки из предоставленного вывода):

```text
$ ros2 topic hz /turtle1/cmd_vel
average rate: 5.001
    min: 0.200s max: 0.200s std dev: 0.00014s window: 4
average rate: 5.000
    min: 0.200s max: 0.200s std dev: 0.00020s window: 9
average rate: 5.000
    min: 0.199s max: 0.201s std dev: 0.00024s window: 49
average rate: 5.000
    min: 0.199s max: 0.201s std dev: 0.00024s window: 59
```

Поток стабилен около 5 Гц, период около 0,2 с. Параметр и поток сохранились
после отказа. Изменения скоростей приняты; отдельного вывода содержимого
Twist студент пока не предоставил. Настраиваемые скорости проверяются unit-тестом.

## Сломать: отключить проверку частоты

История коммитов:

- `d5832b9bf23762c4dd211e5d36ea228fc9c06481` — первоначальная валидация;
- `cccd7bd3cd13f92620a9a04a7a72f5e00aa1f700` — проверка диапазона частоты
  закомментирована;
- `403dce0d2e1b584489c83dc04a4de80d67242429` — проверка восстановлена.

По сообщению студента, передача нулевой частоты в дефектной версии привела
к остановке черепахи и следующему завершению процесса (выдержка traceback):

```text
  File "/home/pavel/progs/ros-practice/build/patrol/patrol/patrol.py", line 125, in on_parameters
    new_period = 1.0 / candidate['publish_hz']
                 ~~~~^~~~~~~~~~~~~~~~~~~~~~~~~
ZeroDivisionError: float division by zero
[ros2run]: Process exited with failure 1
```

Причина: без проверки диапазона ноль попадает в вычисление периода таймера.
Исключение выходит из callback, завершает spin и процесс ноды.

## Доказать: восстановить проверку и повторить запрос

После восстановления проверки студент предоставил:

```text
$ ros2 param get /patrol publish_hz
Double value is: 10.0
$ ros2 param set /patrol publish_hz 0.0
Setting parameter failed: publish_hz must be between 1 and 30
$ ros2 param get /patrol publish_hz
Double value is: 10.0
$ ros2 topic hz /turtle1/cmd_vel
average rate: 10.000
    min: 0.100s max: 0.100s std dev: 0.00021s window: 9
average rate: 10.001
    min: 0.100s max: 0.101s std dev: 0.00025s window: 29
average rate: 10.000
    min: 0.099s max: 0.101s std dev: 0.00024s window: 99
average rate: 10.000
    min: 0.099s max: 0.101s std dev: 0.00025s window: 119
```

Повторный запрос отклонён, параметр остался равным 10.0. После отказа
поток сохраняется около 10 Гц, период около 0,1 с, окно достигает 119 сообщений.
Прежнее измерение 5 Гц относится к первому исправному опыту.
Локальный тест callback также подтверждает, что отклонённое значение
не отменяет и не пересоздаёт таймер и не меняет активные скорости.

## Сервис и action

Запрос сервиса `/clear` очищает рисунок и возвращает ответ на единичный вызов.
Цель action `/turtle1/rotate_absolute` задаёт длительный поворот, для которого
доступны feedback, результат и отмена.

Фактические выводы, предоставленные студентом:

```text
$ ros2 service call /clear std_srvs/srv/Empty '{}'
waiting for service to become available...
requester: making request: std_srvs.srv.Empty_Request()

response:
std_srvs.srv.Empty_Response()

$ ros2 action list -t
/turtle1/rotate_absolute [turtlesim_msgs/action/RotateAbsolute]
```

Студент подтвердил, что рисунок очистился. Action найден; отправка цели
не выполнялась и не заявляется как выполненная проверка.

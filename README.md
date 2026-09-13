# ROS Practice

## PR01: Environment and ROS 2 Graph

The practice uses ROS 2 Lyrical, `turtlesim`, and the allocated domains 24 and
25. Run each command from a terminal where the ROS overlay has been activated.

### Run the working graph

Terminal A starts the simulator in domain 24:

```bash
source ~/ros_gz_ws/activate.zsh
export ROS_DOMAIN_ID=24
ros2 run turtlesim turtlesim_node
```

Terminal B starts keyboard control in the same domain. Keep focus in this
terminal and use the arrow keys to move the turtle.

```bash
source ~/ros_gz_ws/activate.zsh
export ROS_DOMAIN_ID=24
ros2 run turtlesim turtle_teleop_key
```

Terminal C inspects the graph:

```bash
source ~/ros_gz_ws/activate.zsh
export ROS_DOMAIN_ID=24
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t
ros2 topic echo /turtle1/pose --once
ros2 topic hz /turtle1/pose
```

### Reproduce and fix the domain split

Leave the simulator in domain 24. Restart `turtle_teleop_key` with
`ROS_DOMAIN_ID=25`; it cannot discover `/turtlesim` or communicate with it.
The pose check in domain 25 times out. Restart the teleop node and the observer
with `ROS_DOMAIN_ID=24` to restore discovery and delivery of `/turtle1/pose`.

### Validate evidence

```bash
python3 -m json.tool evidence/pr01/environment.json > /dev/null
python3 .course-kit/v1/tools/check_practice.py PR01 --submission .
```

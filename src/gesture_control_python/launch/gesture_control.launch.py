import launch
import launch_ros

def generate_launch_description():
    """Launch the gesture control nodes."""

    action_node_turtlesim_node = launch_ros.actions.Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim_node',
        output='screen'
    )   

    action_node_service_turtle_control = launch_ros.actions.Node(
        package='gesture_control_python',
        executable='service_turtle_control',
        name='service_turtle_control',
        output='screen'
    )

    action_node_client_turtle_control_gesture = launch_ros.actions.Node(
        package='gesture_control_python',
        executable='client_turtle_control_gesture',
        name='client_turtle_control_gesture',
        output='screen'
    )

    return launch.LaunchDescription([
        action_node_turtlesim_node,
        action_node_service_turtle_control,
        action_node_client_turtle_control_gesture
    ])
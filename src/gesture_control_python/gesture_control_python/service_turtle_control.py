import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from ges_cl_interface.srv import TurtleCmd

class TurtleControlServer(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        
        # Create a service server
        self.srv = self.create_service(TurtleCmd, 'turtle_cmd', self.turtle_cmd_callback)
        self.get_logger().info('Turtle Control Service is ready.')

        # create a topic publisher to control the turtle and a subscriber to receive the turtle's pose
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        self.subscriber = self.create_subscription(
            Pose, 'turtle1/pose', self.on_pose_received, 10)

    def turtle_cmd_callback(self, request, response) -> TurtleCmd.Response:
        # Handle the service request here
        twist = Twist()
        cmd = request.direction.lower() # Convert to lowercase for case-insensitive comparison
        if cmd == 'w':
            twist.linear.x = 1.0
        elif cmd == 's':
            twist.linear.x = -1.0
        elif cmd == 'a':
            twist.angular.z = 1.0
        elif cmd == 'd':
            twist.angular.z = -1.0
        else:
            self.get_logger().warn(f"Unknown command: {request.direction}")
            response.result = TurtleCmd.Response.FAIL
            return response

        self.publisher_.publish(twist)
        self.get_logger().info(f"Executed command: {request.direction}")
        response.result = TurtleCmd.Response.SUCCESS
        return response
    
    def on_pose_received(self, msg):
        self.get_logger().info(f"Received pose: x={msg.x}, y={msg.y}, theta={msg.theta}")
    
def main():
    rclpy.init()
    node = TurtleControlServer('turtle_control_server_python')
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
import rclpy
from rclpy.node import Node
import sys
from ges_cl_interface.srv import TurtleCmd

try:
    import readchar
except ImportError:
    print("please install readchar: pip install readchar")
    sys.exit(1)

class GestureControlClient(Node):
    def __init__ (self):
        super().__init__('gesture_control_client_python')

        #
        self.client = self.create_client(TurtleCmd, 'turtle_cmd')
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        
    def send_command(self, direction):
        # create a request object and set the direction
        request = TurtleCmd.Request()
        request.direction = direction

        # send async request
        future = self.client.call_async(request)
        future.add_done_callback(self.handle_response)
    
    def handle_response(self, future):
        try:
            response = future.result()
            # check the response and log the result
            if response.result == TurtleCmd.Response.SUCCESS:
                self.get_logger().info('Command executed successfully.')
            else:
                self.get_logger().warn('Command execution failed.')
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')
    
def main(args=None):
    rclpy.init(args=args)
    node = GestureControlClient()

    key_map = {
        'w': 'w',
        's': 's',
        'a': 'a',
        'd': 'd',
        ' ': 'stop'
    }

    try:
        while rclpy.ok(): # Loop until ROS is shutdown
            key = readchar.readkey().lower() # Read a key and convert to lowercase
            if key in key_map:
                node.get_logger().info(f'Sending command: {key_map[key]}')
                node.send_command(key_map[key])
            elif key == '\x03' or key == 'q':  # Ctrl-C or 'q' to exit
                node.get_logger().info('Exiting...')    
                break

            rclpy.spin_once(node,timeout_sec=0.1) # Process ROS events, with a timeout to allow for keyboard input
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt received, exiting...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
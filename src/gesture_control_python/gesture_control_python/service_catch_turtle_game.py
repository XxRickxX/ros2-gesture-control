import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from turtlesim.srv import Spawn, Kill 
from geometry_msgs.msg import Twist
from ges_cl_interface.srv import TurtleCmd
import random
import math
from rcl_interfaces.msg import SetParametersResult, ParameterType, ParameterValue, Parameter
from rcl_interfaces.srv import SetParameters
from std_srvs.srv import Empty
import time

class TurtleGameServer(Node):
    def __init__(self, node_name):
        super().__init__(node_name)

        self.clear_client = self.create_client(Empty, 'clear')

        # parameter settings
        self.last_color_time = time.time()
        self.param_client = self.create_client(SetParameters, '/turtlesim_node/set_parameters')

        # set default speed multiplier and prepare for dynamic updates
        self.speed_multiplier = 1.0 # default value, will be updated by parameter callback
        
        # 1. basic control：bind the 'turtle_cmd' service
        self.srv = self.create_service(TurtleCmd, 'turtle_cmd', self.turtle_cmd_callback)
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        
        # 2. game management：create Turtlesim Client Spawn and Kill 
        self.spawn_client = self.create_client(Spawn, 'spawn')
        self.kill_client = self.create_client(Kill, 'kill')
        
        # 3. coordinate tracking：订阅主乌龟和目标乌龟的位置
        self.turtle1_pose = Pose() # 主乌龟位置
        self.target_pose = Pose()  # 目标乌龟位置
        self.target_name = "prey"   # 给目标乌龟起个名
        
        # subscribe to turtle1 (main turtle) pose
        self.create_subscription(Pose, 'turtle1/pose', self.on_pose_received, 10)
        # subscribe to target turtle (prey) pose
        self.create_subscription(Pose, f'{self.target_name}/pose', self.on_target_pose_received, 10)

        # 4. initialize the game：create the first target turtle
        self.spawn_new_target()
        
        # 5. collision detection timer：calculate distance every 0.1 seconds (10Hz)
        self.create_timer(0.1, self.collision_detection_loop)
        
        self.get_logger().info('game client is ready！interface ：TurtleCmd')
    
    def change_turtle_color(self):
        if not self.param_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('waiting turtlesim set_parameters service...') 
            return
        
        req = SetParameters.Request()

        # change background color r, g, b to a random color
        color_names = ['background_r', 'background_g', 'background_b']
        
        for color in color_names:
            param_value = ParameterValue()
            param_value.type = ParameterType.PARAMETER_INTEGER
            param_value.integer_value = random.randint(0, 255)

            # create a Parameter object and append to the request
            param = Parameter()
            param.name = color
            param.value = param_value
            req.parameters.append(param)

        # log the new color value
        self.param_client.call_async(req)
        self.get_logger().info(f"Sending Color Change Request: RGB({req.parameters[0].value.integer_value}, {req.parameters[1].value.integer_value}, {req.parameters[2].value.integer_value})")

    def spawn_new_target(self):
        """async /spawn """
        if not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('waiting spawn service...')
            return
            
        req = Spawn.Request()
        req.x = random.uniform(1.0, 11.0)
        req.y = random.uniform(1.0, 11.0)
        req.theta = random.uniform(0.0, 6.28)
        req.name = self.target_name
        self.spawn_client.call_async(req)
        self.get_logger().info(f"新乌龟已刷新：x={req.x:.2f}")

    def catch_process(self):
        """async kill + spawn + clear"""
        self.get_logger().info("抓到了！立刻清屏并重置...")

        # 1. 立即清屏（视觉反馈最快）
        self.clear_client.call_async(Empty.Request())
        
        # 1. kill the old target turtle
        kill_req = Kill.Request()
        kill_req.name = self.target_name
        
        # using callback: only spawn a new target turtle after Kill succeeds
        future = self.kill_client.call_async(kill_req)
        future.add_done_callback(self.spawn_after_kill_callback)

    def spawn_after_kill_callback(self, future):
        try:
            response = future.result()
            # Kill succeeded, now spawn a new target turtle
            self.spawn_new_target()

        except Exception as e:
            self.get_logger().error(f"Kill 失败: {e}")

    def collision_detection_loop(self):
        """增加安全锁：位置全为 0 时不判断（防止初始状态误判）"""
        if self.target_pose.x == 0.0 and self.target_pose.y == 0.0:
            return

        distance = math.sqrt(
            (self.turtle1_pose.x - self.target_pose.x)**2 + 
            (self.turtle1_pose.y - self.target_pose.y)**2
        )
        
        # catch condition: distance less than 0.9 (tune as needed)
        if distance < 0.9:
            # temporarily reset target coordinates to prevent repeated triggers
            self.target_pose = Pose() 
            self.catch_process()

    def on_pose_received(self, msg):
        self.turtle1_pose = msg

    def on_target_pose_received(self, msg):
        self.target_pose = msg

    def turtle_cmd_callback(self, request, response) -> TurtleCmd.Response:
        twist = Twist()
        cmd = request.direction.lower()
        
        # 1. # Handle the client request here
        if cmd == 'w':
            twist.linear.x = 1.0* self.speed_multiplier
        elif cmd == 's':
            twist.linear.x = -1.0 * self.speed_multiplier
        elif cmd == 'a':
            twist.angular.z = 1.0 
        elif cmd == 'd':
            twist.angular.z = -1.0 
        elif cmd == 'speed_up':
            self.speed_multiplier = min(3.0, self.speed_multiplier + 0.1)
            self.get_logger().info(f"Speed multiplier increased: {self.speed_multiplier:.2f}")
        elif cmd == 'speed_down':
            self.speed_multiplier = max(1.0, self.speed_multiplier - 0.1)
            self.get_logger().info(f"Speed multiplier decreased: {self.speed_multiplier:.2f}")
        elif cmd == 'change_color':
            if time.time() - self.last_color_time > 0.5:  # limit color change frequency to prevent spamming
                self.change_turtle_color()
                self.last_color_time = time.time()
        elif cmd == 'stop':
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        else:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.get_logger().warn(f"Unknown command: {request.direction}")
            # 使用接口中定义的 FAIL 常量 (0)
            response.result = TurtleCmd.Response.FAIL
            return response

        # 2. 发布指令
        self.publisher_.publish(twist)
        self.get_logger().info(f"Executed: {cmd}")
        # 3. 成功响应
        response.result = TurtleCmd.Response.SUCCESS
        
        return response

def main():
    rclpy.init()
    node = TurtleGameServer('turtle_catch_game_server')
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
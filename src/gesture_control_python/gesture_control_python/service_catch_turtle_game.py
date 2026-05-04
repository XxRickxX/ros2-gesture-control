import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from turtlesim.srv import Spawn, Kill 
from geometry_msgs.msg import Twist
# 注意这里：根据你的 tree，包名是 ges_cl_interface，文件名是 TurtleCmd
from ges_cl_interface.srv import TurtleCmd
import random
import math

class TurtleGameServer(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        
        # 1. 基础控制：绑定你定义的 'turtle_cmd' 服务
        self.srv = self.create_service(TurtleCmd, 'turtle_cmd', self.turtle_cmd_callback)
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel', 10)
        
        # 2. 游戏管理：创建 Turtlesim 自带的 Spawn 和 Kill 客户端
        self.spawn_client = self.create_client(Spawn, 'spawn')
        self.kill_client = self.create_client(Kill, 'kill')
        
        # 3. 坐标追踪
        self.turtle1_pose = Pose() # 主乌龟位置
        self.target_pose = Pose()  # 目标乌龟位置
        self.target_name = "prey"   # 给目标乌龟起个名
        
        # 订阅主乌龟 (turtle1)
        self.create_subscription(Pose, 'turtle1/pose', self.on_pose_received, 10)
        # 订阅目标乌龟 (prey)
        self.create_subscription(Pose, f'{self.target_name}/pose', self.on_target_pose_received, 10)

        # 4. 初始化游戏：生成第一只目标乌龟
        self.spawn_new_target()
        
        # 5. 碰撞检测计时器：每 0.1 秒计算一次距离 (10Hz)
        self.create_timer(0.1, self.collision_detection_loop)
        
        self.get_logger().info('游戏服务端已就绪！目标接口：TurtleCmd')

    def spawn_new_target(self):
        """异步调用 /spawn 服务"""
        if not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('等待 spawn 服务中...')
            return
            
        req = Spawn.Request()
        req.x = random.uniform(1.0, 10.0)
        req.y = random.uniform(1.0, 10.0)
        req.theta = random.uniform(0.0, 6.28)
        req.name = self.target_name
        self.spawn_client.call_async(req)
        self.get_logger().info(f"新乌龟已刷新：x={req.x:.2f}")

    def collision_detection_loop(self):
        """欧几里得距离检测"""
        # 计算两点间距离
        distance = math.sqrt(
            (self.turtle1_pose.x - self.target_pose.x)**2 + 
            (self.turtle1_pose.y - self.target_pose.y)**2
        )
        
        # 触发阈值建议设为 0.6 - 0.8
        if distance < 0.7 and self.target_pose.x != 0.0:
            self.get_logger().info("🎯 抓到了！")
            self.catch_process()

    def catch_process(self):
        """核心重置逻辑"""
        # 1. 杀掉现有的 prey
        kill_req = Kill.Request()
        kill_req.name = self.target_name
        self.kill_client.call_async(kill_req)
        
        # 2. 瞬间再生
        self.spawn_new_target()

    def on_pose_received(self, msg):
        self.turtle1_pose = msg

    def on_target_pose_received(self, msg):
        self.target_pose = msg

    def turtle_cmd_callback(self, request, response) -> TurtleCmd.Response:
        twist = Twist()
        cmd = request.direction.lower()
        
        # 1. 运动逻辑处理
        if cmd == 'w':
            twist.linear.x = 1.0
        elif cmd == 's':
            twist.linear.x = -1.0
        elif cmd == 'a':
            twist.angular.z = 1.0
        elif cmd == 'd':
            twist.angular.z = -1.0
        elif cmd == 'stop':
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        else:
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
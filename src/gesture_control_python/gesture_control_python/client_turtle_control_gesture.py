import rclpy
from rclpy.node import Node
from ges_cl_interface.srv import TurtleCmd 
import math
import cv2
import mediapipe as mp



mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

class GestureControlClient(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        self.get_logger().info(f"{node_name} has been started!")

        self.ges_con_client_ = self.create_client(TurtleCmd, 'turtle_cmd')
        while not self.ges_con_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again')
        self.get_logger().info('connected to the turtle control service')

        # initialize camera
        self.cap = cv2.VideoCapture(0)

        # initialize MediaPipe
        self.hands = mp_hands.Hands(
            model_complexity = 0, #simple model
            max_num_hands = 1, # only detect one hand
            min_detection_confidence = 0.8, # minimum confidence for hand detection
            min_tracking_confidence = 0.5 # minimum confidence for hand tracking   
        )

        self.gesture_names = {
            'w':'Forward (5 fingers)',
            's':'Backward (Fist)',
            'a':'Turn Left(1 fingers)',
            'd':'Turn Right(2 fingers)',
            'change_color':'Change Color (Rock)',
            'speed_up':'Speed Up (6 fingers)',
            'speed_down':'Slow Down (7 fingers)',
            'not_good':'I know you will do that...'
        }

        self.last_gesture = None

        # 
        self.create_timer(0.1,self.process_frame)

        self.get_logger().info('Gesture Control Node Started')

    def vector_2d_angle(self, v1, v2):
        v1_x = v1[0]
        v1_y = v1[1]
        v2_x = v2[0]
        v2_y = v2[1]
        try:
            angle_ = math.degrees(
                math.acos(
                    (v1_x*v2_x + v1_y*v2_y) /
                    (((v1_x**2+v1_y**2)**0.5)*((v2_x**2+v2_y**2)**0.5))
                )
            )
        except:
            angle_=180
        return angle_
    
    def hand_angle(self, hand_):
        angle_list=[]
            # calculate thumb angle
            # === 计算大拇指的弯曲角度 ===
            # 原理：通过计算“手掌边缘向量”与“指尖向量”的夹角来判断手指是否伸直
            # hand_[n][0] 是第 n 个点的 X 坐标，hand_[n][1] 是 Y 坐标
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0]) - int(hand_[2][0])),(int(hand_[0][1])-int(hand_[2][1]))),
            ((int(hand_[3][0]) - int(hand_[4][0])),(int(hand_[3][1])-int(hand_[4][1])))
        )
        angle_list.append(angle_)

        # calculate index finger angle 食指
        angle_ = self.vector_2d_angle(
                ((int(hand_[0][0]) - int(hand_[6][0])), (int(hand_[0][1]) - int(hand_[6][1]))),
                ((int(hand_[7][0]) - int(hand_[8][0])), (int(hand_[7][1]) - int(hand_[8][1])))
            )
        angle_list.append(angle_)

        # calculate middle finger angle 中指
        angle_ = self.vector_2d_angle(
                ((int(hand_[0][0]) - int(hand_[10][0])), (int(hand_[0][1]) - int(hand_[10][1]))),
                ((int(hand_[11][0]) - int(hand_[12][0])), (int(hand_[11][1]) - int(hand_[12][1])))
            )
        angle_list.append(angle_)

        # calculate ring finger angle 无名指
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0]) - int(hand_[14][0])), (int(hand_[0][1]) - int(hand_[14][1]))),
            ((int(hand_[15][0]) - int(hand_[16][0])), (int(hand_[15][1]) - int(hand_[16][1])))
            ) 
        angle_list.append(angle_)

        # calculate pinky finger angle 小拇指
        angle_ = self.vector_2d_angle(
                ((int(hand_[0][0]) - int(hand_[18][0])), (int(hand_[0][1]) - int(hand_[18][1]))),
                ((int(hand_[19][0]) - int(hand_[20][0])), (int(hand_[19][1]) - int(hand_[20][1])))
            )
        angle_list.append(angle_)

        return angle_list
    
    def detect_gesture(self, angle_list):
        "detect hand gesture"
        f1,f2,f3,f4,f5 = angle_list

        if f1 < 50 and f2 < 50 and f3 < 50 and f4 < 50 and f5 < 50: # 5 fingers
            return 'w'
        elif f1 >= 50 and f2 >= 50 and f3 >= 50 and f4 >= 50 and f5 >= 50: # fist
            return 's'
        elif f1 >= 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 >= 50: # 1 finger
            return 'a'
        elif f1 >= 50 and f2 < 50 and f3 < 50 and f4 >= 50 and f5 >= 50: # 
            return 'd' 
        elif f1 < 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 < 50: # rock, change color
            return 'change_color'
        elif f1 < 50 and f2 >= 50 and f3 >= 50 and f4 >= 50 and f5 < 50: # six , speed up
            return 'speed_up'
        elif f1 < 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 >= 50: # seven , speed down
            return 'speed_down'
        elif f1 >= 50 and f2 >= 50 and f3 < 50 and f4 >= 50 and f5 >= 50: # 
            return 'not_good'
        else:
            return None

    
    def process_frame(self):

        fontFace = cv2.FONT_HERSHEY_SIMPLEX # set the font for displaying text
        linType = cv2.LINE_AA # set the line type for displaying text
        ret, img = self.cap.read()
        if not ret:
            return
        # 1. Flip the image horizontally for a later selfie-view display, and convert the BGR image to RGB.
        w, h = img.shape[1], img.shape[0]

        # 2. mediapie need RGB image, so convert the BGR image to RGB
        img_rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

        # 3. detect the hand gesture
        results = self.hands.process(img_rgb)

        gesture= None # initialize gesture

        # 4. analyse coordinates,
        if results.multi_hand_landmarks:
            # only process the first detected hand
            hand_landmarks = results.multi_hand_landmarks[0]

            finger_points = []
            for landmark in hand_landmarks.landmark:
                x = int(landmark.x*w) 
                y = int(landmark.y*h)
                finger_points.append((x,y))
                # 5. check the finger angle
            if len(finger_points)>0:
                angle_list = self.hand_angle(finger_points)
                
                # 6. identifiy the detected gesture
                gesture =self.detect_gesture(angle_list)

                # 7. visualize the hand structure
                mp_drawing.draw_landmarks( # draw the hand landmarks on the original image
                    img, # the original image
                    hand_landmarks, # the hand landmarks to draw
                    mp_hands.HAND_CONNECTIONS, # the connections between the landmarks to draw
                    mp_drawing_styles.get_default_hand_landmarks_style(), # the style for drawing the landmarks
                    mp_drawing_styles.get_default_hand_connections_style() # the style for drawing the connections
                    )  

        # 8. send the ROS2 command
        if gesture:
            self.send_command(gesture)
            self.last_gesture = gesture
        elif not gesture:
            self.last_gesture = None 
        

        # 9. display the image
        text = f'Gesture: {self.gesture_names.get(gesture, "Unknown")}' # get the gesture name from the dictionary, if not found, display "Unknown"
            # parameters 1. panel 2. text 3. position 4. font 5. font scale 6. color 7. thickness 8. line type
        cv2.putText(img, text, (10,30), fontFace, 1, (0,255,0), 2, linType)

        cv2.imshow('Gesture Control',img)

        cv2.waitKey(1)

    def send_command(self,direction):
        request = TurtleCmd.Request()
        request.direction = direction

        # send async command
        future = self.ges_con_client_.call_async(request)
        future.add_done_callback(self.handle_reponse)

        
        # if gesture not existing in dictionary, return its current value
        self.get_logger().info(f'sending command:{self.gesture_names.get(direction,direction)}')


    def handle_reponse(self,future):
        try:
            response = future.result()
            # check the response and log the result
            if response.result == TurtleCmd.Response.SUCCESS:
                self.get_logger().info('Command executed successfully.')
            else:
                self.get_logger().warn('Command execution failed.')
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')

    def destroy_node(self):
        if self.hands:
            self.hands.close() # release the MediaPipe resources       
        self.cap.release() # release the camera and close the OpenCV windows      
        cv2.destroyAllWindows()# destroy all OpenCV windows
        
        # call the parent class's destroy_node method to ensure proper cleanup
        super().destroy_node()
    
def main(args=None):
    rclpy.init()
    node = GestureControlClient('gesture_control_client_node')
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Handle keyboard interrupt (Ctrl-C) gracefully
        node.get_logger().info('Keyboard interrupt received, exiting...')
    
    finally:
        node.destroy_node()
        rclpy.shutdown()
if __name__ == '__main__':
    main()


    
 
    
        

        
    

                    





                








        


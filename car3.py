from flask import Flask, Response, render_template
import cv2
from threading import Thread
import RPi.GPIO as GPIO    # 引入GPIO模块
import tty, sys, select, termios



app = Flask(__name__)

camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        ret, frame = camera.read()
        #将视频流转成图像用于传向前端
        frame = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')





#小车控制
def getKey(settings):
    tty.setraw(sys.stdin.fileno())
    rlist = select.select([sys.stdin], [], [], 0.1)

    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ""

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def carControl():
    # 定义对应的引脚变量
    ENA = 38
    INT1 = 37
    INT2 = 35
    INT3 = 33
    INT4 = 31
    ENB = 29

    GPIO.setmode(GPIO.BOARD)  # 使用BCM编号方式
    GPIO.setup(ENA, GPIO.OUT)  # 将连接ENA的GPIO引脚设置为输出模式
    GPIO.setup(INT1, GPIO.OUT)  # 将连接IN1的GPIO引脚设置为输出模式
    GPIO.setup(INT2, GPIO.OUT)  # 将连接IN2的GPIO引脚设置为输出模式
    GPIO.setup(INT3, GPIO.OUT)  # 将连接IN3的GPIO引脚设置为输出模式
    GPIO.setup(INT4, GPIO.OUT)  # 将连接IN4的GPIO引脚设置为输出模式
    GPIO.setup(ENB, GPIO.OUT)  # 将连接INB的GPIO引脚设置为输出模式

    print('ready')
    while True:
        setting = termios.tcgetattr(sys.stdin)
        InPut = getKey(setting)

        if InPut == 'w':  # 如果键盘输入w，则电机正转
            GPIO.output(ENA, GPIO.HIGH)
            GPIO.output(ENB, GPIO.HIGH)
            GPIO.output(INT3, GPIO.HIGH)
            GPIO.output(INT4, GPIO.LOW)
            GPIO.output(INT1, GPIO.HIGH)
            GPIO.output(INT2, GPIO.LOW)
            time.sleep(1)
            #print('前进')
        elif InPut == 's':  # 如果键盘输入s，则电机反转
            GPIO.output(INT1, GPIO.LOW)
            GPIO.output(INT2, GPIO.HIGH)
            GPIO.output(INT3, GPIO.LOW)
            GPIO.output(INT4, GPIO.HIGH)
            GPIO.output(ENA, GPIO.HIGH)
            GPIO.output(ENB, GPIO.HIGH)
            time.sleep(1)
            #print('后退')
        elif InPut == 'd':
            GPIO.output(INT1, GPIO.LOW)
            GPIO.output(INT2, GPIO.LOW)
            GPIO.output(INT3, GPIO.HIGH)
            GPIO.output(INT4, GPIO.LOW)
            GPIO.output(ENA, GPIO.HIGH)
            GPIO.output(ENB, GPIO.HIGH)
            time.sleep(0.2)
            #print('左转')
        elif InPut == 'a':
            GPIO.output(INT1, GPIO.HIGH)
            GPIO.output(INT2, GPIO.LOW)
            GPIO.output(INT3, GPIO.LOW)
            GPIO.output(INT4, GPIO.LOW)
            GPIO.output(ENA, GPIO.HIGH)
            GPIO.output(ENB, GPIO.HIGH)
            time.sleep(0.2)
            #print('右转')
        elif InPut == 'q':  # 如果键盘输入的数值为q，退出
            GPIO.output(INT1, GPIO.LOW)
            GPIO.output(INT2, GPIO.LOW)
            GPIO.output(ENA, GPIO.LOW)
            GPIO.output(INT3, GPIO.LOW)
            GPIO.output(INT4, GPIO.LOW)
            GPIO.output(ENB, GPIO.LOW)
            #print('退出程序')
            break
        else:
            GPIO.output(INT1, GPIO.LOW)
            GPIO.output(INT2, GPIO.LOW)
            GPIO.output(ENA, GPIO.LOW)
            GPIO.output(INT3, GPIO.LOW)
            GPIO.output(INT4, GPIO.LOW)
            GPIO.output(ENB, GPIO.LOW)
            #print("Input Error,Please give a true index!!")

if __name__ == '__main__':
    app.run()
    # 创建线程
    car = Thread(target=carControl, args=())
    car.daemon = True
    car.start()

    while True:
        pass



import cv2
from ultralytics import YOLO
import serial
import time

# 加载模型
model = YOLO('best.pt')

# 初始化串口通信
serial_port = None
try:
    serial_port = serial.Serial('COM13', 9600, timeout=1)
    print("串口连接成功！")
    time.sleep(2)  # 等待Arduino重置和串口稳定
except Exception as e:
    print(f"串口初始化失败: {e}")

# 初始化摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

# 添加状态跟踪变量
last_valid_label = None  # 上一次发送指令的状态
last_label = None  # 当前帧的检测结果

while True:
    ret, frame = cap.read()
    if not ret:
        print("无法读取摄像头帧")
        break

    # YOLOv8 进行预测
    results = model(frame)

    # 可视化检测结果
    annotated_frame = results[0].plot()

    # 解析检测结果
    detections = results[0].boxes.data
    
    current_label = None  # 当前检测的标签，默认无标签
    if len(detections) > 0:  # 如果有检测到物体
        det = detections[0]  # 取第一个检测结果
        x1, y1, x2, y2, conf, cls = det.tolist()
        current_label = model.names[int(cls)]

    # 判断是否需要发送指令（根据有效状态变化）
    if current_label != last_valid_label:
        if current_label == "good":
            if serial_port:
                serial_port.write(b'd')
                serial_port.flush()
            print("发送到串口: d")
            last_valid_label = "good"  # 更新有效状态
        elif current_label == "bad":
            if serial_port:
                serial_port.write(b'u')
                serial_port.flush()
            print("发送到串口: u")
            last_valid_label = "bad"  # 更新有效状态
        elif current_label is None:  # 当没有检测到时，不发送指令但保持状态不变
            last_valid_label = None

    # 显示实时检测画面
    cv2.imshow("YOLOv8 Real-Time Detection", annotated_frame)

    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
if serial_port:
    serial_port.close()

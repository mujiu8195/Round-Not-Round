#include <Servo.h> // 包含舵机库

Servo myServo;     // 创建一个舵机对象
int servoPin = 9;  // 定义舵机控制针脚
int pos = 90;      // 舵机初始位置为 90°
bool isMoving = false; // 标记舵机是否在执行动作

void setup() {
  myServo.attach(servoPin); // 将舵机对象绑定到指定针脚
  myServo.write(pos);       // 将舵机移动到初始位置
  Serial.begin(9600);       // 初始化串口通信
}

void loop() {
  if (!isMoving && Serial.available() > 0) {  // 检查是否有串口输入，且当前未在执行动作
    char command = Serial.read();             // 读取串口指令
    if (command == 'u') {                     // 接收到 'u' 指令
      executeCommand(180);                    // 执行转到 180° 动作
    } else if (command == 'd') {              // 接收到 'd' 指令
      executeCommand(0);                      // 执行转到 0° 动作
    }
  }
}

// 定义完整的动作执行函数
void executeCommand(int targetPos) {
  isMoving = true;           // 标记舵机正在执行动作
  moveServo(targetPos);      // 缓慢转动舵机到目标位置
  delay(5000);               // 等待 5 秒
  moveServo(90);             // 缓慢回到中间位置
  isMoving = false;          // 标记舵机动作完成
}

// 定义缓慢转动舵机的函数
void moveServo(int targetPos) {
  if (targetPos > pos) {
    for (int i = pos; i <= targetPos; i++) { // 从当前位置逐步增加到目标位置
      myServo.write(i);                      // 设置舵机位置
      delay(15);                             // 控制转动速度（每步15ms）
    }
  } else {
    for (int i = pos; i >= targetPos; i--) { // 从当前位置逐步减小到目标位置
      myServo.write(i);                      // 设置舵机位置
      delay(15);                             // 控制转动速度
    }
  }
  pos = targetPos;                           // 更新当前位置
}

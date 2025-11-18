#include <Servo.h>

Servo myservo;  // 创建舵机对象
const int servoPin = 9;  // 舵机连接的引脚

void setup() {
  myservo.attach(servoPin);  // 将舵机连接到指定引脚
}

void loop() {

  // 逆时针缓慢转动（改变PWM占空比，较小的脉宽）
  myservo.writeMicroseconds(1600);  // 控制为逆时针缓慢转动
  delay(50);  // 每次发送控制信号的延时


}

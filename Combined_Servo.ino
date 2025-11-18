#include <Servo.h>

Servo myServo;  // 创建舵机对象

void setup() {
    myServo.attach(9);  // 连接舵机到 9 号引脚

}

void loop() {
    myServo.write(0); // 转到 180°
    delay(1000);        // 等待 1 秒

    myServo.write(70);  // 回中 90°
    delay(1000);        // 等待 1 秒

    myServo.write(2);   // 转到 0°
    delay(1000);        // 等待 1 秒

    myServo.write(70);  // 回中 90°
    delay(1000);        // 等待 1 秒

    while(1);  // 停止循环
}

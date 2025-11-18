#include <Servo.h>

// 创建舵机对象
Servo liftServo;    // 升降舵机
Servo flipServo1;   // 翻转舵机1
Servo flipServo2;   // 翻转舵机2

// 定义引脚
const int liftServoPin = 9;    // 升降舵机引脚
const int flipServo1Pin = 10;  // 翻转舵机1引脚
const int flipServo2Pin = 11;  // 翻转舵机2引脚

// 定义位置参数
const int centerPos = 90;      // 中间位置
const int flipAngle = 60;      // 翻转角度
const int liftAngle = 180;     // 升降角度
int currentLiftPos = 90;       // 当前升降位置

bool isMoving = false;         // 动作执行标志
unsigned long moveStartTime = 0;
const unsigned long MOVE_TIMEOUT = 10000; // 10秒超时

void setup() {
    // 初始化舵机
    liftServo.attach(liftServoPin);
    flipServo1.attach(flipServo1Pin);
    flipServo2.attach(flipServo2Pin);
    
    // 初始化位置
    liftServo.write(centerPos);
    flipServo1.write(centerPos);
    flipServo2.write(centerPos);
    
    Serial.begin(9600);
    delay(1000);  // 等待串口稳定
}

// 控制升降舵机缓慢移动
void moveLiftServo(int targetPos) {
    if (targetPos > currentLiftPos) {
        for (int i = currentLiftPos; i <= targetPos; i++) {
            liftServo.write(i);
            delay(15);
        }
    } else {
        for (int i = currentLiftPos; i >= targetPos; i--) {
            liftServo.write(i);
            delay(15);
        }
    }
    currentLiftPos = targetPos;
}

// 控制翻转舵机同步缓慢移动
void moveFlipServos(int startAngle1, int endAngle1, int startAngle2, int endAngle2) {
    int steps = abs(endAngle1 - startAngle1);
    
    for (int i = 0; i <= steps; i++) {
        int angle1 = startAngle1 + (startAngle1 < endAngle1 ? i : -i);
        int angle2 = startAngle2 + (startAngle2 < endAngle2 ? i : -i);
        
        flipServo1.write(angle1);
        flipServo2.write(angle2);
        delay(15);
    }
}

// 执行向上动作序列
void moveUp() {
    Serial.println("执行向上动作");
    // 1. 升降舵机向上移动
    moveLiftServo(liftAngle);
    delay(500);
    
    // 2. 执行向上翻转
    moveFlipServos(centerPos, centerPos + flipAngle, centerPos, centerPos - flipAngle);
    delay(2000);
    
    // 3. 翻转舵机回中
    moveFlipServos(centerPos + flipAngle, centerPos, centerPos - flipAngle, centerPos);
    delay(500);
    
    // 4. 升降舵机回中
    moveLiftServo(centerPos);
    Serial.println("向上动作完成");
}

// 执行向下动作序列
void moveDown() {
    Serial.println("执行向下动作");
    // 1. 升降舵机向下移动
    moveLiftServo(0);
    delay(500);
    
    // 2. 执行向下翻转
    moveFlipServos(centerPos, centerPos - flipAngle, centerPos, centerPos + flipAngle);
    delay(2000);
    
    // 3. 翻转舵机回中
    moveFlipServos(centerPos - flipAngle, centerPos, centerPos + flipAngle, centerPos);
    delay(500);
    
    // 4. 升降舵机回中
    moveLiftServo(centerPos);
    Serial.println("向下动作完成");
}

void loop() {
    // 添加超时检测
    if (isMoving && (millis() - moveStartTime > MOVE_TIMEOUT)) {
        isMoving = false;
        Serial.println("动作执行超时，重置状态");
    }

    if (!isMoving && Serial.available() > 0) {
        char command = Serial.read();
        Serial.print("收到指令: ");
        Serial.println(command);
        
        isMoving = true;
        moveStartTime = millis();
        
        if (command == 'u') {
            moveUp();
        } 
        else if (command == 'd') {
            moveDown();
        }
        
        isMoving = false;
    }
}
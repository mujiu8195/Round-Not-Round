# camera_light_detector.py
# 实现摄像头检测强光时不拍摄，光被阻挡后拍摄

import cv2
import numpy as np
import os
import time

# 配置参数
SAVE_FOLDER = r"H:\作品集\项目一\code\生成花\照片"
LIGHT_THRESHOLD = 200  # 光线亮度阈值，越高则越亮的区域才被视为"强光"
BRIGHT_AREA_THRESHOLD = 0.10  # 强光区域占比阈值，超过10%认为有强光
STABILITY_FRAMES = 5  # 需要连续多少帧满足条件才触发拍摄
COOLDOWN_TIME = 2.0  # 拍摄冷却时间（秒）
CAMERA_INDEX = 0  # 摄像头索引，通常默认摄像头为0
HORIZONTAL_RESOLUTION = (1024, 768)  # 横向分辨率
VERTICAL_RESOLUTION = (768, 1024)    # 纵向分辨率
current_orientation = "horizontal"    # 当前方向，默认横向

def ensure_folder_exists():
    """确保保存文件夹存在"""
    if not os.path.exists(SAVE_FOLDER):
        try:
            os.makedirs(SAVE_FOLDER)
            print(f"创建文件夹: {SAVE_FOLDER}")
        except Exception as e:
            print(f"创建文件夹失败: {e}")
            return False
    return True

def get_next_filename():
    """获取下一个可用的文件名"""
    ensure_folder_exists()
    
    try:
        # 获取所有jpg文件并找出最大编号
        files = [f for f in os.listdir(SAVE_FOLDER) if f.endswith('.jpg') and f[:-4].isdigit()]
        
        # 如果没有文件，从1开始
        if not files:
            return os.path.join(SAVE_FOLDER, "1.jpg")
        
        # 提取数字部分并找出最大值
        max_num = max([int(f[:-4]) for f in files])
        next_num = max_num + 1
        
        return os.path.join(SAVE_FOLDER, f"{next_num}.jpg")
    except Exception as e:
        print(f"获取文件名时出错: {e}")
        # 发生错误时使用时间戳作为备用文件名
        timestamp = int(time.time())
        return os.path.join(SAVE_FOLDER, f"backup_{timestamp}.jpg")

def detect_strong_light(frame):
    """检测图像中是否有强光"""
    # 转换为灰度图
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 计算亮度超过阈值的像素占比
    bright_pixels = np.sum(gray > LIGHT_THRESHOLD)
    total_pixels = gray.size
    bright_ratio = bright_pixels / total_pixels
    
    # 返回是否有强光（亮区域占比超过阈值）
    has_strong_light = bright_ratio > BRIGHT_AREA_THRESHOLD
    return has_strong_light, bright_ratio

def resize_image(frame, orientation):
    """根据指定方向调整图像大小"""
    if orientation == "horizontal":
        return cv2.resize(frame, HORIZONTAL_RESOLUTION)
    else:  # vertical
        return cv2.resize(frame, VERTICAL_RESOLUTION)

def save_image(frame, filename, orientation):
    """保存图像到指定文件"""
    # 调整图像大小
    resized_frame = resize_image(frame, orientation)
    
    # 保存图像
    try:
        cv2.imwrite(filename, resized_frame)
        print(f"已保存图片: {os.path.basename(filename)}")
        return True
    except Exception as e:
        print(f"保存图片失败: {e}")
        return False

def main():
    global current_orientation
    
    # 确保文件夹存在
    if not ensure_folder_exists():
        print("无法创建保存文件夹，程序退出")
        return
    
    # 初始化摄像头
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print("无法打开摄像头，请检查连接或更改摄像头索引")
        return
    
    # 获取摄像头分辨率
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"摄像头分辨率: {frame_width}x{frame_height}")
    
    print("摄像头已启动，正在监测光线...")
    print(f"图片将保存到: {SAVE_FOLDER}")
    print(f"强光亮度阈值: {LIGHT_THRESHOLD}")
    print(f"强光区域占比阈值: {BRIGHT_AREA_THRESHOLD*100:.1f}%")
    print(f"默认照片方向: {current_orientation} ({HORIZONTAL_RESOLUTION if current_orientation == 'horizontal' else VERTICAL_RESOLUTION})")
    print("按'o'键切换照片方向，'c'键手动拍照，ESC键退出")
    
    # 状态变量
    last_capture_time = 0
    stable_dark_frames = 0  # 连续暗帧计数
    was_bright = False  # 修改初始状态为无强光，这样在开始时如果检测到无强光会开始计数
    initial_check = True  # 标记程序是否刚刚启动
    
    try:
        while True:
            # 读取一帧图像
            ret, frame = cap.read()
            if not ret:
                print("无法获取图像，退出程序")
                break
            
            # 检测强光
            has_strong_light, bright_ratio = detect_strong_light(frame)
            
            # 在图像上显示当前状态
            status_text = f"强光检测: {'是' if has_strong_light else '否'} ({bright_ratio*100:.1f}%)"
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 0, 255) if has_strong_light else (0, 255, 0), 2)
            
            current_time = time.time()
            time_since_last_capture = current_time - last_capture_time
            cooldown_text = f"冷却: {max(0, COOLDOWN_TIME - time_since_last_capture):.1f}秒"
            cv2.putText(frame, cooldown_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            orientation_text = f"方向: {'横向' if current_orientation == 'horizontal' else '纵向'}"
            cv2.putText(frame, orientation_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # 程序刚启动时，如果没有强光，立即拍一张照片
            if initial_check:
                initial_check = False
                if not has_strong_light and time_since_last_capture >= COOLDOWN_TIME:
                    filename = get_next_filename()
                    save_image(frame, filename, current_orientation)
                    last_capture_time = current_time
            
            # 显示实时画面
            cv2.imshow("摄像头光线监测", frame)
            
            # 强光变暗（被阻挡）时的逻辑
            if was_bright and not has_strong_light:
                # 连续暗帧计数增加
                stable_dark_frames += 1
                
                # 如果连续多帧都是暗的，且超过冷却时间，则拍摄
                if (stable_dark_frames >= STABILITY_FRAMES and 
                    time_since_last_capture >= COOLDOWN_TIME):
                    
                    # 获取下一个文件名
                    filename = get_next_filename()
                    
                    # 保存图片
                    save_image(frame, filename, current_orientation)
                    
                    # 更新拍摄时间
                    last_capture_time = current_time
                    stable_dark_frames = 0
            
            # 持续无强光的情况
            elif not has_strong_light:
                # 连续暗帧计数增加
                stable_dark_frames += 1
                
                # 如果连续多帧都是暗的，且超过冷却时间，则拍摄
                if (stable_dark_frames >= STABILITY_FRAMES and 
                    time_since_last_capture >= COOLDOWN_TIME):
                    
                    # 获取下一个文件名
                    filename = get_next_filename()
                    
                    # 保存图片
                    save_image(frame, filename, current_orientation)
                    
                    # 更新拍摄时间
                    last_capture_time = current_time
                    stable_dark_frames = 0
            
            elif has_strong_light:
                # 如果检测到强光，重置暗帧计数
                stable_dark_frames = 0
            
            # 更新上一帧状态
            was_bright = has_strong_light
            
            # 按键处理
            key = cv2.waitKey(1)
            if key == 27:  # ESC键
                break
            elif key == ord('c'):  # 按C键手动拍照
                filename = get_next_filename()
                save_image(frame, filename, current_orientation)
                print(f"手动拍摄: {os.path.basename(filename)}")
                last_capture_time = current_time
            elif key == ord('o'):  # 按O键切换照片方向
                current_orientation = "vertical" if current_orientation == "horizontal" else "horizontal"
                print(f"已切换照片方向为: {current_orientation}")
    
    finally:
        # 释放资源
        cap.release()
        cv2.destroyAllWindows()
        print("程序已退出")

if __name__ == "__main__":
    main()
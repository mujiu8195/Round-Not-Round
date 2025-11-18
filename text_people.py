import cv2
import os
from datetime import datetime
import time

class FaceDetectionRecorder:
    def __init__(self, save_path='H:\\person', max_videos=12):
        self.save_path = save_path
        self.max_videos = max_videos
        
        # 创建保存目录
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        # 初始化摄像头
        self.cap = cv2.VideoCapture(0)
        
        # 初始化人脸检测器
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # 视频写入器
        self.video_writer = None
        self.recording = False
        
        # 当前视频编号
        self.current_video_number = self._get_next_video_number()

    def _get_next_video_number(self):
        """获取下一个要覆盖的视频编号"""
        existing_files = [f for f in os.listdir(self.save_path) if f.endswith('.avi')]
        if not existing_files:
            return 1
            
        numbers = [int(f.split('.')[0]) for f in existing_files]
        if len(numbers) < self.max_videos:
            # 如果视频数量未达到最大值，返回下一个编号
            return len(numbers) + 1
        else:
            # 文件数已达到最大值，找到最早的录制文件编号
            file_times = {}
            for f in existing_files:
                file_path = os.path.join(self.save_path, f)
                file_times[int(f.split('.')[0])] = os.path.getmtime(file_path)
            
            # 返回最早录制的文件编号
            return min(file_times, key=file_times.get)

    def _start_recording(self):
        """开始录制视频"""
        if self.recording:
            return
            
        # 设置视频保存路径
        filename = f"{self.current_video_number}.avi"
        filepath = os.path.join(self.save_path, filename)
        
        # 初始化视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(
            filepath, 
            fourcc, 
            20.0, # FPS
            (int(self.cap.get(3)), int(self.cap.get(4)))
        )
        
        self.recording = True
        print(f"开始录制视频 {filename}")

    def _stop_recording(self):
        """停止录制视频"""
        if not self.recording:
            return
            
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            
        self.recording = False
        self.current_video_number = self._get_next_video_number()
        print("停止录制视频")

    def detect_and_record(self):
        """主循环：检测人脸并录制视频"""
        face_detected_frames = 0
        no_face_frames = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                # 转换为灰度图像进行人脸检测
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 人脸检测
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )

                # 绘制检测框
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, 'Face Detected', (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

                # 显示画面
                cv2.imshow('Face Detection', frame)

                # 检测到人脸
                if len(faces) > 0:
                    face_detected_frames += 1
                    no_face_frames = 0
                    
                    # 连续3帧检测到人脸才开始录制
                    if face_detected_frames >= 3 and not self.recording:
                        self._start_recording()
                else:
                    no_face_frames += 1
                    face_detected_frames = 0
                    
                    # 连续10帧未检测到人脸则停止录制
                    if no_face_frames >= 10 and self.recording:
                        self._stop_recording()

                # 如果正在录制，写入帧
                if self.recording and self.video_writer:
                    self.video_writer.write(frame)

                # 按'q'退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            # 清理资源
            self._stop_recording()
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    recorder = FaceDetectionRecorder()
    recorder.detect_and_record()
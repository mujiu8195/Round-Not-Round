from ultralytics import YOLO

model = YOLO('best.pt')

model.predict('2.jpg',save=True, classes = [0 , 1], line_width = 30)
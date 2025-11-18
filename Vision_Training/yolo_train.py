from ultralytics import YOLO

model = YOLO('yolov8n.pt')

model.train(data='gnocchi.yaml',epochs=100)

model.val()
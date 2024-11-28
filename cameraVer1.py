import cv2
import torch
from ultralytics import YOLO
import numpy as np
from datetime import datetime
import os

class ObjectDetection:
    def __init__(self):
        # Загрузка модели YOLOv8
        self.model = YOLO('yolov8n.pt')  # или другую версию модели
        
        # Классы объектов (COCO dataset)
        self.classes = self.model.names
        
        # Настройка параметров записи видео
        self.output_dir = "D:/recorded_videos/"  # Путь для сохранения
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def create_video_writer(self, video_cap, output_filename):
        # Получение параметров видео
        frame_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(video_cap.get(cv2.CAP_PROP_FPS))
        
        # Создание объекта для записи видео
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_path = os.path.join(self.output_dir, output_filename)
        return cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    def detect_objects(self):
        # Подключение к камере
        # Для веб-камеры используйте: cap = cv2.VideoCapture(0)
        # Для IP-камеры используйте URL в формате:
        # cap = cv2.VideoCapture('rtsp://username:password@ip_address:port/path')
        cap = cv2.VideoCapture(0)  # измените на нужный источник

        if not cap.isOpened():
            print("Ошибка при подключении к камере")
            return

        # Создание файла для записи
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'detection_{timestamp}.avi'
        video_writer = self.create_video_writer(cap, output_filename)

        try:
            while True:
                # Чтение кадра
                ret, frame = cap.read()
                if not ret:
                    print("Ошибка при получении кадра")
                    break

                # Распознавание объектов
                results = self.model(frame)
                
                # Обработка результатов
                for result in results:
                    boxes = result.boxes.cpu().numpy()
                    for box in boxes:
                        # Получение координат
                        x1, y1, x2, y2 = box.xyxy[0].astype(int)
                        # Получение класса и уверенности
                        class_id = int(box.cls[0])
                        conf = box.conf[0]
                        
                        # Отрисовка прямоугольника и подписи
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        label = f'{self.classes[class_id]} {conf:.2f}'
                        cv2.putText(frame, label, (x1, y1 - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Запись кадра
                video_writer.write(frame)

                # Отображение результата
                cv2.imshow('Object Detection', frame)

                # Выход по нажатию 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            # Освобождение ресурсов
            cap.release()
            video_writer.release()
            cv2.destroyAllWindows()

    def __del__(self):
        cv2.destroyAllWindows()

# Запуск детектора
if __name__ == "__main__":
    detector = ObjectDetection()
    detector.detect_objects()
import cv2
import torch
from ultralytics import YOLO
import numpy as np
from datetime import datetime
import os
import argparse
from playsound import playsound
import threading
import time

class ObjectDetection:
    def __init__(self):
        # Определяем устройство для вычислений: используем CUDA (GPU), если доступно, иначе CPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu' 
         # Загрузка предобученной модели YOLO из указанного пути
        self.model = YOLO('D:/newProjectYOLOVer2/runs/detect/train/weights/best.pt').to(self.device)
        # Получение списка доступных классов (объектов), на которые обучена модель
        self.classes = self.model.names
         # Указываем путь для сохранения выходного видео
        self.output_dir = "D:/VideoToPython/recorded_videos/" 
        # Проверка существования директории для сохранения видео, если нет - создаем
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        # Установка порога для уверенности (confidence threshold) и IoU
        self.conf_threshold = 0.5
        self.iou_threshold = 0.45
        # Словарь для отслеживания времени последнего проигрывания звука для каждого класса
        self.last_sound_time = {}
        # Минимальный интервал между звуковыми оповещениями (в секундах)
        self.sound_cooldown = 3
        # Путь к звуковому файлу
        self.sound_file = "D:/VideoToPython/hazard-warning.mp3"  # Укажите путь к вашему звуковому файлу

    def play_sound(self, class_name):
        """Воспроизведение звука в отдельном потоке"""
        current_time = time.time()
        # Проверяем, прошло ли достаточно времени с последнего проигрывания для этого класса
        if current_time - self.last_sound_time.get(class_name, 0) >= self.sound_cooldown:
            try:
                threading.Thread(target=playsound, args=(self.sound_file,), daemon=True).start()
                self.last_sound_time[class_name] = current_time
                print(f"Обнаружен объект: {class_name}")
            except Exception as e:
                print(f"Ошибка воспроизведения звука: {e}")

    def create_video_writer(self, video_cap, output_filename):
        frame_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(video_cap.get(cv2.CAP_PROP_FPS))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_path = os.path.join(self.output_dir, output_filename)
        return cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    def process_frame(self, frame):
        results = self.model(frame, conf=self.conf_threshold, iou=self.iou_threshold)
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].astype(int)
                class_id = int(box.cls[0])
                conf = box.conf[0]
                class_name = self.classes[class_id]
                
                # Воспроизведение звука при обнаружении объекта
                self.play_sound(class_name)
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f'{class_name} {conf:.2f}'
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame

    def detect_objects(self, source):
        if source.isdigit():
            cap = cv2.VideoCapture(int(source))
        elif source.startswith(('rtsp://', 'http://', 'https://')):
            cap = cv2.VideoCapture(source)
        else:
            cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            print("Ошибка при открытии источника видео")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'detection_{timestamp}.avi'
        video_writer = self.create_video_writer(cap, output_filename)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Достигнут конец видео или произошла ошибка при чтении кадра")
                    break

                processed_frame = self.process_frame(frame)
                video_writer.write(processed_frame)
                cv2.imshow('Object Detection', processed_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release() # Освобождает ресурсы видеозахвата после завершения обработки
            video_writer.release()  # Освобождает ресурсы видеозаписи
            cv2.destroyAllWindows() # Закрывает все окна, созданные OpenCV

    def __del__(self):
        cv2.destroyAllWindows() # Закрывает все окна OpenCV

def main():
    parser = argparse.ArgumentParser(description="Object Detection with YOLOv8") # Создает парсер аргументов
    parser.add_argument("--source", type=str, default="0", #  Аргумент для источника видео (по умолчанию камера 0) "0" - web камера, D:/newproectYOLO/new_YOLOv8_собств_детекция/video_test3.mp4
                        help="Source of video. Can be camera index, video file path, or RTSP/HTTP URL")
    args = parser.parse_args() # Парсит переданные аргументы

    detector = ObjectDetection() # Создает экземпляр класса ObjectDetection
    detector.detect_objects(args.source) # Запускает детекцию объектов с указанным источником

if __name__ == "__main__": # Проверяет, является ли данный файл основным модулем
    main() # Вызывает основную функцию
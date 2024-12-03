import cv2  # Импорт библиотеки OpenCV для работы с видео и изображениями
import torch  # Импорт библиотеки PyTorch для работы с моделями глубокого обучения
from ultralytics import YOLO  # Импортирует класс YOLO из библиотеки Ultralytics для детекции объектов
import numpy as np  # Импорт библиотеки NumPy для работы с массивами
from datetime import datetime  # Импорт модуля datetime для работы с датой и временем
import os  # Импорт модуля os для взаимодействия с файловой системой
import threading  # Импорт модуля threading для работы с потоками
import time  # Импорт модуля time для работы со временем
import telebot  # Импорт библиотеки для работы с Telegram Bot API
from playsound import playsound  # Импорт функции playsound для воспроизведения звуковых файлов
import argparse  # Импорт библиотеки argparse для обработки аргументов командной строки

class ObjectDetection:
    def __init__(self, telegram_token, chat_id):  # Исправлено на __init__
        # Инициализация бота Telegram
        self.bot = telebot.TeleBot(telegram_token)
        self.chat_id = chat_id
        
        # Выбор устройства для вычислений: используем CUDA, если доступно, иначе - CPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Загрузка предобученной модели YOLO
        self.model = YOLO('D:/newProjectYOLOVer2/runs/detect/train/weights/best.pt').to(self.device)
        
        # Получение списка классов, использующихся в модели
        self.classes = self.model.names

        # Папки для сохранения видео и изображений
        self.output_dir = "D:/VideoToPython/recorded_videos/"
        self.save_images_dir = "D:/VideoToPython/saved_images/"
        
        # Создание директорий, если они не существуют
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.save_images_dir, exist_ok=True)
        
        # Параметры для фильтрации результатов детекции
        self.conf_threshold = 0.5  # Порог уверенности для детекции
        self.iou_threshold = 0.45  # Порог IoU для объединения боксов
        
        # Словарь для отслеживания последнего времени воспроизведения звуков
        self.last_sound_time = {}
        self.sound_cooldown = 3  # Время ожидания между воспроизведением звуков (в секундах)
        
        # Путь к звуковому файлу
        self.sound_file = "D:/VideoToPython/hazard-warning.mp3"

    def create_video_writer(self, video_cap, output_filename):
        """Создание объекта для записи видео"""
        frame_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(video_cap.get(cv2.CAP_PROP_FPS))  # Количество кадров в секунду
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Кодек для записи видео
        output_path = os.path.join(self.output_dir, output_filename)  # Полный путь для сохранения видео
        return cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    def save_image(self, frame, class_name):
        """Сохранение изображения при обнаружении объекта и отправка в Telegram"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Получение текущего времени как строки
        image_filename = f'{class_name}_{timestamp}.jpg'  # Форматирование имени файла
        image_path = os.path.join(self.save_images_dir, image_filename)  # Полный путь для сохранения изображения
        cv2.imwrite(image_path, frame)  # Сохранение изображения
        print(f"Сохранено изображение: {image_path}")  # Сообщение в консоль

        self.send_photo_to_telegram(image_path)  # Отправка изображения в Telegram

    def send_photo_to_telegram(self, image_path):
        """Отправка фотографии в группу Telegram"""
        with open(image_path, 'rb') as photo:
            self.bot.send_photo(self.chat_id, photo)

    def play_sound(self, class_name):
        """Воспроизведение звука в отдельном потоке"""  
        current_time = time.time()  # Получение текущего времени
        # Проверка, достаточно ли времени прошло для воспроизведения звука
        if current_time - self.last_sound_time.get(class_name, 0) >= self.sound_cooldown:
            try:
                # Запуск потока для воспроизведения звука
                threading.Thread(target=playsound, args=(self.sound_file,), daemon=True).start()
                self.last_sound_time[class_name] = current_time  # Обновление времени последнего воспроизведения звука
                print(f"Обнаружен объект: {class_name}")  # Сообщение о распознавании объекта
            except Exception as e:
                print(f"Ошибка воспроизведения звука: {e}")  # Обработка ошибок воспроизведения звука

    def detect_objects(self, source):
        """Функция для детекции объектов"""
        cap = cv2.VideoCapture(source)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = self.model(frame)
            for result in results:
                boxes = result.boxes  # Получение боксов
                for box in boxes:
                    if box.conf >= self.conf_threshold:  # Проверка порога уверенности
                        class_id = int(box.cls)
                        class_name = self.classes[class_id]
                        # Рисуем прямоугольник вокруг найденного объекта
                        cv2.rectangle(frame, (int(box.x1), int(box.y1)), (int(box.x2), int(box.y2)), (255, 0, 0), 2)
                        cv2.putText(frame, class_name, (int(box.x1), int(box.y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                        
                        # Сохранение изображения и воспроизведение звука
                        self.save_image(frame, class_name)
                        self.play_sound(class_name)

            cv2.imshow("Detections", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Object Detection with YOLOv8")
    parser.add_argument("--source", type=str, default="0",
                        help="Source of video. Can be camera index, video file path, or RTSP/HTTP URL")
    args = parser.parse_args()

    # Замените на свои токен и chat_id
    telegram_token = '7535382168:AAHLnaloofQO4xGpSoiXqAdOYL3-3Ip9COM'
    chat_id = '-1002496545090'
    
    detector = ObjectDetection(telegram_token, chat_id)
    detector.detect_objects(args.source)


if __name__ == "__main__":
    main()
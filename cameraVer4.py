import cv2  # Импорт библиотеки OpenCV для работы с видео и изображениями
import torch  # Импорт библиотеки PyTorch для работы с моделями глубокого обучения
from ultralytics import YOLO  # Импортирует класс YOLO из библиотеки Ultralytics для детекции объектов
import numpy as np  # Импорт библиотеки NumPy для работы с массивами
from datetime import datetime  # Импорт модуля datetime для работы с датой и временем
import os  # Импорт модуля os для взаимодействия с файловой системой
import argparse  # Импорт модуля argparse для обработки аргументов командной строки
from playsound import playsound  # Импорт функции playsound для воспроизведения звуковых файлов
import threading  # Импорт модуля threading для работы с потоками
import time  # Импорт модуля time для работы со временем

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InputFile, FSInputFile
from aiogram.filters import Command


# Telegram Bot API Token and Chat ID
API_TOKEN = '7535382168:AAHLnaloofQO4xGpSoiXqAdOYL3-3Ip9COM'  # Замените на токен вашего бота
CHAT_ID = '-1002496545090' 

class ObjectDetection:
    def __init__(self):
        # Выбор устройства для вычислений: используем CUDA, если доступно, иначе - CPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'  
        
        # Загрузка предобученной модели YOLO
        self.model = YOLO('D:/newProjectYOLOVer2/runs/detect/train/weights/best.pt').to(self.device)
        
        # Получение списка классов, использующихся в модели
        self.classes = self.model.names

        # Параметры для отправки сообщений в Telegram
       
        
        # Папки для сохранения видео и изображений
        self.output_dir = "D:/VideoToPython/recorded_videos/"
        self.save_images_dir = "D:/VideoToPython/saved_images/"
        
        # Создание директорий, если они не существуют
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(self.save_images_dir):
            os.makedirs(self.save_images_dir)
        
        # Параметры для фильтрации результатов детекции
        self.conf_threshold = 0.5  # Порог уверенности для детекции
        self.iou_threshold = 0.45  # Порог IoU для объединения боксов
        
        # Словарь для отслеживания последнего времени воспроизведения звуков
        self.last_sound_time = {}
        self.sound_cooldown = 3  # Время ожидания между воспроизведением звуков (в секундах)
        
        # Путь к звуковому файлу
        self.sound_file = "D:/VideoToPython/hazard-warning.mp3"

    async def send_photo_to_telegram(self, image_path):
        """Отправка изображения в Telegram"""
        try:
            photo = FSInputFile(image_path)
            await self.bot.send_photo(chat_id=CHAT_ID, photo=photo, caption='Обнаружен объект!')
        except Exception as e:
            print(f"Ошибка при отправке изображения в Telegram: {e}")

    def save_image(self, frame, class_name):
        """Сохранение изображения при обнаружении объекта"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Получение текущего времени как строки
        image_filename = f'{class_name}_{timestamp}.jpg'  # Форматирование имени файла с классом и временем
        image_path = os.path.join(self.save_images_dir, image_filename)  # Полный путь для сохранения изображения
        cv2.imwrite(image_path, frame)  # Сохранение изображения
        print(f"Сохранено изображение: {image_path}")  # Сообщение в консоль

        # Отправка изображения в Telegram
        asyncio.run(self.send_photo_to_telegram(image_path))


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

    def create_video_writer(self, video_cap, output_filename):
        """Создание объекта для записи видео"""
        # Получение параметров видео
        frame_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(video_cap.get(cv2.CAP_PROP_FPS))  # Количество кадров в секунду
        
        # Кодек для записи видео
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  
        
        # Полный путь для сохранения видео
        output_path = os.path.join(self.output_dir, output_filename)  
        
        # Возвращает объект записи видео
        return cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    def process_frame(self, frame):
        """Обработка одного кадра для распознавания объектов"""
        # Выполнение детекции объектов на кадре
        results = self.model(frame, conf=self.conf_threshold, iou=self.iou_threshold)  
        for result in results:
            boxes = result.boxes.cpu().numpy()  # Получение координат боксов в формате NumPy
            for box in boxes:
                # Извлечение координат бокса, ID класса и уверенности
                x1, y1, x2, y2 = box.xyxy[0].astype(int)
                class_id = int(box.cls[0])
                conf = box.conf[0]
                class_name = self.classes[class_id]  # Получение имени класса

                # Если объект является оружием, сохраняем изображение
                #if "weapon" in class_name.lower():  # Замените "weapon" на нужный класс - изминение - сохранение кадра при любом классе оружия 
                self.save_image(frame, class_name)

                # Воспроизведение звука при обнаружении объекта
                self.play_sound(class_name)

                # Рисование бокса вокруг обнаруженного объекта
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f'{class_name} {conf:.2f}'  # Форматирование ярлыка с именем класса и уверенности
                # Добавление текста на изображение
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame  # Возвращаем обработанный кадр

    def detect_objects(self, source):
        """Запуск детекции объектов"""
        # Создание объекта видеозахвата в зависимости от источника
        if source.isdigit():  # Если источник - это номер камеры
            cap = cv2.VideoCapture(int(source))
        elif source.startswith(('rtsp://', 'http://', 'https://')):  # Если источник - URL
            cap = cv2.VideoCapture(source)
        else:  # В остальных случаях - путь к файлу
            cap = cv2.VideoCapture(source)

        # Проверка на успешное открытие источника
        if not cap.isOpened():
            print("Ошибка при открытии источника видео")
            return

        # Формирование имени для выходного видео
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'detection_{timestamp}.avi'
        video_writer = self.create_video_writer(cap, output_filename)  # Создание объекта для записи видео

        # Основной цикл обработки кадров
        try:
            while True:
                ret, frame = cap.read()  # Чтение кадра
                if not ret:  # Если чтение прошло неудачно
                    print("Достигнут конец видео или произошла ошибка при чтении кадра")
                    break

                processed_frame = self.process_frame(frame)  # Обработка кадра
                video_writer.write(processed_frame)  # Запись обработанного кадра в файл
                cv2.imshow('Object Detection', processed_frame)  # Отображение обработанного кадра в окне

                # Выход при нажатии 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):  
                    break
        finally:
            cap.release()  # Освобождение видеозахвата
            video_writer.release()  # Освобождение видеозаписи
            cv2.destroyAllWindows()  # Закрытие всех окон OpenCV

def main():
    parser = argparse.ArgumentParser(description="Object Detection with YOLOv8")
    parser.add_argument("--source", type=str, default="0", # "0" - web камера, D:/newproectYOLO/new_YOLOv8_собств_детекция/video_test3.mp4
                        help="Source of video. Can be camera index, video file path, or RTSP/HTTP URL")
    args = parser.parse_args()

    detector = ObjectDetection()
    detector.detect_objects(args.source)

if __name__ == "__main__":
    main()
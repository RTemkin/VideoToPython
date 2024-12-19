import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
from sklearn.metrics import accuracy_score

# Функция для распознавания речи из аудиофайла
def recognize_speech_from_file(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='ru-RU')
            return text
        except sr.UnknownValueError:
            return "Не удалось распознать речь"
        except sr.RequestError as e:
            return f"Ошибка сервиса распознавания: {e}"

# Функция для оценки качества распознавания
def evaluate_model(predicted_text, actual_text):
    predicted_words = predicted_text.split()
    actual_words = actual_text.split()
    
    # Вычисляем точность
    accuracy = accuracy_score(actual_words, predicted_words)
    return accuracy

# Пример использования
if __name__ == "__main__":
    # Путь к аудиофайлу и его текстовое содержание
    audio_file_path = "dg.wav"
    expected_text = "Текст, который должен быть распознан"

    # Распознавание речи
    recognized_text = recognize_speech_from_file(audio_file_path)
    print("Распознанный текст:", recognized_text)

    # Оценка качества
    accuracy = evaluate_model(recognized_text, expected_text)
    print(f"Точность распознавания: {accuracy:.2f}")


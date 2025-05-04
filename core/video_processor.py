import time
import cv2
import numpy as np
from typing import Any, Optional, List, Dict
from models.yolo_model import YOLOModel  

class VideoProcessor:
    def __init__(self):
        # Инициализация атрибутов класса
        self.capture = None  # Объект видеозахвата
        self.is_running = False  # Флаг состояния потока
        self.yolo = YOLOModel()  # Инициализация модели YOLO
        self.current_frame = None  # Последний обработанный кадр
        self.detections = []  # Детекции на текущем кадре
        self.fps = 0  # Частота кадров
        self.frame_count = 0  # Счётчик обработанных кадров
        self.start_time = 0  # Время начала обработки

    def start_stream(self, source: Any = 0) -> bool:
        """
        Запускает видеопоток с заданного источника.
        По умолчанию используется веб-камера (source = 0).
        """
        try:
            self.capture = cv2.VideoCapture(source)
            if not self.capture.isOpened():
                raise ValueError("Не удалось открыть видеопоток")
            self.is_running = True
            self.frame_count = 0
            self.start_time = time.time()
            return True
        except Exception as e:
            print(f"Ошибка при запуске видеопотока: {e}")
            return False

    def process_frame(self) -> Optional[np.ndarray]:
        """
        Считывает и обрабатывает один кадр из видеопотока.
        Выполняет детекцию объектов и считает FPS.
        """
        if not self.is_running or self.capture is None:
            return None

        ret, frame = self.capture.read()
        if not ret:
            return None

        frame = cv2.resize(frame, (640, 480))  # Приведение кадра к фиксированному размеру
        results = self.yolo.detect(frame)  # Обнаружение объектов на кадре

        self.current_frame = results['frame']  # Кадр с наложенными рамками
        self.detections = results['detections']  # Сырые результаты детекции

        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        self.fps = self.frame_count / elapsed_time  # Расчет FPS

        return self.current_frame

    def stop_stream(self) -> None:
        """
        Останавливает видеопоток и освобождает ресурсы.
        """
        self.is_running = False
        if self.capture is not None:
            self.capture.release()
        self.capture = None

    def get_detections_info(self) -> List[Dict]:
        """
        Возвращает информацию о текущих детекциях в виде списка словарей.
        Каждый словарь содержит класс, уверенность и координаты рамки.
        """
        info = []
        for det in self.detections:
            x1, y1, x2, y2, conf, cls_id = det[:6]
            info.append({
                'class': self.yolo.classes[int(cls_id)],
                'confidence': float(conf),
                'bbox': [float(x1), float(y1), float(x2), float(y2)]
            })
        return info

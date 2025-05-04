import torch
import numpy as np
from ultralytics import YOLO
from typing import Dict, Any

class YOLOModel:
    def __init__(self, model_path: str = 'models/best.pt'):
        # Загружаем модель YOLOv8
        self.model = self.load_model(model_path)
        self.classes = self.model.names  # Список классов (названия объектов)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'  # Выбор устройства: GPU или CPU
        print(torch.cuda.is_available())  # Отладочный вывод — доступность CUDA

    def load_model(self, model_path: str):
        """
        Загружает модель YOLOv8 из указанного пути.
        """
        try:
            return YOLO(model_path)
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки модели YOLOv8: {e}")

    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Выполняет детекцию объектов на изображении.
        Возвращает кадр с аннотациями и данные о найденных объектах.
        """
        results = self.model(frame, verbose=False)[0]  # Получаем первый результат (batch size = 1)
        rendered_frame = results.plot()  # Отрисовка аннотаций на кадре

        return {
            'detections': results.boxes.data.cpu().numpy(),  # Детекции в виде массива NumPy
            'frame': rendered_frame  # Кадр с отрисованными боксами
        }

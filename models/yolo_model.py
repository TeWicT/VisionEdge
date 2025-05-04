import torch
import numpy as np
from ultralytics import YOLO
from typing import Dict, Any

class YOLOModel:
    def __init__(self, model_path: str = 'models/best.pt'):
        self.model = self.load_model(model_path)
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(torch.cuda.is_available())

    def load_model(self, model_path: str):
        try:
            return YOLO(model_path)
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки модели YOLOv8: {e}")

    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        results = self.model(frame, verbose=False)[0]
        rendered_frame = results.plot()
        return {
            'detections': results.boxes.data.cpu().numpy(),
            'frame': rendered_frame
        }

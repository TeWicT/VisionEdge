import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import torch
from typing import Optional, Dict, Any, List


class YOLOModel:
    """Класс для работы с моделью YOLO"""

    def __init__(self, model_path: str = 'best.pt'):
        self.model = self.load_model(model_path)
        self.classes = self.model.names if hasattr(self.model, 'names') else []
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def load_model(self, model_path: str):
        """Загружает модель YOLO"""
        try:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
            return model
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки модели YOLO: {e}")

    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """Выполняет детекцию объектов на кадре"""
        results = self.model(frame)
        return {
            'detections': results.xyxy[0].cpu().numpy(),
            'frame': np.squeeze(results.render())
        }


class VideoProcessor:
    """Класс для обработки видео с YOLO"""

    def __init__(self):
        self.capture = None
        self.is_running = False
        self.yolo = YOLOModel()
        self.current_frame = None
        self.detections = []
        self.fps = 0
        self.frame_count = 0
        self.start_time = 0

    def start_stream(self, source: Any = 0) -> bool:
        """Начинает захват видеопотока"""
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
        """Обрабатывает текущий кадр"""
        if not self.is_running or self.capture is None:
            return None

        ret, frame = self.capture.read()
        if not ret:
            return None

        # Детекция объектов с помощью YOLO
        results = self.yolo.detect(frame)
        self.current_frame = results['frame']
        self.detections = results['detections']

        # Расчет FPS
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        self.fps = self.frame_count / elapsed_time

        return self.current_frame

    def stop_stream(self) -> None:
        """Останавливает видеопоток"""
        self.is_running = False
        if self.capture is not None:
            self.capture.release()
        self.capture = None

    def get_detections_info(self) -> List[Dict]:
        """Возвращает информацию об обнаруженных объектах"""
        info = []
        for det in self.detections:
            x1, y1, x2, y2, conf, cls_id = det[:6]
            info.append({
                'class': self.yolo.classes[int(cls_id)],
                'confidence': float(conf),
                'bbox': [float(x1), float(y1), float(x2), float(y2)]
            })
        return info



class VisionEdgeUI(tk.Tk):
    """Графический интерфейс управления"""

    def __init__(self):
        super().__init__()
        self.title("VisionEdge - Интерфейс управления")
        self.geometry("1000x700")

        self.video_processor = VideoProcessor()
        self.setup_ui()

        # Для отображения видео
        self.video_label = tk.Label(self)
        self.video_label.pack(side=tk.RIGHT, padx=10, pady=10)

        self.update_video()

    def setup_ui(self):
        """Настраивает элементы интерфейса"""
        # Основной фрейм для управления
        control_frame = ttk.LabelFrame(self, text="Управление", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Раздел "Операции"
        operations_frame = ttk.LabelFrame(control_frame, text="Операции", padding=10)
        operations_frame.pack(fill=tk.X, pady=5)

        ttk.Button(operations_frame, text="Старт", command=self.start_stream).pack(fill=tk.X)
        ttk.Button(operations_frame, text="Стоп", command=self.stop_stream).pack(fill=tk.X)
        ttk.Button(operations_frame, text="Снимок", command=self.take_snapshot).pack(fill=tk.X)

        # Раздел "Информация"
        info_frame = ttk.LabelFrame(control_frame, text="Информация", padding=10)
        info_frame.pack(fill=tk.X, pady=5)

        self.info_text = tk.Text(info_frame, height=10, width=30)
        self.info_text.pack()

        # Раздел "Настройки"
        settings_frame = ttk.LabelFrame(control_frame, text="Настройки", padding=10)
        settings_frame.pack(fill=tk.X, pady=5)

        ttk.Label(settings_frame, text="Источник видео:").pack(anchor=tk.W)
        self.source_var = tk.StringVar(value="0")
        ttk.Entry(settings_frame, textvariable=self.source_var).pack(fill=tk.X)

        # Раздел "Дополнительно"
        advanced_frame = ttk.LabelFrame(control_frame, text="Дополнительно", padding=10)
        advanced_frame.pack(fill=tk.X, pady=5)

        ttk.Button(advanced_frame, text="Фонд", command=self.show_fond).pack(fill=tk.X)
        ttk.Button(advanced_frame, text="Интернет", command=self.show_internet).pack(fill=tk.X)
        ttk.Button(advanced_frame, text="Вариант", command=self.show_variant).pack(fill=tk.X)
        ttk.Button(advanced_frame, text="Технические", command=self.show_technical).pack(fill=tk.X)

    def start_stream(self):
        """Запускает видеопоток"""
        source = self.source_var.get()
        if source.isdigit():
            source = int(source)

        if self.video_processor.start_stream(source):
            messagebox.showinfo("Информация", "Видеопоток успешно запущен")
        else:
            messagebox.showerror("Ошибка", "Не удалось запустить видеопоток")

    def stop_stream(self):
        """Останавливает видеопоток"""
        self.video_processor.stop_stream()
        messagebox.showinfo("Информация", "Видеопоток остановлен")

    def take_snapshot(self):
        """Делает снимок текущего кадра"""
        if self.video_processor.current_frame is not None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.jpg"
            cv2.imwrite(filename, cv2.cvtColor(self.video_processor.current_frame, cv2.COLOR_RGB2BGR))
            messagebox.showinfo("Информация", f"Снимок сохранен как {filename}")

    def update_video(self):
        """Обновляет отображение видео"""
        frame = self.video_processor.process_frame()

        if frame is not None:
            # Конвертируем кадр для Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            # Обновляем информацию
            self.update_info()

        self.after(10, self.update_video)

    def update_info(self):
        """Обновляет информационную панель"""
        info = f"FPS: {self.video_processor.fps:.1f}\n\n"
        info += "Обнаруженные объекты:\n"

        for obj in self.video_processor.get_detections_info():
            info += f"- {obj['class']} ({obj['confidence']:.2f})\n"

        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)

    def show_fond(self):
        messagebox.showinfo("Фонд", "Информация о фонде")

    def show_internet(self):
        messagebox.showinfo("Интернет", "Настройки интернета")

    def show_variant(self):
        messagebox.showinfo("Вариант", "Выбор варианта")

    def show_technical(self):
        messagebox.showinfo("Технические", "Технические настройки")

    def on_closing(self):
        self.video_processor.stop_stream()
        self.destroy()


if __name__ == "__main__":
    app = VisionEdgeUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
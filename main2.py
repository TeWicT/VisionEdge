import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import torch
from typing import Optional, Dict, Any, List
from ultralytics import YOLO
from tkinter import filedialog
print(torch.version.cuda)
class YOLOModel:
    """Класс для работы с моделью YOLOv8"""

    def __init__(self, model_path: str = 'best.pt'):
        self.model = self.load_model(model_path)
        self.classes = self.model.names
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(torch.cuda.is_available())

    def load_model(self, model_path: str):
        """Загружает модель YOLOv8"""
        try:
            return YOLO(model_path)  # <-- используем Ultralytics API напрямую
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки модели YOLOv8: {e}")

    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """Выполняет детекцию объектов на кадре"""
        results = self.model(frame, verbose=False)[0]  # получаем первый результат
        rendered_frame = results.plot()
        return {
            'detections': results.boxes.data.cpu().numpy(),  # numpy-массив с box, conf, cls
            'frame': rendered_frame
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

        frame = cv2.resize(frame, (640, 480))  # или (416, 416)

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
        self.geometry("1920x1080")

        self.video_processor = VideoProcessor()
        self.setup_ui()

        # Для отображения видео
        self.video_label = tk.Label(self)
        self.video_label.pack(side=tk.RIGHT, padx=10, pady=10)

        # Ползунок перемотки
        self.seek_var = tk.DoubleVar()
        self.seek_slider = ttk.Scale(self, from_=0, to=100, orient="horizontal",
                                    variable=self.seek_var, command=self.on_seek)
        self.seek_slider.pack(side=tk.RIGHT, fill=tk.X, padx=10, pady=5)
        self.time_label = ttk.Label(self, text="00:00 / 00:00")
        self.time_label.pack(side=tk.RIGHT, padx=10)

        self.seek_slider.config(state="disabled")


        self.update_video()

    def format_time(self, seconds: float) -> str:
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        return f"{minutes:02}:{sec:02}"


    def on_seek(self, value):
        if self.video_processor.capture is not None and not self.video_processor.capture.get(cv2.CAP_PROP_FPS) == 0:
            frame_count = int(self.video_processor.capture.get(cv2.CAP_PROP_FRAME_COUNT))
            seek_frame = int(float(value) / 100 * frame_count)
            self.video_processor.capture.set(cv2.CAP_PROP_POS_FRAMES, seek_frame)


    def select_video_file(self):
        """Открывает диалог выбора видеофайла и подставляет путь в поле"""
        filetypes = [("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Выберите видеофайл", filetypes=filetypes)
        if filename:
            self.source_var.set(filename)


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
        ttk.Button(settings_frame, text="Выбрать файл", command=self.select_video_file).pack(fill=tk.X, pady=(5, 0))

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
            # Проверим, является ли источник видеофайлом
            if isinstance(source, str) and not source.startswith("rtsp") and not source.startswith("http"):
                self.seek_slider.config(state="normal")
                total_frames = int(self.video_processor.capture.get(cv2.CAP_PROP_FRAME_COUNT))
                if total_frames > 0:
                    self.seek_slider.config(to=100)
            else:
                self.seek_slider.config(state="disabled")

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

        # Обновим ползунок, если это видеофайл
        cap = self.video_processor.capture
        if cap is not None and self.seek_slider["state"] == "normal":
            pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
            total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if total > 0:
                self.seek_var.set(pos / total * 100)

        # Обновим текст времени
        # Обновим текст времени
        capture = self.video_processor.capture
        if capture is not None:
            fps = capture.get(cv2.CAP_PROP_FPS)
            if fps > 0:
                current_sec = capture.get(cv2.CAP_PROP_POS_FRAMES) / fps
                total_sec = capture.get(cv2.CAP_PROP_FRAME_COUNT) / fps
                self.time_label.config(
                    text=f"{self.format_time(current_sec)} / {self.format_time(total_sec)}"
                )


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
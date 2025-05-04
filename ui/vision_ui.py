import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import time
from core.video_processor import VideoProcessor

class VisionEdgeUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VisionEdge - Интерфейс управления")
        self.geometry("1920x1080")

        self.video_processor = VideoProcessor()
        self.setup_ui()  # Инициализация интерфейса

        # Метка для отображения видео
        self.video_label = tk.Label(self)
        self.video_label.pack(side=tk.RIGHT, padx=10, pady=10)

        # Слайдер перемотки видео
        self.seek_var = tk.DoubleVar()
        self.seek_slider = ttk.Scale(self, from_=0, to=100, orient="horizontal",
                                     variable=self.seek_var, command=self.on_seek)
        self.seek_slider.pack(side=tk.RIGHT, fill=tk.X, padx=10, pady=5)

        # Метка с временем
        self.time_label = ttk.Label(self, text="00:00 / 00:00")
        self.time_label.pack(side=tk.RIGHT, padx=10)
        self.seek_slider.config(state="disabled")

        self.update_video()  # Запуск обновления видео

    def format_time(self, seconds: float) -> str:
        # Форматирование времени в mm:ss
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        return f"{minutes:02}:{sec:02}"

    def on_seek(self, value):
        # Перемотка видео к заданной позиции
        cap = self.video_processor.capture
        if cap is not None and cap.get(cv2.CAP_PROP_FPS):
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            seek_frame = int(float(value) / 100 * frame_count)
            cap.set(cv2.CAP_PROP_POS_FRAMES, seek_frame)

    def select_video_file(self):
        # Выбор файла видео через диалог
        filetypes = [("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        filename = filedialog.askopenfilename(title="Выберите видеофайл", filetypes=filetypes)
        if filename:
            self.source_var.set(filename)

    def setup_ui(self):
        # Секция управления
        control_frame = ttk.LabelFrame(self, text="Управление", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Операции: старт, стоп, снимок
        operations_frame = ttk.LabelFrame(control_frame, text="Операции", padding=10)
        operations_frame.pack(fill=tk.X, pady=5)
        ttk.Button(operations_frame, text="Старт", command=self.start_stream).pack(fill=tk.X)
        ttk.Button(operations_frame, text="Стоп", command=self.stop_stream).pack(fill=tk.X)
        ttk.Button(operations_frame, text="Снимок", command=self.take_snapshot).pack(fill=tk.X)

        # Информация о детекциях
        info_frame = ttk.LabelFrame(control_frame, text="Информация", padding=10)
        info_frame.pack(fill=tk.X, pady=5)
        self.info_text = tk.Text(info_frame, height=10, width=30)
        self.info_text.pack()

        # Настройки источника видео
        settings_frame = ttk.LabelFrame(control_frame, text="Настройки", padding=10)
        settings_frame.pack(fill=tk.X, pady=5)
        ttk.Label(settings_frame, text="Источник видео:").pack(anchor=tk.W)
        self.source_var = tk.StringVar(value="0")
        ttk.Entry(settings_frame, textvariable=self.source_var).pack(fill=tk.X)
        ttk.Button(settings_frame, text="Выбрать файл", command=self.select_video_file).pack(fill=tk.X, pady=(5, 0))

    def start_stream(self):
        # Запуск видеопотока
        source = self.source_var.get()
        if source.isdigit():
            source = int(source)

        if self.video_processor.start_stream(source):
            # Включить перемотку, если это видеофайл
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
        # Остановка видеопотока
        self.video_processor.stop_stream()
        messagebox.showinfo("Информация", "Видеопоток остановлен")

    def take_snapshot(self):
        # Сохранение текущего кадра
        if self.video_processor.current_frame is not None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{timestamp}.jpg"
            cv2.imwrite(filename, cv2.cvtColor(self.video_processor.current_frame, cv2.COLOR_RGB2BGR))
            messagebox.showinfo("Информация", f"Снимок сохранен как {filename}")

    def update_video(self):
        # Обновление кадра в интерфейсе
        frame = self.video_processor.process_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            self.update_info()

        # Обновление положения слайдера и времени
        cap = self.video_processor.capture
        if cap is not None and self.seek_slider["state"] == "normal":
            pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
            total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if total > 0:
                self.seek_var.set(pos / total * 100)

        if cap is not None:
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps > 0:
                current_sec = cap.get(cv2.CAP_PROP_POS_FRAMES) / fps
                total_sec = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
                self.time_label.config(
                    text=f"{self.format_time(current_sec)} / {self.format_time(total_sec)}"
                )

        self.after(10, self.update_video)  # Циклическое обновление каждые 10 мс

    def update_info(self):
        # Отображение FPS и списка детекций
        info = f"FPS: {self.video_processor.fps:.1f}\n\nОбнаруженные объекты:\n"
        for obj in self.video_processor.get_detections_info():
            info += f"- {obj['class']} ({obj['confidence']:.2f})\n"
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info)

    def on_closing(self):
        # Закрытие приложения и остановка потока
        self.video_processor.stop_stream()
        self.destroy()

# utils/report.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def generate_report(detection_log, output_path):
    """
    Сгенерировать PDF отчет на основе detection_log.
    detection_log: list of tuples (time_sec, [classes])
    output_path: path to save pdf
    Отчёт включает объекты, которые были в кадре >2 секунд.
    """
    # Регистрируем шрифт с поддержкой кириллицы
    font_name = 'DejaVuSans'
    font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
    if not os.path.isfile(font_path):
        raise FileNotFoundError(f"TTF-файл шрифта не найден: {font_path}")
    pdfmetrics.registerFont(TTFont(font_name, font_path))

    # Сгруппируем интервалы присутствия по классу
    intervals = {}
    seen = {}
    prev_time = {}

    for time_sec, classes in detection_log:
        for cls in classes:
            if cls not in seen:
                seen[cls] = time_sec
        # Закрываем интервал для отсутствующих
        for cls in list(seen.keys()):
            if cls not in classes:
                start = seen.pop(cls)
                end = prev_time.get(cls, time_sec)
                if end - start >= 2:
                    intervals.setdefault(cls, []).append((start, end))
        prev_time = {cls: time_sec for cls in classes}

    # Закрываем оставшиеся интервалы
    for cls, start in seen.items():
        end = prev_time.get(cls, start)
        if end - start >= 2:
            intervals.setdefault(cls, []).append((start, end))

    # Создаем PDF
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont(font_name, 16)
    c.drawString(50, y, "Отчет по детекции объектов")
    y -= 30
    c.setFont(font_name, 12)

    for cls, ivs in intervals.items():
        c.drawString(50, y, f"Объект: {cls}")
        y -= 20
        for start, end in ivs:
            c.drawString(70, y, f"С {start:.2f}s до {end:.2f}s")
            y -= 15
        y -= 10
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont(font_name, 12)

    c.save()
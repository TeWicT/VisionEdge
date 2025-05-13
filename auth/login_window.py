import tkinter as tk
from tkinter import ttk, messagebox
from auth.auth import init_db, verify_user
from ui.vision_ui import VisionEdgeUI

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Авторизация VisionEdge")
        self.geometry("300x180")
        self.resizable(False, False)

        # Логин
        ttk.Label(self, text="Логин:").pack(pady=(20, 5))
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack()

        # Пароль
        ttk.Label(self, text="Пароль:").pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack()

        # Кнопка Войти
        ttk.Button(self, text="Войти", command=self.login).pack(pady=15)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        user = verify_user(username, password)
        if user:
            self.destroy()
            # Передаём user дальше (включая is_admin)
            app = VisionEdgeUI(user)
            app.protocol("WM_DELETE_WINDOW", app.on_closing)
            app.mainloop()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

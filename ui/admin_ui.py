# ui/admin_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from auth.auth import hash_password, init_db, DB_PATH
import sqlite3

class AdminUI(tk.Toplevel):
    """
    Окно админ-панели для создания и просмотра пользователей.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Админ-панель")
        self.geometry("400x300")
        self.resizable(False, False)

        # Форма создания пользователя
        frm = ttk.LabelFrame(self, text="Создать пользователя", padding=10)
        frm.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frm, text="Логин:").grid(row=0, column=0, sticky=tk.W)
        self.login_entry = ttk.Entry(frm)
        self.login_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)

        ttk.Label(frm, text="Пароль:").grid(row=1, column=0, sticky=tk.W, pady=(5,0))
        self.pass_entry = ttk.Entry(frm, show="*")
        self.pass_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=(5,0))

        self.is_admin_var = tk.BooleanVar()
        ttk.Checkbutton(frm, text="Админ", variable=self.is_admin_var).grid(row=2, column=0, columnspan=2, pady=(5,0))

        ttk.Button(frm, text="Добавить", command=self.add_user).grid(row=3, column=0, columnspan=2, pady=10)
        frm.columnconfigure(1, weight=1)

        # Список пользователей
        self.tree = ttk.Treeview(self, columns=("username", "is_admin"), show="headings")
        self.tree.heading("username", text="Логин")
        self.tree.heading("is_admin", text="Админ")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        self.refresh_users()

    def get_connection(self):
        return sqlite3.connect(DB_PATH)

    def refresh_users(self):
        # Очищаем и заполняем список
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT username, is_admin FROM users ORDER BY id ASC")
        for username, is_admin in cur.fetchall():
            self.tree.insert('', tk.END, values=(username, bool(is_admin)))
        conn.close()

    def add_user(self):
        username = self.login_entry.get().strip()
        password = self.pass_entry.get().strip()
        is_admin = int(self.is_admin_var.get())
        if not username or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль")
            return
        hashed = hash_password(password)
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                (username, hashed, is_admin)
            )
            conn.commit()
            messagebox.showinfo("Успех", f"Пользователь '{username}' создан")
            self.login_entry.delete(0, tk.END)
            self.pass_entry.delete(0, tk.END)
            self.is_admin_var.set(False)
            self.refresh_users()
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Такой логин уже существует")
        finally:
            conn.close()

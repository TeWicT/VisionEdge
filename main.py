from auth.auth import init_db
from auth.login_window import LoginWindow

if __name__ == "__main__":
    # Сначала инициализируем БД и дефолтного админа
    init_db()

    # Запускаем окно входа
    login = LoginWindow()
    login.mainloop()

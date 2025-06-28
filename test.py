import time
import tkinter as tk
import keyboard  # Установите библиотеку: pip install keyboard
from threading import Thread


def next_track():
    print("Следующий трек")
    # Здесь код для управления плеером


def prev_track():
    print("Предыдущий трек")
    # Здесь код для управления плеером


def play_pause():
    print("Пауза/Воспроизведение")
    # Здесь код для управления плеером


def setup_global_hotkeys():

    while True:
        event = keyboard.read_event().name
        print(repr(event))
        time.sleep(0.5)




# Запускаем обработчик горячих клавиш в отдельном потоке
hotkey_thread = Thread(target=setup_global_hotkeys, daemon=True)
hotkey_thread.start()

# Создаем графическое окно
root = tk.Tk()
root.title("Глобальные медиа клавиши")
root.geometry("400x300")

# Добавляем элементы интерфейса
label = tk.Label(
    root,
    text="Мультимедийные клавиши работают глобально:\n\n"
         "▶|❚❚ - Пауза/Плей\n"
         "⏮ - Предыдущий трек\n"
         "⏭ - Следующий трек\n\n"
         "Программа работает в фоновом режиме.\n"
         "Закройте это окно для завершения.",
    font=("Arial", 14),
    justify='left'
)
label.pack(pady=50)

# Добавляем кнопку для выхода
exit_button = tk.Button(root, text="Выход", command=root.destroy, font=("Arial", 12))
exit_button.pack(pady=10)

root.mainloop()







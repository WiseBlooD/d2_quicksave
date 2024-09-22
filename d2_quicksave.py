import pyautogui
import keyboard
import configparser
import time
import pystray
from pystray import MenuItem as item
from PIL import Image
import sys
import pygetwindow as gw
import tkinter as tk
from tkinter import messagebox

config = configparser.ConfigParser()
config.read('config.ini')

# Загрузка начальных настроек из config.ini
save_key = config['Settings'].get('save_key', 'shift+q')
save_name = config['Settings'].get('save_name', 'save_name')
window_title = config['Settings'].get('window_title', 'Disciples II')

paused = False  # Флаг для паузы

# Функция для сохранения
def quicksave():
    global paused
    if paused:
        print("Программа находится на паузе, сохранение не выполняется.")
        return  # Ничего не делаем, если пауза включена

    active_window = gw.getActiveWindow()
    if active_window and active_window.title == window_title:
        pyautogui.press('esc')
        time.sleep(0.2)
        pyautogui.press('s')
        time.sleep(0.2)
        pyautogui.typewrite(save_name, interval=0.1)
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.2)
        pyautogui.press('esc')          
        time.sleep(0.2)
        pyautogui.press('esc')       

# Переключение паузы и обновление иконки
def toggle_pause(icon, item):
    global paused
    paused = not paused
    status = "Paused" if paused else "Active"
    icon.title = f"Quicksave - {status}"  # Обновляем текст иконки

    if paused:
        icon.icon = Image.open('icon_paused.png')  # Меняем иконку на паузу
    else:
        icon.icon = Image.open('icon_active.png')  # Возвращаем стандартную иконку

    print(f"Режим переключен: {status}")

def open_settings(icon, item):
    global save_key, save_name, window_title
    
    # Создаем окно tkinter
    settings_window = tk.Tk()
    settings_window.title("Настройки")

    # Центрирование окна
    window_width = 300
    window_height = 150
    screen_width = settings_window.winfo_screenwidth()
    screen_height = settings_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    settings_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Обновляем состояние окна
    settings_window.update_idletasks()  
    settings_window.lift()  
    settings_window.focus_force()  

    def save_settings():
        global save_key, save_name, window_title

        new_save_key = entry_save_key.get()
        new_save_name = entry_save_name.get()
        new_window_title = entry_window_title.get()

        try:
            if new_save_key:
                keyboard.remove_hotkey(save_key)
                keyboard.add_hotkey(new_save_key, quicksave)
                save_key = new_save_key
                config['Settings']['save_key'] = save_key

            if new_save_name:
                save_name = new_save_name
                config['Settings']['save_name'] = save_name

            if new_window_title:
                window_title = new_window_title
                config['Settings']['window_title'] = window_title

            with open('config.ini', 'w') as configfile:
                config.write(configfile)

            messagebox.showinfo("Настройка", "Настройки успешно обновлены!")
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
        finally:
            settings_window.destroy()



    # Метки и поля ввода для каждого параметра
    label_save_key = tk.Label(settings_window, text="Горячая клавиша:")
    label_save_key.grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_save_key = tk.Entry(settings_window)
    entry_save_key.insert(0, save_key)
    entry_save_key.grid(row=0, column=1, padx=10, pady=5)

    label_save_name = tk.Label(settings_window, text="Имя сохранения:")
    label_save_name.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_save_name = tk.Entry(settings_window)
    entry_save_name.insert(0, save_name)
    entry_save_name.grid(row=1, column=1, padx=10, pady=5)

    label_window_title = tk.Label(settings_window, text="Название окна   :")
    label_window_title.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_window_title = tk.Entry(settings_window)
    entry_window_title.insert(0, window_title)
    entry_window_title.grid(row=2, column=1, padx=10, pady=5)

    # Кнопка для сохранения настроек
    save_button = tk.Button(settings_window, text="Сохранить", command=save_settings)
    save_button.grid(row=3, column=0, columnspan=2, pady=10)

    settings_window.mainloop()


# Выход из программы
def quit_program(icon, item):
    icon.stop()
    sys.exit()

# Загрузка изображения для иконки
def create_image(image_path):
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        print(f"Файл {image_path} не найден.")
        sys.exit(1)
    return image

# Настройка трея
def setup_tray():
    image = create_image('icon_active.png')  # Начальная иконка для активного режима
    menu = (
        item('Pause', toggle_pause),
        item('Настройка', open_settings),
        item('Выход', quit_program)
    )
    icon = pystray.Icon("quicksave", image, "Quicksave - Active", menu)
    icon.run()

keyboard.add_hotkey(save_key, quicksave)
setup_tray()

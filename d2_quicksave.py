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
from tkinter import filedialog, messagebox
import os
import pyperclip

config = configparser.ConfigParser()
config.read('config.ini')

# Загрузка начальных настроек из config.ini
save_key = config['Settings'].get('save_key', 'right_ctrl+e')
save_name = config['Settings'].get('save_name', 'save_name')
window_title = config['Settings'].get('window_title', 'Disciples II')
save_directory = config['Settings'].get('save_directory', '')
change_counter_key = config['Settings'].get('change_counter_key', 'ctrl+f7')
save_file_name = config['Settings'].get('save_file_name', '')
save_counter = int(config['Settings'].get('save_counter', 1))  # Счетчик для сохранений
use_counter_save = config['Settings'].getboolean('use_counter_save', True)  # Чекбокс по умолчанию активен
paused = False  # Флаг для паузы

def quicksave():
    global paused, save_counter, save_name, save_directory, use_counter_save
    if paused:
        print("Программа находится на паузе, сохранение не выполняется.")
        return

    active_window = gw.getActiveWindow()
    if not active_window or active_window.title != window_title:
         print("Не удалось определить активное окно игры!")
         return

    if active_window and active_window.title == window_title:
        if use_counter_save:
            # Сохранение по дням (с использованием счетчика)
            active_window.activate()
            save_file_name = f"{save_name}{save_counter}.sg"
            pyperclip.copy(save_name)
            keyboard.send('esc')
            time.sleep(0.4)
            keyboard.send('s')
            time.sleep(0.3)
            keyboard.send('ctrl+v')
            time.sleep(0.3)
            keyboard.write(str(save_counter), delay=0.1)
            time.sleep(0.4)
            keyboard.send('enter')
            time.sleep(0.3)
            keyboard.send('enter')
            time.sleep(0.3)
            keyboard.send('enter')
            time.sleep(0.3)
            keyboard.send('esc')   
            save_counter += 1
            config['Settings']['save_counter'] = str(save_counter)
        else:
            # Альтернативное сохранение (без счетчика)
            active_window.activate()
            pyperclip.copy(save_name)
            time.sleep(0.3)
            pyautogui.press('esc')
            time.sleep(0.4)
            keyboard.send('s')
            time.sleep(0.4)
            keyboard.press_and_release('ctrl+v')
            time.sleep(0.4)
            keyboard.send('enter')
            time.sleep(0.3)
            keyboard.send('enter')
            time.sleep(0.3)
            keyboard.send('enter')
            time.sleep(0.3)
            keyboard.send('esc')          


        with open('config.ini', 'w') as configfile:
            config.write(configfile)

# Функция для удаления всех сохранений
def delete_saves():
    global save_directory

    if not save_directory:
        messagebox.showerror("Ошибка", "Путь к директории с сохранениями не указан.")
        return

    if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все сохранения?"):
        try:
            for filename in os.listdir(save_directory):
                file_path = os.path.join(save_directory, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            messagebox.showinfo("Удаление", "Все сохранения успешно удалены.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении сохранений: {e}")

# Открыть диалоговое окно для выбора директории с сохранениями
def select_save_directory():
    global save_directory
    save_directory = filedialog.askdirectory(title="Выберите директорию с сохранениями")
    if save_directory:
        config['Settings']['save_directory'] = save_directory
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        directory_label.config(text=save_directory)  # Обновляем текст с выбранным путем
        messagebox.showinfo("Настройка", f"Путь к сохранениям: {save_directory}")
    else:
        directory_label.config(text="Укажите путь к папке с сохранениями")

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

# Окно изменения save_counter и save_name
def open_counter_window():
    counter_window = tk.Tk()
    counter_window.title("Изменение save_counter и save_name")
    
    window_width = 300
    window_height = 125
    screen_width = counter_window.winfo_screenwidth()
    screen_height = counter_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    counter_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Окно поверх других окон
    counter_window.attributes('-topmost', True)

    # Поля для изменения save_counter и save_name
    def save_changes():
        global save_counter, save_name
        save_counter = int(entry_save_counter.get())
        save_name = entry_save_name.get()

        config['Settings']['save_counter'] = str(save_counter)
        config['Settings']['save_name'] = save_name
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        counter_window.destroy()

    label_save_counter = tk.Label(counter_window, text="Счётчик сохранений:")
    label_save_counter.grid(row=0, column=0, padx=10, pady=5)
    entry_save_counter = tk.Entry(counter_window)
    entry_save_counter.insert(0, save_counter)
    entry_save_counter.grid(row=0, column=1, padx=10, pady=5)

    label_save_name = tk.Label(counter_window, text="Имя сохранения:")
    label_save_name.grid(row=1, column=0, padx=10, pady=5)
    entry_save_name = tk.Entry(counter_window)
    entry_save_name.insert(0, save_name)
    entry_save_name.grid(row=1, column=1, padx=10, pady=5)

    save_button = tk.Button(counter_window, text="Сохранить", command=save_changes)
    save_button.grid(row=2, column=0, columnspan=2, pady=10)

    counter_window.mainloop()

# Открытие окна настроек
def open_settings(icon, item):
    global save_key, save_name, window_title, change_counter_key, use_counter_save
    
    settings_window = tk.Tk()
    settings_window.title("Настройки")

    window_width = 425
    window_height = 400
    screen_width = settings_window.winfo_screenwidth()
    screen_height = settings_window.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    settings_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    settings_window.update_idletasks()  
    settings_window.lift()  
    settings_window.focus_force()  

    def save_settings():
        global save_key, save_name, window_title, change_counter_key, use_counter_save

        new_save_counter = entry_save_counter.get()
        new_save_key = entry_save_key.get()
        new_save_name = entry_save_name.get()
        new_window_title = entry_window_title.get()
        new_change_counter_key = entry_change_counter_key.get()

        try:
            if new_save_counter:
                global save_counter
                save_counter = int(new_save_counter)
                config['Settings']['save_counter'] = str(save_counter)

            if new_save_key:
                keyboard.remove_hotkey(save_key)
                keyboard.add_hotkey(new_save_key, quicksave)
                save_key = new_save_key
                config['Settings']['save_key'] = save_key

            if new_change_counter_key:
                keyboard.remove_hotkey(change_counter_key)
                keyboard.add_hotkey(new_change_counter_key, open_counter_window)
                change_counter_key = new_change_counter_key
                config['Settings']['change_counter_key'] = change_counter_key

            if new_save_name:
                save_name = new_save_name
                config['Settings']['save_name'] = save_name

            if new_window_title:
                window_title = new_window_title
                config['Settings']['window_title'] = window_title

            # Сохранение состояния чекбокса
            use_counter_save = use_counter_save_var.get()
            config['Settings']['use_counter_save'] = str(use_counter_save)

            with open('config.ini', 'w') as configfile:
                config.write(configfile)

            messagebox.showinfo("Настройка", "Настройки успешно обновлены!")
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
        finally:
            settings_window.destroy()

    # Отображение текущего значения save_counter
    label_save_counter = tk.Label(settings_window, text="Текущий счётчик сохранений:")
    label_save_counter.grid(row=0, column=0, padx=10, pady=5, sticky="e")
    entry_save_counter = tk.Entry(settings_window)
    entry_save_counter.insert(0, save_counter)
    entry_save_counter.grid(row=0, column=1, padx=10, pady=5)

    label_save_key = tk.Label(settings_window, text="Горячая клавиша для сохранения:")
    label_save_key.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    entry_save_key = tk.Entry(settings_window)
    entry_save_key.insert(0, save_key)
    entry_save_key.grid(row=1, column=1, padx=10, pady=5)

    label_change_counter_key = tk.Label(settings_window, text="Горячая клавиша для изменения счётчика:")
    label_change_counter_key.grid(row=2, column=0, padx=10, pady=5, sticky="e")
    entry_change_counter_key = tk.Entry(settings_window)
    entry_change_counter_key.insert(0, change_counter_key)
    entry_change_counter_key.grid(row=2, column=1, padx=10, pady=5)

    label_save_name = tk.Label(settings_window, text="Имя сохранения (ник оппонента):")
    label_save_name.grid(row=3, column=0, padx=10, pady=5, sticky="e")
    entry_save_name = tk.Entry(settings_window)
    entry_save_name.insert(0, save_name)
    entry_save_name.grid(row=3, column=1, padx=10, pady=5)

    label_window_title = tk.Label(settings_window, text="Название окна игры:")
    label_window_title.grid(row=4, column=0, padx=10, pady=5, sticky="e")
    entry_window_title = tk.Entry(settings_window)
    entry_window_title.insert(0, window_title)
    entry_window_title.grid(row=4, column=1, padx=10, pady=5)

    
    # Чекбокс для использования сохранения по дням
    use_counter_save_var = tk.BooleanVar(value=use_counter_save)
    checkbox_use_counter_save = tk.Checkbutton(settings_window, text="Использовать сохранение по дням", variable=use_counter_save_var)
    checkbox_use_counter_save.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    directory_label_text = "Укажите путь к папке с сохранениями" if not save_directory else save_directory
    directory_label = tk.Label(settings_window, text=directory_label_text, fg="gray")
    directory_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    button_select_dir = tk.Button(settings_window, text="Выбрать папку сохранений", command=select_save_directory)
    button_select_dir.grid(row=7, column=0, columnspan=2, pady=10)

    button_delete_saves = tk.Button(settings_window, text="Удалить все сохранения", command=delete_saves, bg="red", fg="white")
    button_delete_saves.grid(row=8, column=0, columnspan=2, pady=10)

    save_button = tk.Button(settings_window, text="Сохранить", command=save_settings)
    save_button.grid(row=9, column=0, columnspan=2, pady=10)

    settings_window.mainloop()

# Выход из программы
def quit_program(icon, item=None):
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
    image = create_image('icon_active.png')
    menu = (
        item('Pause', toggle_pause),
        item('Настройка', open_settings),
        item('Выход', quit_program)
    )
    icon = pystray.Icon("quicksave", image, "Quicksave - Active", menu)
    icon.run()

keyboard.add_hotkey(save_key, quicksave)
keyboard.add_hotkey(change_counter_key, open_counter_window)  # Добавляем хоткей для вызова окна изменения save_counter
keyboard.add_hotkey("ctrl+f8", delete_saves)  # Хоткей для удаления сохранений
setup_tray()


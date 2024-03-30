"""Программа для копирования (архивации) файлов с сохранением структуры папок"""

import os
import shutil
import time
import calendar
import win32com.client
import tkinter as tk
from tkinter import filedialog
from tkcalendar import DateEntry
from sys import exit
import babel.numbers  # нужно для перевода в exe

# Исключаем мультипроцессинг
proc_name = 'my_files_backup.exe'
my_pid = os.getpid()
wmi = win32com.client.GetObject('winmgmts:')
all_procs = wmi.InstancesOf('Win32_Process')
for proc in all_procs:
    if proc.Properties_("Name").Value == proc_name:
        proc_pid = proc.Properties_("ProcessID").Value
        if proc_pid != my_pid:
            os.kill(proc_pid, 9)

time_of_modified = os.path.getmtime  # Дата модификации
time_of_created = os.path.getctime  # Дата создания
created_or_modified = os.path.getatime  # дата последнего изменения, нужна для понимания отсутствия выбора в коде


def make_menu(w):
    """Команды вырезать/копировать/вставить"""
    global the_menu
    the_menu = tk.Menu(w, tearoff=0)
    the_menu.add_command(label="Вырезать")
    the_menu.add_command(label="Копировать")
    the_menu.add_command(label="Вставить")
    the_menu.add_command(label="Удалить")


def show_menu(e):
    """Контекстное меню с перечнем команд"""
    w = e.widget
    the_menu.entryconfigure("Вырезать", command=lambda: w.event_generate("<<Cut>>"))
    the_menu.entryconfigure("Копировать", command=lambda: w.event_generate("<<Copy>>"))
    the_menu.entryconfigure("Вставить", command=lambda: w.event_generate("<<Paste>>"))
    the_menu.entryconfigure("Удалить", command=lambda: w.event_generate("<<Clear>>"))
    the_menu.tk.call("tk_popup", the_menu, e.x_root, e.y_root)


archive_choise = 0
copy_choise = 0
zero_folder = 0
one_folder = 0
two_folders = 0
three_folders = 0
four_folders = 0


def error_window(xxx):
    """Окно с ошибкой"""
    er_text = f'\n{xxx}\n'
    er_win = tk.Toplevel(root)
    er_win.geometry('240x70')
    root.eval(f'tk::PlaceWindow {str(er_win)} center')
    photo_er = tk.PhotoImage(file='backup_logo.png')
    er_win.iconphoto(False, photo_er)
    er_win.resizable(False, False)
    er_win['bg'] = '#EEEEEE'
    er_win.wm_attributes('-alpha', 0.9)
    er_lab = tk.Label(er_win, text=er_text, font='Arial 12')
    er_lab.pack()
    er_win.after(2000, er_win.destroy)
    er_win.grid()


def final_window():
    """Окно окончания копирования"""
    er_win = tk.Toplevel()
    er_win.geometry('240x120')
    root.eval(f'tk::PlaceWindow {str(er_win)} center')
    photo_fin = tk.PhotoImage(file='backup_logo.png')
    er_win.iconphoto(False, photo_fin)
    er_win.resizable(False, False)
    er_win['bg'] = '#EEEEEE'
    er_win.wm_attributes('-alpha', 1)
    er_lab = tk.Label(er_win, text='\nКопирование завершено\n', font='Arial 12')
    er_lab.pack()
    er_win_but = tk.Button(er_win, text='OK', command=lambda: er_win.destroy(), width=8, height=2)
    er_win_but.pack()
    # er_win.after(3000, er_win.destroy)
    # er_win.grid()


def get_folder_path():
    """Кнопка выбора папки"""
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)


def get_folders_pathes():
    """Кнопка выбора папки"""
    folder_selected_from = filedialog.askdirectory()
    folders_pathes.set(folder_selected_from)


def copy_choise_func():
    """Выбор копирования"""
    global copy_choise, archive_choise
    copy_choise = 1,
    archive_choise = 0


def archive_choise_func():
    """Выбор архивации"""
    global copy_choise, archive_choise
    copy_choise = 0,
    archive_choise = 1


def time_of_modified_func():
    """По дате изменения"""
    global time_of_modified, created_or_modified
    created_or_modified = time_of_modified
    return created_or_modified


def time_of_created_func():
    """По дате создания"""
    global time_of_created, created_or_modified
    created_or_modified = time_of_created
    return created_or_modified


def zero_folder_func():
    """0 папок в глубину, просто копия"""
    global zero_folder, one_folder, two_folders, three_folders, four_folders
    zero_folder = 1
    one_folder = two_folders = three_folders = four_folders = 0


def one_folder_func():
    """1 папка в глубину"""
    global zero_folder, one_folder, two_folders, three_folders, four_folders
    one_folder = 1
    zero_folder = two_folders = three_folders = four_folders = 0


def two_folders_func():
    """2 папки в глубину"""
    global zero_folder, one_folder, two_folders, three_folders, four_folders
    two_folders = 1
    zero_folder = one_folder = three_folders = four_folders = 0


def three_folders_func():
    """2 папки в глубину"""
    global zero_folder, one_folder, two_folders, three_folders, four_folders
    three_folders = 1
    zero_folder = one_folder = two_folders = four_folders = 0


def four_folders_func():
    """2 папки в глубину"""
    global zero_folder, one_folder, two_folders, three_folders, four_folders
    four_folders = 1
    zero_folder = one_folder = two_folders = three_folders = 0


# Главное окно
root = tk.Tk()
root.title('Бэкап Моих Файлов')
root.geometry('800x460')
root.eval('tk::PlaceWindow . center')
photo = tk.PhotoImage(file='backup_logo.png')
root.iconphoto(False, photo)
root.resizable(False, False)
root['bg'] = '#EEEEEE'
root.wm_attributes('-alpha', 1)
make_menu(root)  # Сразу определим функцию с менюшками
# Главная надпись
label_name = tk.Label(text='Займёмся Бэкапом 😏', font="Arial 14 bold", foreground='#245175', background='#EEEEEE')
label_name.pack()

# Область под текст
frame_text = tk.Frame(root)
frame_text.place(relx=0.025, rely=0.08, relheight=0.50, relwidth=0.95)
label_from = tk.Label(frame_text, text='', font="Arial 12", background='#EEEEEE')
label_from.pack()
# Поле под текст (многострочное со скроллингом) с перечнем путей папок/файлов
text_area = tk.Text(frame_text, font='Arial 10')
with open('Files_Backup_path_from.txt') as f1:
    text_from = f1.read()  # Прочитаем файлик, чтобы вставить инфу из него в текстовое поле
    f1.close()
text_area.insert("1.0", text_from)
scrollbar = tk.Scrollbar(frame_text)
scrollbar.config(command=text_area.yview)
text_area.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_area.pack(expand=tk.YES, fill=tk.BOTH)
text_area.bind_class("Text", "<Button-3><ButtonRelease-3>", show_menu)  # Менюшка
# Сделаем кнопку выбора папки
folders_pathes = tk.StringVar()
but_find_1 = tk.Button(label_from, text="      Откуда      ",
                       command=lambda: [get_folders_pathes(), text_area.insert('end', f'{folders_pathes.get()}\n')])
but_find_1.pack()
# Область под текст и поле однострочного текста для пути копирования
frame_text_endpoint = tk.Frame(root, background='#EEEEEE')
frame_text_endpoint.place(relx=0.025, rely=0.61, relwidth=0.95)
label_where = tk.Label(frame_text_endpoint, text='', font="Arial 12", background='#EEEEEE')
label_where.pack()
# Сделаем строку и кнопку выбора папки
folder_path = tk.StringVar()
text_endpoint = tk.Entry(frame_text_endpoint, font='Arial 10', textvariable=folder_path)
with open('Files_Backup_path_to.txt') as f2:
    text_to = f2.read()  # Прочитаем файлик, чтобы вставить инфу из него в текстовое поле
    f2.close()
text_endpoint.insert(0, text_to)  # Вставим текст из файла
but_find_2 = tk.Button(text_endpoint, text="      Куда      ", command=get_folder_path)
but_find_2.pack(side=tk.RIGHT)
text_endpoint.pack(fill=tk.X)
text_endpoint.bind_class("Entry", "<Button-3><ButtonRelease-3>", show_menu)  # Менюшка

# Область под галочки и кнопочки №1
choise_frame_for_folders = tk.Frame(root, background='#EEEEEE')
choise_frame_for_folders.place(relx=0.025, rely=0.76, relheight=0.06, relwidth=0.95)

# Рабио батоны, выбор количества папок в глубину
folders_in = tk.IntVar()  # чтоб был пустой батон
choise_label_for_folders = tk.Label(choise_frame_for_folders, text='Выбери количество папок для анализа в глубину:   ')
choise_label_for_folders.pack(side=tk.LEFT)
btn_folder_4 = tk.Radiobutton(choise_frame_for_folders, variable=folders_in, value=5, text='4   ',
                              command=four_folders_func)
btn_folder_4.pack(side=tk.LEFT)
btn_folder_3 = tk.Radiobutton(choise_frame_for_folders, variable=folders_in, value=4, text='3   ',
                              command=three_folders_func)
btn_folder_3.pack(side=tk.LEFT)
btn_folder_2 = tk.Radiobutton(choise_frame_for_folders, variable=folders_in, value=3, text='2   ',
                              command=two_folders_func)
btn_folder_2.pack(side=tk.LEFT)
btn_folder_1 = tk.Radiobutton(choise_frame_for_folders, variable=folders_in, value=2, text='1   ',
                              command=one_folder_func)
btn_folder_1.pack(side=tk.LEFT)
btn_folder_0 = tk.Radiobutton(choise_frame_for_folders, variable=folders_in, value=1, text='0  (копия)',
                              command=zero_folder_func)
btn_folder_0.pack(side=tk.LEFT)
label_me = tk.Label(choise_frame_for_folders, text='     Design   by   DEMSTON  ', font=('Arial', 9), foreground='Gray',
                    height=2, width=28)
label_me.pack(side=tk.RIGHT)

# Область под галочки и кнопочки №2
choise_frame = tk.Frame(root, background='#EEEEEE')
choise_frame.place(relx=0.025, rely=0.84, relheight=0.1, relwidth=0.95)
# Чек-бокс, радио батон (копия/архив)
label_checkbox_copyarchive = tk.Label(choise_frame, background='#EEEEEE')
label_checkbox_copyarchive.pack(side=tk.LEFT)
copyarchive = tk.IntVar()  # чтоб был пустой батон
checkbox_archive = tk.Radiobutton(label_checkbox_copyarchive, value=2, variable=copyarchive, text='Заархивировать     ',
                                  command=archive_choise_func)
checkbox_archive.pack(side=tk.TOP)
checkbox_copy = tk.Radiobutton(label_checkbox_copyarchive, value=1, variable=copyarchive, text='Скопировать           ',
                               command=copy_choise_func)
checkbox_copy.pack(side=tk.BOTTOM)
label_behind_radio = tk.Label(choise_frame, background='#EEEEEE', height=3, width=1)
label_behind_radio.pack(side=tk.LEFT)
# Чек-бокс, радио батон (создание/изменение)
label_checkbox_madeedit = tk.Label(choise_frame, background='#EEEEEE')
label_checkbox_madeedit.pack(side=tk.LEFT)
madeedit = tk.IntVar()  # чтоб был пустой батон
checkbox_made = tk.Radiobutton(label_checkbox_madeedit, value=1, variable=madeedit, text='По дате создания            ',
                               command=time_of_created_func)
checkbox_made.pack(side=tk.TOP)
checkbox_edit = tk.Radiobutton(label_checkbox_madeedit, value=2, variable=madeedit, text='По дате изменения         ',
                               command=time_of_modified_func)
checkbox_edit.pack(side=tk.BOTTOM)
label_behind_date = tk.Label(choise_frame, background='#EEEEEE', height=3, width=1)
label_behind_date.pack(side=tk.LEFT)
# Дата
label_date_entry = tk.Label(choise_frame, background='#EEEEEE')
label_date_entry.pack(side=tk.LEFT)
label_date_text = tk.Label(label_date_entry, text='Изменено после:', background='#EEEEEE')
label_date_text.pack(side=tk.TOP)
date_entry = DateEntry(label_date_entry, width=10, bg="darkblue", fg="white", date_pattern='dd.mm.yyyy')
date_entry.pack(side=tk.BOTTOM)


def main_function():
    """Главная функция. Пишем/читаем текстовые файлы с путями. Потом копируем/архивируем по заданным параметрам"""
    global time_of_modified, archive_choise, copy_choise
    main_text = text_area.get("1.0", "end")
    target_text = text_endpoint.get()
    with open('Files_Backup_path_to.txt', 'w') as path_to_txt:
        path_to_txt.write(target_text)  # Запишем пути, куда будем копировать
        path_to_txt.close()
    with open('Files_Backup_path_from.txt', 'w') as path_from_txt:
        path_from_txt.writelines(main_text)  # Запишем пути, откуда будем копировать
        path_from_txt.close()
    with open('Files_Backup_path_from.txt') as path_from_txt:
        with open('Files_Backup_path_to.txt') as path_to_txt:
            target_dir_current = rf'{path_to_txt.read()}'
            # Исходим из выбора типа бэкапа: копия/архив
            if archive_choise == 0:
                target_dir = target_dir_current
            elif archive_choise == 1:
                target_dir = target_dir_current + '\\' + 'Archive_Temp'
                os.makedirs(target_dir)  # Создаём временную папку, которую заархивируем
            else:
                pass
            home_path = path_from_txt.read().splitlines()
            for i in home_path:  # Пройдёмся по каждой строке с путём папки и высчитаем разницу во времени
                home_dir = rf'{i}'
                time_delta = time.time() - calendar.timegm(time.strptime(f'{date_entry.get()} 00:00:00',
                                                                         '%d.%m.%Y %H:%M:%S'))
                # Поехали!
                for adress, dirs, files in os.walk(home_dir):
                    if adress == home_dir:
                        # Условие, которое препятствует проникновению программы в другие папки, кроме этой
                        for file in files:
                            file_path = os.path.join(home_dir, file)
                            if time.time() - created_or_modified(file_path) < time_delta:
                                shutil.copy(file_path, os.path.join(target_dir, file))
                        if zero_folder == 1 and one_folder == 0 and two_folders == 0 and three_folders == 0 \
                                and four_folders == 0:
                            shutil.copytree(home_dir, target_dir, dirs_exist_ok=True)
                        else:
                            for dir1 in dirs:  # Цикл 1
                                dir_path = os.path.join(home_dir, dir1)
                                if time.time() - created_or_modified(dir_path) < time_delta:
                                    dir1_copy = str(target_dir + '\\' + str(dir1))
                                    if os.path.isdir(dir1_copy):
                                        pass
                                    else:
                                        os.mkdir(dir1_copy)
                                    for adress2, dirs2, files2 in os.walk(dir_path):
                                        if adress2 == dir_path:
                                            for file2 in files2:
                                                file_path_2 = os.path.join(dir_path, file2)
                                                if time.time() - created_or_modified(file_path_2) < time_delta:
                                                    shutil.copy(file_path_2, os.path.join(dir1_copy, file2))
                                            if zero_folder == 0 and one_folder == 1 and two_folders == 0 and \
                                                    three_folders == 0 and four_folders == 0:
                                                shutil.copytree(dir_path, dir1_copy, dirs_exist_ok=True)
                                            else:
                                                for dir2 in dirs2:  # Цикл 2
                                                    dir_path_2 = os.path.join(dir_path, dir2)
                                                    if time.time() - created_or_modified(dir_path_2) < time_delta:
                                                        dir2_copy = str(
                                                            target_dir + '\\' + str(dir1) + '\\' + str(dir2))
                                                        if os.path.isdir(dir2_copy):
                                                            pass
                                                        else:
                                                            os.mkdir(dir2_copy)
                                                        for adress3, dirs3, files3 in os.walk(dir_path_2):
                                                            if adress3 == dir_path_2:
                                                                for file3 in files3:
                                                                    file_path_3 = os.path.join(dir_path_2, file3)
                                                                    if time.time() - created_or_modified(
                                                                            file_path_3) < time_delta:
                                                                        shutil.copy(file_path_3,
                                                                                    os.path.join(dir2_copy, file3))
                                                                if zero_folder == 0 and one_folder == 0 \
                                                                        and two_folders == 1 and three_folders == 0 and four_folders == 0:
                                                                    shutil.copytree(dir_path_2, dir2_copy, dirs_exist_ok=True)
                                                                else:
                                                                    for dir3 in dirs3:  # Цикл 3
                                                                        dir_path_3 = os.path.join(dir_path_2, dir3)
                                                                        if time.time() - created_or_modified(
                                                                                dir_path_3) < time_delta:
                                                                            dir3_copy = str(
                                                                                target_dir + '\\' + str(dir1) + '\\'
                                                                                + str(dir2) + '\\' + str(dir3))
                                                                            if os.path.isdir(dir3_copy):
                                                                                pass
                                                                            else:
                                                                                os.mkdir(dir3_copy)
                                                                            for adress4, dirs4, files4 in os.walk(
                                                                                    dir_path_3):
                                                                                if adress4 == dir_path_3:
                                                                                    for file4 in files4:
                                                                                        file_path_4 = os.path.join(
                                                                                            dir_path_3, file4)
                                                                                        if time.time() - created_or_modified(
                                                                                                file_path_4) < time_delta:
                                                                                            shutil.copy(file_path_4,
                                                                                                        os.path.join(
                                                                                                            dir3_copy,
                                                                                                            file4))
                                                                                    if zero_folder == 0 and one_folder == 0 and two_folders == 0 \
                                                                                            and three_folders == 1 and four_folders == 0:
                                                                                        shutil.copytree(dir_path_3,
                                                                                                        dir3_copy,
                                                                                                        dirs_exist_ok=True)
                                                                                    else:
                                                                                        for dir4 in dirs4:  # Цикл 4
                                                                                            dir_path_4 = os.path.join(
                                                                                                dir_path_3, dir4)
                                                                                            if time.time() - created_or_modified(
                                                                                                    dir_path_4) < time_delta:
                                                                                                dir4_copy = str(
                                                                                                    target_dir + '\\' + str(
                                                                                                        dir1) + '\\' + str(
                                                                                                        dir2 + '\\' + str(
                                                                                                            dir3)) + '\\' + str(
                                                                                                        dir4))
                                                                                                if os.path.isdir(
                                                                                                        dir4_copy):
                                                                                                    pass
                                                                                                else:
                                                                                                    os.mkdir(dir4_copy)
                                                                                                for adress5, dirs5, files5 in os.walk(
                                                                                                        dir_path_4):
                                                                                                    if adress5 == dir_path_4:
                                                                                                        for file5 in files5:
                                                                                                            file_path_5 = os.path.join(
                                                                                                                dir_path_4,
                                                                                                                file5)
                                                                                                            if time.time() - created_or_modified(
                                                                                                                    file_path_5) < time_delta:
                                                                                                                shutil.copy(
                                                                                                                    file_path_5,
                                                                                                                    os.path.join(
                                                                                                                        dir4_copy,
                                                                                                                        file5))
                                                                                                        shutil.copytree(
                                                                                                            dir_path_4,
                                                                                                            dir4_copy,
                                                                                                            dirs_exist_ok=True)
                path_to_txt.close()
            path_from_txt.close()
            if archive_choise == 1:  # Заархивируем при соответствующем условии
                arhive_name = target_dir_current + os.sep + 'My_Archive_' + time.strftime('%Y-%d-%m_%H%M%S')
                shutil.make_archive(arhive_name, 'zip', target_dir)
            else:
                pass
            if 'Archive_Temp' in target_dir:
                shutil.rmtree(target_dir)  # Удалим временную папку, которая заархивировалась


def main_of_the_main():
    """Соберём в кучу наши функции, предотвратим ошибки и скопируем"""
    if text_endpoint.get() in text_area.get("1.0", "end") or os.path.exists(text_endpoint.get()) is False:
        error_window('Неверный путь!')
    elif zero_folder == 0 and one_folder == 0 and two_folders == 0 and three_folders == 0 and four_folders == 0:
        error_window('Выбери глубину папок!')
    elif archive_choise == 0 and copy_choise == 0:
        error_window('Выбери тип бэкапа!')
    elif created_or_modified == os.path.getatime:
        error_window('Выбери создан или изменён!')
    else:
        main_function()
        final_window()


def save_func():
    """Функция сохранения путей в файл"""
    main_text = text_area.get("1.0", "end")
    target_text = text_endpoint.get()
    with open('Files_Backup_path_to.txt', 'w') as path_to_txt:
        path_to_txt.write(target_text)  # Запишем пути, куда будем копировать
        path_to_txt.close()
    with open('Files_Backup_path_from.txt', 'w') as path_from_txt:
        path_from_txt.writelines(main_text)  # Запишем пути, откуда будем копировать
        path_from_txt.close()


def clean_func():
    """Функция очистки полей и файла"""
    text_area.delete("1.0", 'end')
    text_endpoint.delete(0, 'end')
    main_text = text_area.get("1.0", "end")
    target_text = text_endpoint.get()
    with open('Files_Backup_path_to.txt', 'w') as path_to_txt:
        path_to_txt.write(target_text)  # Запишем пути, куда будем копировать
        path_to_txt.close()
    with open('Files_Backup_path_from.txt', 'w') as path_from_txt:
        path_from_txt.writelines(main_text)  # Запишем пути, откуда будем копировать
        path_from_txt.close()


# Кнопки
but_close = tk.Button(choise_frame, text='Выйти', font=('Arial', 12), height=2, width=6, command=exit)
but_close.pack(side=tk.RIGHT)
label_behind_but = tk.Label(choise_frame, background='#EEEEEE', height=3, width=1)
label_behind_but.pack(side=tk.RIGHT)
but_go = tk.Button(choise_frame, text='Go!', font=('Arial', 12, 'bold'), height=2, width=6, command=main_of_the_main)
but_go.pack(side=tk.RIGHT)
label_behind_but_2 = tk.Label(choise_frame, background='#EEEEEE', height=3, width=1)
label_behind_but_2.pack(side=tk.RIGHT)
but_save = tk.Button(choise_frame, text='💾', font=('Arial', 12), height=2, width=6, command=save_func)
but_save.pack(side=tk.RIGHT)
label_behind_but_3 = tk.Label(choise_frame, background='#EEEEEE', height=3, width=1)
label_behind_but_3.pack(side=tk.RIGHT)
but_clean = tk.Button(choise_frame, text='🗑', font=('Arial', 12), height=2, width=6, command=clean_func)
but_clean.pack(side=tk.RIGHT)

root.mainloop()

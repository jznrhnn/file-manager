import tkinter as tk
from tkinter import ttk, messagebox
import fileManager
import time
import threading
import os
import gettext
import configparser

# load the config file
config = configparser.ConfigParser()
config.read('config.ini')

current_language = config.get('language', 'language')

# 导入函数
locale_dir = os.path.join(os.path.dirname(__file__), 'language')
translator = gettext.translation(
    'messages', localedir=locale_dir, languages=[current_language])
translator.install()

t = translator.gettext


# 切换语言
def change_language():
    global current_language
    current_language = "en" if current_language == "cn" else "cn"

    # 修改配置值
    config['language']['language'] = current_language

    # 保存修改后的配置文件
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    alert = messagebox.askquestion(
        t("warnBoxMessage"), t("languageChangedWarn"))
    if alert == 'yes':
        # 关闭当前窗口
        root.destroy()


# 记录目录文件
def record_origin_game(replace=False):
    status_code, message = fileManager.record_origin_game(replace=replace)
    if status_code == fileManager.SUCCESS_CODE:
        alert = messagebox.showinfo("Command Executed", message)
    else:
        alert = messagebox.askquestion(
            # Do you want to replace it?
            t("warnBoxMessage"), message+"\n"+t("ReplaceWarn"), icon='warning')
        if alert == 'yes':
            record_origin_game(replace=True)

    initBox()


# 显示两个列表的区别
def show_difference():
    # show added files as green in listbox2
    global differences
    differences = fileManager.file_difference(
        origin_file_info, current_file_info)

    listbox2.delete(0, tk.END)

    for item in current_file_info.keys():
        if differences[item] == fileManager.FILE_STATUS.ADDED:
            listbox2.insert(tk.END, item)
            listbox2.itemconfig(tk.END, {'fg': 'green'})
        elif differences[item] == fileManager.FILE_STATUS.MODIFIED:
            listbox2.insert(tk.END, item)
            listbox2.itemconfig(tk.END, {'fg': 'orange'})
        else:
            listbox2.insert(tk.END, item)

    # show deleted files as red in listbox1
    listbox1.delete(0, tk.END)

    for item in origin_file_info.keys():
        if differences[item] == fileManager.FILE_STATUS.DELETED:
            listbox1.insert(tk.END, item)
            listbox1.itemconfig(tk.END, {'fg': 'red'})
        else:
            listbox1.insert(tk.END, item)

    # update overview label
    added_files = [key for key, value in differences.items(
    ) if value == fileManager.FILE_STATUS.ADDED]
    modified_files = [key for key, value in differences.items(
    ) if value == fileManager.FILE_STATUS.MODIFIED]
    removed_files = [key for key, value in differences.items(
    ) if value == fileManager.FILE_STATUS.DELETED]

    origin_file_size_msg = t("Origin File size")+": {origin_file_size}"
    current_file_msg = t("Current File size")+": {current_file_size}"
    added_files_msg = t("Files added")+": {added_files_count}"
    modified_files_msg = t("Files modified")+": {modified_files_count}"
    removed_files_msg = t("Files removed")+": {removed_files_count}"

    message = "\n".join([
        origin_file_size_msg.format(origin_file_size=len(origin_file_info)),
        current_file_msg.format(current_file_size=len(current_file_info)),
        added_files_msg.format(added_files_count=len(added_files)),
        modified_files_msg.format(modified_files_count=len(modified_files)),
        removed_files_msg.format(removed_files_count=len(removed_files))
    ])

    overview_label.config(text=message)


# 显示文件列表
def initBox():
    # clear listbox
    listbox1.delete(0, tk.END)
    listbox2.delete(0, tk.END)

    global origin_file_info
    global current_file_info

    origin_file_info = fileManager.load_file_info_json()
    current_file_info = fileManager.load_file_info()

    # 在listbox2中显示差集
    for item in origin_file_info.keys():
        listbox1.insert(tk.END, item)

    for item in current_file_info.keys():
        listbox2.insert(tk.END, item)


# 恢复原始文件
def restore_origin():
    move_result, move_message = fileManager.move_files(fileManager.config_game_path, fileManager.config_backup_path,
                                                       fileManager.config_original_list, True)
    if move_result == fileManager.SUCCESS_CODE:
        messagebox.showinfo(t("commandExecuted"),
                            t("filesRestored"))
    else:
        messagebox.showerror("Error", move_message)

    initBox()


# 恢复原始文件并显示进度
def restore_origin_with_progress():
    _, file_size = fileManager.move_files(fileManager.config_game_path, fileManager.config_backup_path,
                                          fileManager.config_original_list, backup=True, predict=True)
    move_files_thread = threading.Thread(target=restore_origin)
    move_files_thread.start()
    if file_size/1024/1024/1024 > 1:
        messagebox.showwarning(
            # The size of the files to be moved is too large, it may take a long time to complete the operation, please be patient
            t("warnBoxMessage"), t("largeFileSizeWarn"))
        while fileManager.get_folder_size(fileManager.config_backup_path) != 0:
            current_size = fileManager.get_folder_size(
                fileManager.config_backup_path)
            progress['value'] = current_size / file_size * 100
            progress.update()
            time.sleep(1)

    initBox()


def load_mod_files():
    move_result, move_message = fileManager.move_files(fileManager.config_backup_path, fileManager.config_game_path,
                                                       fileManager.config_original_list, False)
    if move_result == fileManager.SUCCESS_CODE:
        # "Command Executed",
        # "Origin game files restored"
        messagebox.showinfo(t("commandExecuted"), t("filesRestored"))
    else:
        messagebox.showerror("Error", move_message)

    initBox()


def load_mod_files_with_progress():
    _, file_size = fileManager.move_files(fileManager.config_backup_path,
                                          fileManager.config_game_path, backup=False, predict=True)
    move_files_thread = threading.Thread(target=load_mod_files)
    move_files_thread.start()
    if file_size/1024/1024/1024 > 1:
        messagebox.showwarning(
            t("warnBoxMessage"), t("largeFileSizeWarn"))
        while fileManager.get_folder_size(fileManager.config_backup_path) != 0:
            current_size = fileManager.get_folder_size(
                fileManager.config_backup_path)
            progress['value'] = (file_size - current_size) / file_size * 100
            progress.update()
            time.sleep(1)
        return

    initBox()


def mode():
    pass


def on_mouse_wheel(event):
    if event.delta < 0:
        direction = 1
    else:
        direction = -1
    listbox1.yview_scroll(direction, "units")
    listbox2.yview_scroll(direction, "units")


# file info
origin_file_info = {}
current_file_info = {}
differences = {}

# create window
root = tk.Tk()
root.title(t("projectTitle"))
root.geometry("700x480")  # Adjust window size

# create a frame for buttons
button_bar = tk.Frame(root)
button_bar.pack(side=tk.TOP, fill=tk.X)

# create a frame for listboxes
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

# create a scrollbar
scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# create listboxes
listbox1 = tk.Listbox(frame)
listbox2 = tk.Listbox(frame)


# create title labels
title_frame = tk.Frame(frame)
title_frame.pack(side=tk.TOP, fill=tk.X)
title_label1 = tk.Label(title_frame, text=t("listBoxTitle1"),
                        font=("Arial", 12, "bold"))
title_label1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

title_label2 = tk.Label(title_frame, text="listBoxTitle2",
                        font=("Arial", 12, "bold"))
title_label2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

initBox()

# create buttons
button_union = tk.Button(
    # Record Origin Game File
    button_bar, text=t("recordButton"), command=record_origin_game)
button_difference = tk.Button(
    # Show Difference
    button_bar, text=t("showDifference"), command=show_difference)
button_restore = tk.Button(
    # Restore Origin Game File
    button_bar, text=t("restoreOriginFile"), command=restore_origin_with_progress)
button_load_mods = tk.Button(
    # Load Mod File
    button_bar, text=t("loadFileButton"), command=load_mod_files_with_progress)
# TODO: add mode button, compare file with md5
button_mode = tk.Button(
    button_bar, text=t("languageButton")+"/"+current_language, command=change_language)

# Place buttons at the bottom of the window
button_union.pack(side=tk.LEFT, padx=5)
button_difference.pack(side=tk.LEFT, padx=5)
button_restore.pack(side=tk.LEFT, padx=5)
button_load_mods.pack(side=tk.LEFT, padx=5)
button_mode.pack(side=tk.LEFT, padx=5)

# Place listboxes on the left side of the window
listbox1.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
listbox2.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
listbox1.bind("<MouseWheel>", on_mouse_wheel)
listbox2.bind("<MouseWheel>", on_mouse_wheel)

# create a frame for progress bar
top_frame = tk.Frame(root)
top_frame.pack(side="top", fill="x", expand=True)

progress = ttk.Progressbar(
    top_frame, orient="horizontal", length=300, mode="determinate")
progress.pack(padx=10, pady=10, fill="x", expand=True)


# Create a label to display list overview
overview_frame = tk.Frame(root)
overview_frame.pack(side=tk.BOTTOM, fill=tk.X)

overview_label = tk.Label(overview_frame)

show_difference()

added_files = [key for key, value in differences.items(
) if value == fileManager.FILE_STATUS.ADDED]
modified_files = [key for key, value in differences.items(
) if value == fileManager.FILE_STATUS.MODIFIED]
removed_files = [key for key, value in differences.items(
) if value == fileManager.FILE_STATUS.DELETED]


overview_label.pack(side=tk.BOTTOM, pady=10)

# Run the window
root.mainloop()

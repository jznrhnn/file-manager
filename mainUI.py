import tkinter as tk
from tkinter import ttk, messagebox
import fileManager
import time
import threading


def record_origin_game(replace=False):
    status_code, message = fileManager.record_origin_game(replace=replace)
    if status_code == fileManager.SUCCESS_CODE:
        alert = messagebox.showinfo("Command Executed", message)
    else:
        alert = messagebox.askquestion(
            "Warnning", message+"\nDo you want to replace it?", icon='warning')
        if alert == 'yes':
            record_origin_game(replace=True)

    initBox()


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

    overview_label.config(
        text=f'''Origin File size: {len(origin_file_info)}    Current File: {len(current_file_info)}
    files added: {len(added_files)}
    files modified: {len(modified_files)}
    files removed: {len(removed_files)}'''
    )


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


def restore_origin():
    move_result, move_message = fileManager.move_files(fileManager.config_game_path, fileManager.config_backup_path,
                                                       fileManager.config_original_list, True)
    if move_result == fileManager.SUCCESS_CODE:
        messagebox.showinfo("Command Executed",
                            "Origin game files restored")
    else:
        messagebox.showerror("Error", move_message)

    initBox()


def restore_origin_with_progress():
    _, file_size = fileManager.move_files(fileManager.config_game_path, fileManager.config_backup_path,
                                          fileManager.config_original_list, backup=True, predict=True)
    move_files_thread = threading.Thread(target=restore_origin)
    move_files_thread.start()
    if file_size/1024/1024/1024 > 1:
        messagebox.showwarning(
            "Warnning", "The size of the files to be moved is too large, it may take a long time to complete the operation, please be patient")
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
        messagebox.showinfo("Command Executed",
                            "Origin game files restored")
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
            "Warnning", "The size of the files to be moved is too large, it may take a long time to complete the operation, please be patient")
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
root.title("Mode Manager")
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
title_label1 = tk.Label(title_frame, text="Origin File",
                        font=("Arial", 12, "bold"))
title_label1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

title_label2 = tk.Label(title_frame, text="Current File",
                        font=("Arial", 12, "bold"))
title_label2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

initBox()

# create buttons
button_union = tk.Button(
    button_bar, text="Record Origin Game File", command=record_origin_game)
button_difference = tk.Button(
    button_bar, text="Show Difference", command=show_difference)
button_restore = tk.Button(
    button_bar, text="Restore Origin Game File", command=restore_origin_with_progress)
button_load_mods = tk.Button(
    button_bar, text="Load Mod File", command=load_mod_files_with_progress)
# TODO: add mode button, compare file with md5
button_mode = tk.Button(
    button_bar, text="File Difference Mods (Default, Size and File Number)", command=restore_origin_with_progress)

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

import os
import configparser
import hashlib
import json
from enum import Enum
import shutil
import time
import gettext

# load the config file
config = configparser.ConfigParser()
config.read('config.ini')

ERROR_CODE = 500
SUCCESS_CODE = 200


class FILE_STATUS(Enum):
    SAME = 0
    ADDED = 1
    MODIFIED = 2
    DELETED = 3


config_game_path = config.get('game', 'game_path')

config_original_list = config.get('game', 'original_list')

config_backup_path = config.get('mods', 'backup_path')

current_language = config.get('language', 'language')

# 导入语言函数
locale_dir = os.path.join(os.path.dirname(__file__), 'language')
translator = gettext.translation(
    'messages', localedir=locale_dir, languages=[current_language])
translator.install()

t = translator.gettext

def calculate_file_hash(file_path, algorithm='MD5'):
    """calculate the hash value of the file
    Args:
        file_path (str): the path of the file
        algorithm (str, optional): the algorithm of the hash value. Defaults to 'MD5'.
    """
    if os.path.isdir(file_path):
        raise Exception("file path is a directory")
    with open(file_path, 'rb') as file:
        hash_function = hashlib.new(algorithm)
        while chunk := file.read(4096):
            hash_function.update(chunk)

    return hash_function.hexdigest()


# TODO: add a function to get the hash value of all files in the directory
def get_files_with_hashes(directory):
    """get the hash value of all files in the directory
    Args:
        directory (str): the path of the directory
    """
    files_with_hashes = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, directory)
            file_hash = calculate_file_hash(file_path)
            files_with_hashes[relative_path] = file_hash
    return files_with_hashes


def get_folder_size(folder_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            file_path = os.path.join(dirpath, f)
            total_size += os.path.getsize(file_path)
    return total_size


def load_file_info(dir_path=config_game_path, fullFile=False, hash=False):
    """load the file list from the file system
    Args:
        file_path (str): the path of the file
    """
    # Get the list of files in the directory
    file_records = {}
    file_list = os.listdir(dir_path)

    i = 0
    # get hash value of each file
    for file in file_list:
        file_path = os.path.join(dir_path, file)
        # record the directory files number and size when fullFile is False
        if os.path.isdir(file_path):
            file_records[file] = [{'file_len': len(os.listdir(file_path))}, {
                'dir_size': get_folder_size(file_path)}]
            if fullFile:
                get_files_with_hashes(file_path)
                # TODO
        else:
            if hash:
                file_records[file] = calculate_file_hash(file_path)
            else:
                file_records[file] = os.path.getsize(file_path)

        i += 1
        process = round(i/len(file_list)*100, 2), '%'

    return file_records


def record_origin_game(fullFile=False, replace=False):
    # Get the list of files in the directory
    file_records = {}
    file_list = os.listdir(config_game_path)

    file_records = load_file_info()

    # alert if file already exists
    if os.path.exists(config_original_list) and not replace:
        return ERROR_CODE, t("fileExistMessage")

    # save file list
    with open(config_original_list, 'w') as file:
        json.dump(file_records, file, indent=4)

    return SUCCESS_CODE, t("fileRecordSuccessMessage")


def load_file_info_json(file_path=config_original_list):
    """load the file list from the json file
    Args:
        file_path (str): the path of the file
    """
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as file:
        file_info = json.load(file)
    return file_info


def file_difference(file1, file2):
    """get the difference of two files
    Args:
        file1 (dict): the first file map
        file2 (dict): the second file map
    return:
        file_map (dict): the difference of two files, the key is the file name, 
        the value is the status of the file
    """
    # get the difference of two files
    added_list = set(file2).difference(file1)
    deleted_list = set(file1).difference(file2)
    modified_list = []
    origin_list = []

    # get the modified files
    intersection = set(file1).intersection(file2)
    for item in intersection:
        if file1[item] != file2[item]:
            modified_list.append(item)
        else:
            origin_list.append(item)

    file_map = {}
    for item in origin_list:
        file_map[item] = FILE_STATUS.SAME
    for item in added_list:
        file_map[item] = FILE_STATUS.ADDED
    for item in modified_list:
        file_map[item] = FILE_STATUS.MODIFIED
    for item in deleted_list:
        file_map[item] = FILE_STATUS.DELETED

    return file_map


def move_files(source_path, destination_path, file_record_path=None, backup=True, predict=False):
    start_time = time.time()
    source_files_info = load_file_info(source_path)

    size = 0
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    if backup:
        origin_files_info = load_file_info_json(file_record_path)

        # if destination file is not empty,return error
        if len(os.listdir(destination_path)) != 0:
            return ERROR_CODE, "destination path is not empty,pelase check it"
        # move files that are not in the origin file list to the destination path
        for file in source_files_info.keys():
            if file not in origin_files_info.keys():
                if predict:
                    size += get_folder_size(os.path.join(source_path, file))
                else:
                    shutil.move(os.path.join(source_path, file),
                                os.path.join(destination_path, file))
    else:
        for file in source_files_info.keys():
            if predict:
                size += get_folder_size(os.path.join(source_path, file))
            else:
                shutil.move(os.path.join(source_path, file),
                            os.path.join(destination_path, file))

    print(f"move files cost {time.time()-start_time} seconds")
    return SUCCESS_CODE, size

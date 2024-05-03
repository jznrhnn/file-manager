import unittest
import fileManager


class TestFileManager(unittest.TestCase):

    # 测试文件比较方法
    def test_difference(self):
        origin = {
            'a': 1,
            'b': 2,
            'c': 2,
            'd': 'test',
            'f': [1, 2],
            "x64": [
                {
                    "file_len": 3
                },
                {
                    "dir_size": 17060.356058120728
                }
            ],
        }
        current = {
            'a': 1,
            'b': 2,
            'c': 3,
            'e': 'test',
            'f': [1, 2],
            "x64": [
                {
                    "file_len": 4
                },
                {
                    "dir_size": 17060.356058120728
                }
            ],
        }
        difference_test = fileManager.file_difference(origin, current)

        self.assertEqual(difference_test['a'], fileManager.FILE_STATUS.SAME)
        self.assertEqual(difference_test['b'], fileManager.FILE_STATUS.SAME)
        self.assertEqual(difference_test['c'],
                         fileManager.FILE_STATUS.MODIFIED)
        self.assertEqual(difference_test['d'], fileManager.FILE_STATUS.DELETED)
        self.assertEqual(difference_test['e'], fileManager.FILE_STATUS.ADDED)
        self.assertEqual(difference_test['f'], fileManager.FILE_STATUS.SAME)
        self.assertEqual(difference_test['x64'],
                         fileManager.FILE_STATUS.MODIFIED)

    # 测试载入文件信息方法
    def test_load_file_info(self):
        files = fileManager.load_file_info('test/test0')
        self.assertEqual(files, {'test.dll': 0, 'test copy.dll': 0, 'test_dir': [{
            "file_len": 1
        },
            {
                "dir_size": 0
        }]})

    # 测试移动文件方法
    def test_move_files(self):
        source_path = 'test/test1'
        destination_path = 'test/test2'
        file_log_path = 'test/original_list.json'
        current_files_info = fileManager.load_file_info(source_path)
        # 将test1中的文件移动到test2中
        status,message=fileManager.move_files(source_path, destination_path, file_log_path)
        print(status,message)
        source_file = fileManager.load_file_info(source_path)
        record_file = fileManager.load_file_info_json(file_log_path)
        # record file should contain all files in source dir
        self.assertSetEqual(set(source_file.keys()) -
                            set(record_file.keys()), set())
        # moved files should equal to destination dir
        self.assertSetEqual(set(fileManager.load_file_info(destination_path).keys()), set(
            current_files_info.keys()) - set(fileManager.load_file_info_json(file_log_path).keys()))

    def test_move_files_without_record(self):
        source_path = 'test/test2'
        destination_path = 'test/test1'
        

        source_file = fileManager.load_file_info(source_path)

        fileManager.move_files(
            source_path, destination_path, backup=False)
        
        destination_file = fileManager.load_file_info(destination_path)

        # source file should be empty
        self.assertSetEqual(set(fileManager.load_file_info(source_path).keys()), set())
        # moved files should equal to destination dir
        self.assertSetEqual(set(source_file.keys())-set(destination_file.keys()), set())


if __name__ == '__main__':
    unittest.main()

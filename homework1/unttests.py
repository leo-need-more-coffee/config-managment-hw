import unittest
import os
import shutil
import tarfile
from emulator import ShellEmulator
from tkinter import Tk


class TestShellEmulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Создаем тестовую виртуальную файловую систему."""
        cls.test_tar_path = "test_virtual_fs.tar"
        cls.test_fs_root = "test_virtual_fs"
        os.makedirs(cls.test_fs_root, exist_ok=True)
        
        # Создаем тестовую файловую структуру
        os.makedirs(os.path.join(cls.test_fs_root, "dir1"), exist_ok=True)
        with open(os.path.join(cls.test_fs_root, "file1.txt"), "w") as f:
            f.write("Test file content")
        with open(os.path.join(cls.test_fs_root, "dir1", "file2.txt"), "w") as f:
            f.write("Another test file")
        
        # Архивируем тестовую файловую систему
        with tarfile.open(cls.test_tar_path, "w") as tar:
            tar.add(cls.test_fs_root, arcname=".")

    @classmethod
    def tearDownClass(cls):
        """Удаляем тестовую виртуальную файловую систему."""
        shutil.rmtree(cls.test_fs_root, ignore_errors=True)
        if os.path.exists(cls.test_tar_path):
            os.remove(cls.test_tar_path)

    def setUp(self):
        """Инициализация ShellEmulator перед каждым тестом."""
        self.root = Tk()
        self.shell = ShellEmulator(self.root, self.test_tar_path)
        self.shell.extract_virtual_fs()
        self.virtual_fs_path = "virtual_fs"

    def tearDown(self):
        """Очистка после каждого теста."""
        shutil.rmtree(self.virtual_fs_path, ignore_errors=True)
        self.root.destroy()

    def test_list_files(self):
        """Тест команды ls."""
        self.shell.current_path = "/"
        self.shell.list_files()
        output = self.shell.text_area.get("1.0", "end").strip()
        self.assertIn("file1.txt", output)
        self.assertIn("dir1", output)

    def test_change_directory(self):
        """Тест команды cd."""
        self.shell.current_path = "/"
        self.shell.change_directory("dir1")
        self.assertEqual(self.shell.current_path, "/dir1")
        self.shell.change_directory("..")
        self.assertEqual(self.shell.current_path, "/")

    def test_print_working_directory(self):
        """Тест команды pwd."""
        self.shell.current_path = "/dir1"
        self.shell.print_working_directory()
        output = self.shell.text_area.get("1.0", "end").strip()
        self.assertIn("/dir1", output)

    def test_uname_info(self):
        """Тест команды uname."""
        self.shell.uname_info()
        output = self.shell.text_area.get("1.0", "end").strip()
        self.assertIn("Linux", output)  # Написать имя ОС

    def test_copy_file(self):
        """Тест команды cp."""
        src = os.path.join(self.virtual_fs_path, "file1.txt")
        dest = os.path.join(self.virtual_fs_path, "file1_copy.txt")
        self.shell.copy_file(f"file1.txt file1_copy.txt")
        self.assertTrue(os.path.exists(dest))
        with open(dest, "r") as f:
            content = f.read()
        self.assertEqual(content, "Test file content")

    def test_copy_directory(self):
        """Тест копирования директории cp."""
        src = os.path.join(self.virtual_fs_path, "dir1")
        dest = os.path.join(self.virtual_fs_path, "dir1_copy")
        self.shell.copy_file(f"dir1 dir1_copy")
        self.assertTrue(os.path.exists(dest))
        self.assertTrue(os.path.exists(os.path.join(dest, "file2.txt")))

    def test_invalid_command(self):
        """Тест на неизвестную команду."""
        self.shell.entry.insert(0, "unknown_command")
        self.shell.execute_command(None)
        output = self.shell.text_area.get("1.0", "end").strip()
        self.assertIn("команда не найдена", output)


if __name__ == "__main__":
    unittest.main()

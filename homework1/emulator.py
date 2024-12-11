import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import tarfile
import sys
import argparse
import platform
import shutil


class ShellEmulator:
    def __init__(self, master, virtual_fs_path):
        self.master = master
        self.master.title("Shell Emulator")
        self.current_path = "/"
        self.history = []

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.username = os.getlogin()

        self.virtual_fs_path = virtual_fs_path

        self.label = tk.Label(master, text=f"{self.username}")
        self.label.pack(padx=10, pady=5)

        self.entry = tk.Entry(master)
        self.entry.pack(padx=10, pady=10, fill=tk.X)
        self.entry.bind("<Return>", self.execute_command)

        self.extract_virtual_fs()

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(description='Запуск эмулятора командной строки vshell.')
        parser.add_argument('virtual_fs', type=str, help='Путь к образу файловой системы (tar или zip).')

        args = parser.parse_args()

        if not os.path.exists(args.virtual_fs):
            parser.error(f"Файл виртуальной файловой системы '{args.virtual_fs}' не найден.")

        return args

    def extract_virtual_fs(self):
        if not os.path.exists(self.virtual_fs_path):
            messagebox.showerror("Ошибка", "Файл виртуальной файловой системы не найден.")
            return

        with tarfile.open(self.virtual_fs_path) as tar:
            tar.extractall(path="virtual_fs", filter=tarfile.data_filter)

    def execute_command(self, event):
        command = self.entry.get()
        self.history.append(command)

        command_dict = {
            "ls": self.list_files,
            "cd": lambda: self.change_directory(command[3:].strip()),
            "pwd": self.print_working_directory,
            "exit": self.master.quit,
            "uname": self.uname_info,
            "cp": lambda: self.copy_file(command[3:].strip())
        }

        cmd_func = command_dict.get(command.split()[0], None)

        if cmd_func:
            cmd_func()
        else:
            self.text_area.insert(tk.END, f"{self.username}: команда не найдена\n")

        self.entry.delete(0, tk.END)

    def list_files(self):
        try:
            files = os.listdir(f"virtual_fs{self.current_path}")
            output = "\n".join(files) if files else "Пустая директория\n"
            self.text_area.insert(tk.END, f"{output}\n")
        except FileNotFoundError:
            self.text_area.insert(tk.END, "Директория не найдена\n")
    
    def change_directory(self, path):
        if path == "..":
            if self.current_path != "/":
                parts = self.current_path.rstrip("/").split("/")
                parts.pop()
                self.current_path = "/".join(parts) or "/"
            return

        new_path = os.path.join(f"virtual_fs{self.current_path}", path)
        if os.path.isdir(new_path):
            self.current_path = new_path.replace("virtual_fs", "")
        else:
            self.text_area.insert(tk.END, "Директория не найдена\n")

    def print_working_directory(self):
        current_dir = f"{self.username}:{self.current_path}\n"
        self.text_area.insert(tk.END, current_dir)

    def uname_info(self):
        system_info = platform.uname()
        output = f"{system_info.system} {system_info.node} {system_info.release} {system_info.version} {system_info.machine}\n"
        self.text_area.insert(tk.END, output)

    def copy_file(self, args):
        try:
            src, dest = args.split()
            src_path = os.path.join(f"virtual_fs{self.current_path}", src)
            dest_path = os.path.join(f"virtual_fs{self.current_path}", dest)

            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy(src_path, dest_path)

            self.text_area.insert(tk.END, f"Копирование '{src}' в '{dest}' выполнено успешно.\n")
        except ValueError:
            self.text_area.insert(tk.END, "Ошибка: команда cp требует два аргумента: источник и назначение.\n")
        except FileNotFoundError:
            self.text_area.insert(tk.END, "Файл или директория не найдены.\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Ошибка при копировании: {str(e)}\n")


if __name__ == "__main__":
    args = ShellEmulator.parse_arguments()
    root = tk.Tk()
    app = ShellEmulator(root, args.virtual_fs)

    root.mainloop()

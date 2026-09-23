import os
import tempfile


class FileManager:

    @staticmethod
    def read_file(filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл {filepath} не знайдено.")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def save_file(filepath, content):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def read_binary(filepath: str) -> bytes:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Файл {filepath} не знайдено.")
        with open(filepath, 'rb') as f:
            return f.read()

    @staticmethod
    def save_binary(filepath: str, data: bytes) -> None:
        with open(filepath, 'wb') as f:
            f.write(data)

    @staticmethod
    def print_to_printer(content):
        if not content:
            raise ValueError("Немає даних для друку.")

        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.txt') as temp_file:
            temp_file.write(content)
            temp_filepath = temp_file.name

        try:
            import ctypes
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "print", temp_filepath, None, None, 0
            )
            if ret <= 32:
                raise OSError(f"Помилка ShellExecute під час друку (код: {ret})")
        finally:
            import threading
            def delayed_delete():
                import time
                time.sleep(5)
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
            threading.Thread(target=delayed_delete, daemon=True).start()

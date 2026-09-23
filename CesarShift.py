import os
import customtkinter as ctk
from tkinter import filedialog, messagebox

from CaesarCipher import CaesarCipher
from FileManager import FileManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BinaryFileDialog(ctk.CTkToplevel):

    def __init__(self, parent, default_key: str = "3"):
        super().__init__(parent)
        self.title("Шифрування файлу будь-якого формату")
        self.geometry("560x340")
        self.resizable(False, False)
        self.grab_set()

        self._input_path = ctk.StringVar()
        self._output_path = ctk.StringVar()
        self._key_var = ctk.StringVar(value=default_key)
        self._mode_var = ctk.StringVar(value="encrypt")

        ctk.CTkLabel(
            self, text="🗂  Побайтовий шифр Цезаря — будь-який формат",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(pady=(18, 2))
        ctk.CTkLabel(
            self,
            text="Кожен байт файлу зсувається на значення ключа (mod 256).\n"
                 "Підтримуються: зображення, PDF, DOCX, ZIP та будь-які інші формати.",
            font=ctk.CTkFont(size=11), text_color="gray70"
        ).pack(pady=(0, 14))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="x", padx=24)
        body.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(body, text="Режим:", anchor="w").grid(row=0, column=0, sticky="w", pady=6)
        mode_frame = ctk.CTkFrame(body, fg_color="transparent")
        mode_frame.grid(row=0, column=1, sticky="w", padx=(10, 0))
        ctk.CTkRadioButton(mode_frame, text="Зашифрувати",
                           variable=self._mode_var, value="encrypt").pack(side="left", padx=(0, 16))
        ctk.CTkRadioButton(mode_frame, text="Розшифрувати",
                           variable=self._mode_var, value="decrypt").pack(side="left")

        ctk.CTkLabel(body, text="Ключ (число):", anchor="w").grid(row=1, column=0, sticky="w", pady=6)
        ctk.CTkEntry(body, textvariable=self._key_var, width=120).grid(
            row=1, column=1, sticky="w", padx=(10, 0)
        )

        ctk.CTkLabel(body, text="Вхідний файл:", anchor="w").grid(row=2, column=0, sticky="w", pady=6)
        in_row = ctk.CTkFrame(body, fg_color="transparent")
        in_row.grid(row=2, column=1, sticky="ew", padx=(10, 0))
        in_row.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(in_row, textvariable=self._input_path).grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(in_row, text="…", width=36,
                      command=self._browse_input).grid(row=0, column=1, padx=(6, 0))

        ctk.CTkLabel(body, text="Вихідний файл:", anchor="w").grid(row=3, column=0, sticky="w", pady=6)
        out_row = ctk.CTkFrame(body, fg_color="transparent")
        out_row.grid(row=3, column=1, sticky="ew", padx=(10, 0))
        out_row.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(out_row, textvariable=self._output_path).grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(out_row, text="…", width=36,
                      command=self._browse_output).grid(row=0, column=1, padx=(6, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(18, 14))
        ctk.CTkButton(btn_row, text="Закрити", width=110,
                      fg_color="gray30", hover_color="gray20",
                      command=self.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_row, text="▶  Виконати", width=140,
                      command=self._run).pack(side="right")


    def _browse_input(self):
        path = filedialog.askopenfilename(title="Оберіть вхідний файл",
                                          filetypes=[("Усі файли", "*.*")])
        if path:
            self._input_path.set(path)
            if not self._output_path.get():
                base, ext = os.path.splitext(path)
                mode = self._mode_var.get()
                suffix = ".enc" if mode == "encrypt" else ".dec"
                self._output_path.set(base + suffix + ext)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(title="Зберегти результат як",
                                            filetypes=[("Усі файли", "*.*")])
        if path:
            self._output_path.set(path)

    def _run(self):
        src = self._input_path.get().strip()
        dst = self._output_path.get().strip()
        key_str = self._key_var.get().strip()

        if not src:
            messagebox.showwarning("Увага", "Вкажіть вхідний файл.", parent=self)
            return
        if not dst:
            messagebox.showwarning("Увага", "Вкажіть вихідний файл.", parent=self)
            return

        is_valid, key = CaesarCipher.validate_key(key_str)
        if not is_valid:
            messagebox.showerror("Помилка", "Ключ має бути цілим числом!", parent=self)
            return

        try:
            data = FileManager.read_binary(src)
            if self._mode_var.get() == "encrypt":
                result = CaesarCipher.encrypt_bytes(data, key)
                action = "зашифровано"
            else:
                result = CaesarCipher.decrypt_bytes(data, key)
                action = "розшифровано"
            FileManager.save_binary(dst, result)
            size_kb = len(result) / 1024
            messagebox.showinfo(
                "Успіх",
                f"Файл успішно {action}!\n"
                f"Розмір: {size_kb:.1f} КБ\n"
                f"Збережено: {dst}",
                parent=self
            )
            self.destroy()
        except FileNotFoundError as e:
            messagebox.showerror("Помилка", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Помилка", f"Під час обробки файлу сталася помилка:\n{e}", parent=self)


class BruteForceDialog(ctk.CTkToplevel):

    def __init__(self, parent, ciphertext, apply_callback):
        super().__init__(parent)
        self.title("Атака грубою силою — Всі варіанти розшифрування")
        self.geometry("820x560")
        self.resizable(True, True)
        self.grab_set()  # Модальне вікно

        self._apply_callback = apply_callback
        self._results = CaesarCipher.brute_force(ciphertext)
        self._selected_key = None

        header = ctk.CTkLabel(
            self,
            text="🔓  Груба сила — перебір усіх ключів",
            font=ctk.CTkFont(size=17, weight="bold"),
        )
        header.pack(pady=(16, 4))

        sub = ctk.CTkLabel(
            self,
            text="Оберіть рядок із вірогідним відкритим текстом, а потім натисніть «Застосувати».",
            font=ctk.CTkFont(size=12),
            text_color="gray70",
        )
        sub.pack(pady=(0, 10))

        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        col_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        col_frame.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 0))
        ctk.CTkLabel(col_frame, text="Ключ", width=50,
                     font=ctk.CTkFont(weight="bold"), anchor="center").pack(side="left")
        ctk.CTkLabel(col_frame, text="Розшифрований текст",
                     font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=(12, 0))

        self._scroll = ctk.CTkScrollableFrame(list_frame)
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self._scroll.grid_columnconfigure(1, weight=1)

        self._row_frames = []
        for idx, (key, text) in enumerate(self._results):
            self._build_row(idx, key, text)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 14))

        self._status_label = ctk.CTkLabel(
            btn_frame, text="Рядок не вибрано.",
            font=ctk.CTkFont(size=12), text_color="gray60", anchor="w"
        )
        self._status_label.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            btn_frame, text="Закрити", width=110,
            fg_color="gray30", hover_color="gray20",
            command=self.destroy
        ).pack(side="right", padx=(8, 0))

        self._apply_btn = ctk.CTkButton(
            btn_frame, text="✔  Застосувати", width=140,
            state="disabled",
            command=self._on_apply
        )
        self._apply_btn.pack(side="right")


    def _build_row(self, idx, key, text):
        bg_normal = ("gray85", "gray20") if idx % 2 == 0 else ("gray80", "gray17")
        bg_selected = ("#1f6aa5", "#1f6aa5")

        row = ctk.CTkFrame(self._scroll, fg_color=bg_normal, corner_radius=6)
        row.grid(row=idx, column=0, sticky="ew", pady=2)
        row.grid_columnconfigure(1, weight=1)

        key_lbl = ctk.CTkLabel(
            row, text=str(key), width=50,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="center",
        )
        key_lbl.grid(row=0, column=0, padx=(8, 4), pady=6)

        preview = text if len(text) <= 120 else text[:120] + "…"
        text_lbl = ctk.CTkLabel(
            row, text=preview,
            font=ctk.CTkFont(size=12),
            anchor="w", justify="left",
        )
        text_lbl.grid(row=0, column=1, sticky="ew", padx=(4, 8), pady=6)

        select_fn = lambda e, k=key, r=row, i=idx: self._select_row(k, r, i)
        for widget in (row, key_lbl, text_lbl):
            widget.bind("<Button-1>", select_fn)

        self._row_frames.append((row, bg_normal))

    def _select_row(self, key, selected_row, selected_idx):
        for i, (row, bg) in enumerate(self._row_frames):
            row.configure(fg_color=bg)

        selected_row.configure(fg_color=("#1f6aa5", "#1f6aa5"))
        self._selected_key = key
        self._apply_btn.configure(state="normal")
        self._status_label.configure(
            text=f"Вибрано ключ {key}  |  натисніть «Застосувати», щоб підставити текст.",
            text_color="gray90"
        )

    def _on_apply(self):
        if self._selected_key is None:
            return
        _, decrypted = self._results[self._selected_key - 1]
        self._apply_callback(self._selected_key, decrypted)
        self.destroy()


class CryptoAppGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Шифр Цезаря - Криптосистема")
        self.geometry("800x500")

        self.current_filepath = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(9, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Меню", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_create = ctk.CTkButton(self.sidebar, text="Створити новий", command=self.handle_create)
        self.btn_create.grid(row=1, column=0, padx=20, pady=10)

        self.btn_open = ctk.CTkButton(self.sidebar, text="Відкрити файл", command=self.handle_open)
        self.btn_open.grid(row=2, column=0, padx=20, pady=10)

        self.btn_save = ctk.CTkButton(self.sidebar, text="Зберегти файл", command=self.handle_save)
        self.btn_save.grid(row=3, column=0, padx=20, pady=10)

        self.btn_print = ctk.CTkButton(self.sidebar, text="Друк (Принтер)", command=self.handle_print)
        self.btn_print.grid(row=4, column=0, padx=20, pady=10)

        self.btn_binary = ctk.CTkButton(
            self.sidebar, text="🗂 Файл (будь-який)", command=self.handle_binary_file,
            fg_color="#0e7490", hover_color="#155e75"
        )
        self.btn_binary.grid(row=5, column=0, padx=20, pady=10)

        self.btn_brute = ctk.CTkButton(
            self.sidebar, text="🔓 Груба сила", command=self.handle_brute_force,
            fg_color="#7c3aed", hover_color="#5b21b6"
        )
        self.btn_brute.grid(row=6, column=0, padx=20, pady=10)

        self.btn_about = ctk.CTkButton(self.sidebar, text="Про розробника", command=self.handle_about)
        self.btn_about.grid(row=7, column=0, padx=20, pady=10)

        self.btn_exit = ctk.CTkButton(self.sidebar, text="Вихід", command=self.destroy, fg_color="red",
                                      hover_color="darkred")
        self.btn_exit.grid(row=10, column=0, padx=20, pady=20)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.crypto_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.crypto_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.key_label = ctk.CTkLabel(self.crypto_frame, text="Ключ (число):")
        self.key_label.pack(side="left", padx=(0, 10))

        self.key_entry = ctk.CTkEntry(self.crypto_frame, width=100)
        self.key_entry.pack(side="left", padx=(0, 20))
        self.key_entry.insert(0, "3")  # Значення за замовчуванням

        self.btn_encrypt = ctk.CTkButton(self.crypto_frame, text="Зашифрувати",
                                         command=lambda: self.handle_crypto('encrypt'))
        self.btn_encrypt.pack(side="left", padx=10)

        self.btn_decrypt = ctk.CTkButton(self.crypto_frame, text="Розшифрувати",
                                         command=lambda: self.handle_crypto('decrypt'))
        self.btn_decrypt.pack(side="left", padx=10)

        self.text_area = ctk.CTkTextbox(self.main_frame, wrap="word", font=ctk.CTkFont(size=14))
        self.text_area.grid(row=1, column=0, sticky="nsew")

    def get_text(self):
        return self.text_area.get("1.0", "end-1c")

    def set_text(self, text):
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", text)

    def handle_create(self):
        self.current_filepath = None
        self.set_text("")
        messagebox.showinfo("Створено", "Новий файл створено. Можете вводити текст.")

    def handle_open(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            try:
                content = FileManager.read_file(filepath)
                self.set_text(content)
                self.current_filepath = filepath
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{e}")

    def handle_save(self):
        text = self.get_text()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=os.path.basename(self.current_filepath) if self.current_filepath else "untitled.txt"
        )
        if filepath:
            try:
                FileManager.save_file(filepath, text)
                self.current_filepath = filepath
                messagebox.showinfo("Успіх", f"Файл успішно збережено!")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося зберегти файл:\n{e}")

    def handle_print(self):
        text = self.get_text()
        try:
            FileManager.print_to_printer(text)
            messagebox.showinfo("Друк", "Документ успішно відправлено на принтер!")
        except ValueError as ve:
            messagebox.showwarning("Увага", str(ve))
        except OSError as oe:
            messagebox.showerror("Помилка друку", f"Не вдалося виконати друк:\n{oe}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка під час друку:\n{e}")

    def handle_crypto(self, mode='encrypt'):
        text = self.get_text()

        if not CaesarCipher.validate_data(text):
            messagebox.showwarning("Увага", "Текстове поле порожнє!")
            return

        key_str = self.key_entry.get()
        is_valid, key = CaesarCipher.validate_key(key_str)

        if not is_valid:
            messagebox.showerror("Помилка", "Ключ має бути цілим числом!")
            return

        if mode == 'encrypt':
            result_text = CaesarCipher.encrypt(text, key)
            self.set_text(result_text)
            messagebox.showinfo("Успіх", "Текст успішно зашифровано!")
        else:
            result_text = CaesarCipher.decrypt(text, key)
            self.set_text(result_text)
            messagebox.showinfo("Успіх", "Текст успішно розшифровано!")

    def handle_binary_file(self):
        BinaryFileDialog(self, default_key=self.key_entry.get())

    def handle_brute_force(self):
        text = self.get_text()
        if not CaesarCipher.validate_data(text):
            messagebox.showwarning("Увага", "Текстове поле порожнє! Введіть шифротекст.")
            return

        def apply_result(key, decrypted_text):
            self.key_entry.delete(0, "end")
            self.key_entry.insert(0, str(key))
            self.set_text(decrypted_text)
            messagebox.showinfo(
                "Груба сила",
                f"Застосовано ключ {key}. Текст розшифровано та підставлено у поле."
            )

        BruteForceDialog(self, text, apply_result)

    def handle_about(self):
        info = (
            "Розробник: Тишко Даніїл Євгенович\n"
            "Студент спеціальності 'Інженерія програмного забезпечення'\n"
            "НТУУ «КПІ ім. Ігоря Сікорського»"
        )
        messagebox.showinfo("Про розробника", info)


if __name__ == "__main__":
    app = CryptoAppGUI()
    app.mainloop()
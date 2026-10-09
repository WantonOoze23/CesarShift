import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox

from CaesarCipher import CaesarCipher, TrithemiusCipher
from FileManager import FileManager

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def add_context_menu(widget):
    menu = tk.Menu(widget, tearoff=0, bg="#2b2b2b", fg="white", activebackground="#1f6aa5")
    menu.add_command(label="Копіювати", command=lambda: widget.event_generate("<<Copy>>"))
    menu.add_command(label="Вставити", command=lambda: widget.event_generate("<<Paste>>"))
    menu.add_command(label="Вирізати", command=lambda: widget.event_generate("<<Cut>>"))

    def show_menu(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    if hasattr(widget, '_textbox'):
        widget._textbox.bind("<Button-3>", show_menu)
    elif hasattr(widget, '_entry'):
        widget._entry.bind("<Button-3>", show_menu)
    else:
        widget.bind("<Button-3>", show_menu)


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

        ctk.CTkLabel(self, text="🗂  Побайтовий шифр Цезаря — будь-який формат",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(18, 2))
        ctk.CTkLabel(self,
                     text="Кожен байт файлу зсувається на значення ключа (mod 256).\nПідтримуються: зображення, PDF, DOCX, ZIP та будь-які інші формати.",
                     font=ctk.CTkFont(size=11), text_color="gray70").pack(pady=(0, 14))

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="x", padx=24)
        body.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(body, text="Режим:", anchor="w").grid(row=0, column=0, sticky="w", pady=6)
        mode_frame = ctk.CTkFrame(body, fg_color="transparent")
        mode_frame.grid(row=0, column=1, sticky="w", padx=(10, 0))
        ctk.CTkRadioButton(mode_frame, text="Зашифрувати", variable=self._mode_var, value="encrypt").pack(side="left",
                                                                                                          padx=(0, 16))
        ctk.CTkRadioButton(mode_frame, text="Розшифрувати", variable=self._mode_var, value="decrypt").pack(side="left")

        ctk.CTkLabel(body, text="Ключ (число):", anchor="w").grid(row=1, column=0, sticky="w", pady=6)
        key_entry = ctk.CTkEntry(body, textvariable=self._key_var, width=120)
        key_entry.grid(row=1, column=1, sticky="w", padx=(10, 0))
        add_context_menu(key_entry)

        ctk.CTkLabel(body, text="Вхідний файл:", anchor="w").grid(row=2, column=0, sticky="w", pady=6)
        in_row = ctk.CTkFrame(body, fg_color="transparent")
        in_row.grid(row=2, column=1, sticky="ew", padx=(10, 0))
        in_row.grid_columnconfigure(0, weight=1)
        in_entry = ctk.CTkEntry(in_row, textvariable=self._input_path)
        in_entry.grid(row=0, column=0, sticky="ew")
        add_context_menu(in_entry)
        ctk.CTkButton(in_row, text="…", width=36, command=self._browse_input).grid(row=0, column=1, padx=(6, 0))

        ctk.CTkLabel(body, text="Вихідний файл:", anchor="w").grid(row=3, column=0, sticky="w", pady=6)
        out_row = ctk.CTkFrame(body, fg_color="transparent")
        out_row.grid(row=3, column=1, sticky="ew", padx=(10, 0))
        out_row.grid_columnconfigure(0, weight=1)
        out_entry = ctk.CTkEntry(out_row, textvariable=self._output_path)
        out_entry.grid(row=0, column=0, sticky="ew")
        add_context_menu(out_entry)
        ctk.CTkButton(out_row, text="…", width=36, command=self._browse_output).grid(row=0, column=1, padx=(6, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(18, 14))
        ctk.CTkButton(btn_row, text="Закрити", width=110, fg_color="gray30", hover_color="gray20",
                      command=self.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btn_row, text="▶  Виконати", width=140, command=self._run).pack(side="right")

    def _browse_input(self):
        path = filedialog.askopenfilename(title="Оберіть вхідний файл", filetypes=[("Усі файли", "*.*")])
        if path:
            self._input_path.set(path)
            if not self._output_path.get():
                base, ext = os.path.splitext(path)
                suffix = ".enc" if self._mode_var.get() == "encrypt" else ".dec"
                self._output_path.set(base + suffix + ext)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(title="Зберегти результат як", filetypes=[("Усі файли", "*.*")])
        if path:
            self._output_path.set(path)

    def _run(self):
        src, dst, key_str = self._input_path.get().strip(), self._output_path.get().strip(), self._key_var.get().strip()
        if not src or not dst:
            messagebox.showwarning("Увага", "Вкажіть файли.", parent=self)
            return
        is_valid, key = CaesarCipher.validate_key(key_str)
        if not is_valid:
            messagebox.showerror("Помилка", "Ключ має бути цілим числом!", parent=self)
            return
        try:
            data = FileManager.read_binary(src)
            result = CaesarCipher.encrypt_bytes(data,
                                                key) if self._mode_var.get() == "encrypt" else CaesarCipher.decrypt_bytes(
                data, key)
            FileManager.save_binary(dst, result)
            messagebox.showinfo("Успіх", f"Файл оброблено!\nЗбережено: {dst}", parent=self)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Помилка", str(e), parent=self)


class BruteForceDialog(ctk.CTkToplevel):
    def __init__(self, parent, ciphertext, apply_callback):
        super().__init__(parent)
        self.title("Атака грубою силою — Цезар")
        self.geometry("820x560")
        self.grab_set()

        self._apply_callback = apply_callback
        self._results = CaesarCipher.brute_force(ciphertext)
        self._selected_key = None

        ctk.CTkLabel(self, text="🔓  Груба сила — перебір усіх ключів", font=ctk.CTkFont(size=17, weight="bold")).pack(
            pady=(16, 4))
        ctk.CTkLabel(self, text="Оберіть рядок із вірогідним відкритим текстом.", font=ctk.CTkFont(size=12),
                     text_color="gray70").pack(pady=(0, 10))

        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        self._scroll = ctk.CTkScrollableFrame(list_frame)
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self._scroll.grid_columnconfigure(1, weight=1)

        self._row_frames = []
        for idx, (key, text) in enumerate(self._results):
            self._build_row(idx, key, text)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 14))

        self._apply_btn = ctk.CTkButton(btn_frame, text="✔  Застосувати", state="disabled", command=self._on_apply)
        self._apply_btn.pack(side="right")
        ctk.CTkButton(btn_frame, text="Закрити", fg_color="gray30", hover_color="gray20", command=self.destroy).pack(
            side="right", padx=(8, 0))

    
    def _build_row(self, idx, key, text):
        bg = ("gray85", "gray20") if idx % 2 == 0 else ("gray80", "gray17")
        row = ctk.CTkFrame(self._scroll, fg_color=bg, corner_radius=6)
        row.grid(row=idx, column=0, sticky="ew", pady=2)
        row.grid_columnconfigure(1, weight=1)
        key_lbl = ctk.CTkLabel(row, text=str(key), width=50, font=ctk.CTkFont(size=13, weight="bold"))
        key_lbl.grid(row=0, column=0, padx=8, pady=6)
        text_lbl = ctk.CTkLabel(row, text=text[:120] + ("…" if len(text) > 120 else ""), font=ctk.CTkFont(size=12),
                                anchor="w", justify="left")
        text_lbl.grid(row=0, column=1, sticky="ew", padx=8, pady=6)
        select_fn = lambda e, k=key, r=row: self._select_row(k, r)
        for w in (row, key_lbl, text_lbl): w.bind("<Button-1>", select_fn)
        self._row_frames.append((row, bg))

    def _select_row(self, key, selected_row):
        for row, bg in self._row_frames: row.configure(fg_color=bg)
        selected_row.configure(fg_color=("#1f6aa5", "#1f6aa5"))
        self._selected_key = key
        self._apply_btn.configure(state="normal")

    def _on_apply(self):
        if self._selected_key is not None:
            _, decrypted = self._results[self._selected_key - 1]
            self._apply_callback(self._selected_key, decrypted)
            self.destroy()


class TrithemiusAttackDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Активна атака на шифр Тритеміуса")
        self.geometry("600x650")
        self.grab_set()

        ctk.CTkLabel(self, text="🎯 Активна атака (Вiдомий вiдкритий текст)",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(self, text="Введіть пару повідомлень для автоматичного знаходження ключів.",
                     font=ctk.CTkFont(size=12), text_color="gray70").pack(pady=(0, 10))

        ctk.CTkLabel(self, text="Незашифрований текст (Plaintext):").pack(anchor="w", padx=20)
        self.plain_text = ctk.CTkTextbox(self, height=100)
        self.plain_text.pack(fill="x", padx=20, pady=(0, 10))
        add_context_menu(self.plain_text)  # Додаємо контекстне меню

        ctk.CTkLabel(self, text="Зашифрований текст (Ciphertext):").pack(anchor="w", padx=20)
        self.cipher_text = ctk.CTkTextbox(self, height=100)
        self.cipher_text.pack(fill="x", padx=20, pady=(0, 15))
        add_context_menu(self.cipher_text)  # Додаємо контекстне меню

        self.btn_attack = ctk.CTkButton(self, text="Знайти ключі", command=self.run_attack)
        self.btn_attack.pack(pady=10)

        self.res_frame = ctk.CTkFrame(self)
        self.res_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.res_linear = ctk.CTkLabel(self.res_frame, text="Лінійний ключ: -", font=ctk.CTkFont(size=14))
        self.res_linear.pack(anchor="w", padx=10, pady=10)

        self.res_nonlinear = ctk.CTkLabel(self.res_frame, text="Нелінійний ключ: -", font=ctk.CTkFont(size=14))
        self.res_nonlinear.pack(anchor="w", padx=10, pady=10)

        self.res_keyword = ctk.CTkLabel(self.res_frame, text="Гасло: -", font=ctk.CTkFont(size=14))
        self.res_keyword.pack(anchor="w", padx=10, pady=10)

        ctk.CTkButton(self, text="Закрити", fg_color="gray30", hover_color="gray20", command=self.destroy).pack(
            pady=(0, 15))

    def run_attack(self):
        pt = self.plain_text.get("1.0", "end-1c").strip()
        ct = self.cipher_text.get("1.0", "end-1c").strip()

        if not pt or not ct:
            messagebox.showwarning("Увага", "Заповніть обидва поля!", parent=self)
            return
        if len(pt) != len(ct):
            messagebox.showwarning("Увага", "Довжина текстів повинна збігатися!", parent=self)
            return

        self.res_linear.configure(text="Лінійний ключ: Аналіз...")
        self.res_nonlinear.configure(text="Нелінійний ключ: Аналіз...")
        self.res_keyword.configure(text="Гасло: Аналіз...")
        self.update()

        results = TrithemiusCipher.active_attack(pt, ct)

        if "error" in results:
            messagebox.showerror("Помилка", results["error"], parent=self)
            return

        linear_text = f"A = {results['linear'][0]}, B = {results['linear'][1]}" if 'linear' in results else "Не знайдено"
        self.res_linear.configure(text=f"Лінійний ключ: {linear_text}")

        nonlinear_text = f"A = {results['nonlinear'][0]}, B = {results['nonlinear'][1]}, C = {results['nonlinear'][2]}" if 'nonlinear' in results else "Не знайдено"
        self.res_nonlinear.configure(text=f"Нелінійний ключ: {nonlinear_text}")

        keyword_text = results['keyword'] if 'keyword' in results else "Не знайдено"
        self.res_keyword.configure(text=f"Гасло: {keyword_text}")


class CryptoAppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Універсальна Криптосистема")
        self.geometry("1280x720")

        self.current_filepath = None
        self.cipher_mode_var = ctk.StringVar(value="caesar")
        self.trithemius_key_type_var = ctk.StringVar(value="linear")

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

        self.btn_binary = ctk.CTkButton(self.sidebar, text="🗂 Файл (Цезар)", command=self.handle_binary_file,
                                        fg_color="#0e7490", hover_color="#155e75")
        self.btn_binary.grid(row=5, column=0, padx=20, pady=10)

        self.btn_brute = ctk.CTkButton(self.sidebar, text="🔓 Груба сила (Цезар)", command=self.handle_brute_force,
                                       fg_color="#7c3aed", hover_color="#5b21b6")
        self.btn_brute.grid(row=6, column=0, padx=20, pady=10)

        self.btn_about = ctk.CTkButton(self.sidebar, text="Про розробника", command=self.handle_about)
        self.btn_about.grid(row=7, column=0, padx=20, pady=10)

        self.btn_exit = ctk.CTkButton(self.sidebar, text="Вихід", command=self.destroy, fg_color="red",
                                      hover_color="darkred")
        self.btn_exit.grid(row=10, column=0, padx=20, pady=20)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        self.algo_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.algo_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(self.algo_frame, text="Алгоритм:").pack(side="left", padx=(0, 10))
        self.algo_combo = ctk.CTkComboBox(self.algo_frame, values=["Шифр Цезаря", "Шифр Тритеміуса"],
                                          command=self.on_algo_change)
        self.algo_combo.pack(side="left", padx=(0, 20))

        self.crypto_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.crypto_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.trithemius_options_frame = ctk.CTkFrame(self.crypto_frame, fg_color="transparent")

        self.radio_linear = ctk.CTkRadioButton(self.trithemius_options_frame, text="Лінійне (A, B)",
                                               variable=self.trithemius_key_type_var, value="linear",
                                               command=self.update_key_ui)
        self.radio_linear.pack(side="left", padx=5)

        self.radio_nonlinear = ctk.CTkRadioButton(self.trithemius_options_frame, text="Нелінійне (A, B, C)",
                                                  variable=self.trithemius_key_type_var, value="nonlinear",
                                                  command=self.update_key_ui)
        self.radio_nonlinear.pack(side="left", padx=5)

        self.radio_keyword = ctk.CTkRadioButton(self.trithemius_options_frame, text="Гасло",
                                                variable=self.trithemius_key_type_var, value="keyword",
                                                command=self.update_key_ui)
        self.radio_keyword.pack(side="left", padx=5)

        self.key_input_container = ctk.CTkFrame(self.crypto_frame, fg_color="transparent")
        self.key_input_container.pack(side="left", padx=(0, 20))

        self.entry_caesar = ctk.CTkEntry(self.key_input_container, width=100)
        add_context_menu(self.entry_caesar)  # Додаємо контекстне меню

        self.entry_A = ctk.CTkEntry(self.key_input_container, width=50)
        add_context_menu(self.entry_A)  # Додаємо контекстне меню

        self.entry_B = ctk.CTkEntry(self.key_input_container, width=50)
        add_context_menu(self.entry_B)  # Додаємо контекстне меню

        self.entry_C = ctk.CTkEntry(self.key_input_container, width=50)
        add_context_menu(self.entry_C)  # Додаємо контекстне меню

        self.entry_keyword = ctk.CTkEntry(self.key_input_container, width=150)
        add_context_menu(self.entry_keyword)  # Додаємо контекстне меню

        self.entry_caesar.insert(0, "3")
        self.entry_A.insert(0, "1")
        self.entry_B.insert(0, "2")
        self.entry_C.insert(0, "3")
        self.entry_keyword.insert(0, "СЕКРЕТ")

        self.btn_encrypt = ctk.CTkButton(self.crypto_frame, text="Зашифрувати",
                                         command=lambda: self.handle_crypto('encrypt'))
        self.btn_encrypt.pack(side="left", padx=10)

        self.btn_decrypt = ctk.CTkButton(self.crypto_frame, text="Розшифрувати",
                                         command=lambda: self.handle_crypto('decrypt'))
        self.btn_decrypt.pack(side="left", padx=10)

        self.text_area = ctk.CTkTextbox(self.main_frame, wrap="word", font=ctk.CTkFont(size=14))
        self.text_area.grid(row=2, column=0, sticky="nsew")
        add_context_menu(self.text_area)

        self.update_key_ui()

    def on_algo_change(self, choice):
        if choice == "Шифр Тритеміуса":
            self.cipher_mode_var.set("trithemius")
            self.trithemius_options_frame.pack(side="left", before=self.key_input_container, padx=(0, 10))
            self.btn_binary.configure(state="disabled")

            self.btn_brute.configure(text="🎯 Атака (Тритеміус)", command=self.handle_trithemius_attack,
                                     fg_color="#b91c1c", hover_color="#991b1b")
        else:
            self.cipher_mode_var.set("caesar")
            self.trithemius_options_frame.pack_forget()
            self.btn_binary.configure(state="normal")

            self.btn_brute.configure(text="🔓 Груба сила (Цезар)", command=self.handle_brute_force, fg_color="#7c3aed",
                                     hover_color="#5b21b6")

        self.update_key_ui()

    def update_key_ui(self):
        for widget in self.key_input_container.winfo_children():
            widget.grid_forget()

        algo = self.cipher_mode_var.get()
        if algo == "caesar":
            ctk.CTkLabel(self.key_input_container, text="Ключ:").grid(row=0, column=0, padx=(0, 5))
            self.entry_caesar.grid(row=0, column=1)
        elif algo == "trithemius":
            mode = self.trithemius_key_type_var.get()
            if mode == "linear":
                ctk.CTkLabel(self.key_input_container, text="A:").grid(row=0, column=0, padx=(0, 2))
                self.entry_A.grid(row=0, column=1, padx=(0, 10))
                ctk.CTkLabel(self.key_input_container, text="B:").grid(row=0, column=2, padx=(0, 2))
                self.entry_B.grid(row=0, column=3)
            elif mode == "nonlinear":
                ctk.CTkLabel(self.key_input_container, text="A:").grid(row=0, column=0, padx=(0, 2))
                self.entry_A.grid(row=0, column=1, padx=(0, 10))
                ctk.CTkLabel(self.key_input_container, text="B:").grid(row=0, column=2, padx=(0, 2))
                self.entry_B.grid(row=0, column=3, padx=(0, 10))
                ctk.CTkLabel(self.key_input_container, text="C:").grid(row=0, column=4, padx=(0, 2))
                self.entry_C.grid(row=0, column=5)
            elif mode == "keyword":
                ctk.CTkLabel(self.key_input_container, text="Гасло:").grid(row=0, column=0, padx=(0, 5))
                self.entry_keyword.grid(row=0, column=1)

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
                self.set_text(FileManager.read_file(filepath))
                self.current_filepath = filepath
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося відкрити файл:\n{e}")

    def handle_save(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                                                initialfile=os.path.basename(
                                                    self.current_filepath) if self.current_filepath else "untitled.txt")
        if filepath:
            try:
                FileManager.save_file(filepath, self.get_text())
                self.current_filepath = filepath
                messagebox.showinfo("Успіх", f"Файл успішно збережено!")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося зберегти файл:\n{e}")

    def handle_print(self):
        try:
            FileManager.print_to_printer(self.get_text())
            messagebox.showinfo("Друк", "Документ успішно відправлено на принтер!")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка під час друку:\n{e}")

    def handle_crypto(self, mode='encrypt'):
        text, current_algo = self.get_text(), self.cipher_mode_var.get()
        if current_algo == "caesar":
            if not CaesarCipher.validate_data(text): return messagebox.showwarning("Увага", "Поле порожнє!")
            is_valid, key = CaesarCipher.validate_key(self.entry_caesar.get())
            if not is_valid: return messagebox.showerror("Помилка", "Ключ має бути цілим числом!")
            self.set_text(CaesarCipher.encrypt(text, key) if mode == 'encrypt' else CaesarCipher.decrypt(text, key))
            messagebox.showinfo("Успіх", "Успішно!")

        elif current_algo == "trithemius":
            key_type = self.trithemius_key_type_var.get()
            if key_type == "linear":
                key_str = f"{self.entry_A.get()} {self.entry_B.get()}"
            elif key_type == "nonlinear":
                key_str = f"{self.entry_A.get()} {self.entry_B.get()} {self.entry_C.get()}"
            elif key_type == "keyword":
                key_str = self.entry_keyword.get()

            if not TrithemiusCipher.validate_data(text): return messagebox.showwarning("Увага", "Поле порожнє!")
            is_valid, parsed_key = TrithemiusCipher.validate_key(key_type, key_str)

            if not is_valid: return messagebox.showerror("Помилка", "Некоректний ключ!")
            self.set_text(
                TrithemiusCipher.encrypt(text, key_type, parsed_key) if mode == 'encrypt' else TrithemiusCipher.decrypt(
                    text, key_type, parsed_key))
            messagebox.showinfo("Успіх", "Успішно!")

    def handle_binary_file(self):
        BinaryFileDialog(self, default_key=self.entry_caesar.get())

    def handle_brute_force(self):
        if not CaesarCipher.validate_data(self.get_text()): return messagebox.showwarning("Увага", "Поле порожнє!")
        BruteForceDialog(self, self.get_text(),
                         lambda k, dec: (self.entry_caesar.delete(0, "end"), self.entry_caesar.insert(0, str(k)),
                                         self.set_text(dec)))

    def handle_trithemius_attack(self):
        TrithemiusAttackDialog(self)

    def handle_about(self):
        messagebox.showinfo("Про розробника",
                            "Розробник: Тишко Даніїл Євгенович\nСтудент спеціальності 'Інженерія програмного забезпечення'\nНТУУ «КПІ ім. Ігоря Сікорського»")


if __name__ == "__main__":
    app = CryptoAppGUI()
    app.mainloop()
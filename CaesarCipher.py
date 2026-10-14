class CaesarCipher:

    EN_LOWER = "abcdefghijklmnopqrstuvwxyz"
    EN_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    UK_LOWER = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
    UK_UPPER = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"

    @staticmethod
    def validate_key(key_str):
        try:
            key = int(key_str)
            return True, key
        except ValueError:
            return False, None

    @staticmethod
    def validate_data(text):
        if not text or len(text.strip()) == 0:
            return False
        return True

    @classmethod
    def _shift_char(cls, char, key):
        if char in cls.EN_LOWER:
            n = len(cls.EN_LOWER)
            return cls.EN_LOWER[(cls.EN_LOWER.index(char) + key) % n]
        elif char in cls.EN_UPPER:
            n = len(cls.EN_UPPER)
            return cls.EN_UPPER[(cls.EN_UPPER.index(char) + key) % n]
        elif char in cls.UK_LOWER:
            n = len(cls.UK_LOWER)
            return cls.UK_LOWER[(cls.UK_LOWER.index(char) + key) % n]
        elif char in cls.UK_UPPER:
            n = len(cls.UK_UPPER)
            return cls.UK_UPPER[(cls.UK_UPPER.index(char) + key) % n]
        else:
            return char

    @classmethod
    def encrypt(cls, text, key):
        return "".join(cls._shift_char(c, key) for c in text)

    @classmethod
    def decrypt(cls, text, key):
        return "".join(cls._shift_char(c, -key) for c in text)

    @classmethod
    def brute_force(cls, ciphertext):
        results = []
        max_key = max(len(cls.EN_LOWER), len(cls.UK_LOWER))  # 34
        for key in range(1, max_key):
            decrypted = cls.decrypt(ciphertext, key)
            results.append((key, decrypted))
        return results

    @staticmethod
    def encrypt_bytes(data: bytes, key: int) -> bytes:
        shift = key % 256
        return bytes((b + shift) % 256 for b in data)

    @staticmethod
    def decrypt_bytes(data: bytes, key: int) -> bytes:
        shift = key % 256
        return bytes((b - shift) % 256 for b in data)


class TrithemiusCipher:

    EN_LOWER = "abcdefghijklmnopqrstuvwxyz"
    EN_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    UK_LOWER = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
    UK_UPPER = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"

    @staticmethod
    def validate_data(text):
        if not text or len(text.strip()) == 0:
            return False
        return True

    @staticmethod
    def validate_key(key_type, key_str):
        if key_type == 'linear':
            try:
                parts = key_str.replace(',', ' ').split()
                if len(parts) != 2: return False, None
                return True, (int(parts[0]), int(parts[1]))
            except ValueError:
                return False, None
        elif key_type == 'nonlinear':
            try:
                parts = key_str.replace(',', ' ').split()
                if len(parts) != 3: return False, None
                return True, (int(parts[0]), int(parts[1]), int(parts[2]))
            except ValueError:
                return False, None
        elif key_type == 'keyword':
            if not key_str or len(key_str.strip()) == 0: return False, None
            return True, key_str.strip()
        return False, None

    @classmethod
    def _get_alphabet(cls, char):
        if char in cls.EN_LOWER: return cls.EN_LOWER
        if char in cls.EN_UPPER: return cls.EN_UPPER
        if char in cls.UK_LOWER: return cls.UK_LOWER
        if char in cls.UK_UPPER: return cls.UK_UPPER
        return None

    @classmethod
    def _get_char_index(cls, char):
        alphabet = cls._get_alphabet(char)
        return alphabet.index(char) if alphabet else 0

    @classmethod
    def _calculate_shift(cls, p, key_type, parsed_key):
        if key_type == 'linear':
            A, B = parsed_key
            return A * p + B
        elif key_type == 'nonlinear':
            A, B, C = parsed_key
            return A * (p ** 2) + B * p + C
        elif key_type == 'keyword':
            keyword = parsed_key
            key_char = keyword[p % len(keyword)]
            return cls._get_char_index(key_char)
        return 0

    @classmethod
    def _process_text(cls, text, key_type, parsed_key, mode='encrypt'):
        result = []
        for p, char in enumerate(text):
            k = cls._calculate_shift(p, key_type, parsed_key)
            if mode == 'decrypt':
                k = -k

            alphabet = cls._get_alphabet(char)
            if alphabet:
                n = len(alphabet)
                result.append(alphabet[(alphabet.index(char) + k) % n])
            else:
                result.append(char)
        return "".join(result)

    @classmethod
    def encrypt(cls, text, key_type, parsed_key):
        return cls._process_text(text, key_type, parsed_key, mode='encrypt')

    @classmethod
    def decrypt(cls, text, key_type, parsed_key):
        return cls._process_text(text, key_type, parsed_key, mode='decrypt')

    @classmethod
    def active_attack(cls, plaintext, ciphertext):
        results = {}
        if not plaintext or not ciphertext or len(plaintext) != len(ciphertext):
            return {"error": "Тексти порожні або мають різну довжину!"}

        required_shifts = {}
        for p, (p_char, c_char) in enumerate(zip(plaintext, ciphertext)):
            alphabet = cls._get_alphabet(p_char)
            if alphabet:
                p_idx = alphabet.index(p_char)
                c_idx = alphabet.index(c_char)
                shift = (c_idx - p_idx) % len(alphabet)
                required_shifts[p] = (shift, len(alphabet))

        test_positions = list(required_shifts.items())[:3]

        linear_key = None
        for a in range(100):
            for b in range(100):
                match = True
                for p, (req_shift, alpha_len) in test_positions[:2]:
                    if (a * p + b) % alpha_len != req_shift:
                        match = False
                        break
                if match and cls.encrypt(plaintext, 'linear', (a, b)) == ciphertext:
                    linear_key = (a, b)
                    break
            if linear_key: break
        if linear_key: results['linear'] = linear_key

        nonlinear_key = None
        for a in range(35):
            for b in range(35):
                for c in range(35):
                    match = True
                    for p, (req_shift, alpha_len) in test_positions[:3]:
                        if (a * (p ** 2) + b * p + c) % alpha_len != req_shift:
                            match = False
                            break
                    if match and cls.encrypt(plaintext, 'nonlinear', (a, b, c)) == ciphertext:
                        nonlinear_key = (a, b, c)
                        break
                if nonlinear_key: break
            if nonlinear_key: break
        if nonlinear_key: results['nonlinear'] = nonlinear_key

        best_keyword = None
        max_len = min(50, len(plaintext))

        for L in range(1, max_len + 1):
            possible_keyword_en = ""
            possible_keyword_uk = ""
            valid_length = True

            for i in range(L):
                valid_char_en = None
                valid_char_uk = None
                has_letters = False

                for p, _ in required_shifts.items():
                    if p % L == i:
                        has_letters = True
                        break

                if not has_letters:
                    possible_keyword_en += 'A'
                    possible_keyword_uk += 'А'
                    continue

                for candidate in cls.EN_UPPER:
                    cand_idx = cls.EN_UPPER.index(candidate)
                    is_match = True
                    for p, (req_shift, alpha_len) in required_shifts.items():
                        if p % L == i:
                            if cand_idx % alpha_len != req_shift:
                                is_match = False
                                break
                    if is_match:
                        valid_char_en = candidate
                        break

                for candidate in cls.UK_UPPER:
                    cand_idx = cls.UK_UPPER.index(candidate)
                    is_match = True
                    for p, (req_shift, alpha_len) in required_shifts.items():
                        if p % L == i:
                            if cand_idx % alpha_len != req_shift:
                                is_match = False
                                break
                    if is_match:
                        valid_char_uk = candidate
                        break

                if valid_char_en is None and valid_char_uk is None:
                    valid_length = False
                    break
                else:
                    possible_keyword_en += valid_char_en if valid_char_en else '?'
                    possible_keyword_uk += valid_char_uk if valid_char_uk else '?'

            if valid_length:
                if cls.encrypt(plaintext, 'keyword', possible_keyword_en) == ciphertext or \
                   cls.encrypt(plaintext, 'keyword', possible_keyword_uk) == ciphertext:
                    best_keyword = f"{possible_keyword_en} (EN)  /  {possible_keyword_uk} (UA)"
                    break

        if best_keyword:
            results['keyword'] = best_keyword

        return results
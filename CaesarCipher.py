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

        test_positions, test_p_chars, test_c_chars = [], [], []
        for i, (p, c) in enumerate(zip(plaintext, ciphertext)):
            if cls._get_alphabet(p):
                test_positions.append(i)
                test_p_chars.append(p)
                test_c_chars.append(c)
                if len(test_positions) >= 3:
                    break

        linear_key = None
        for a in range(34):
            for b in range(34):
                match = True
                for i in range(min(2, len(test_positions))):
                    pos = test_positions[i]
                    p_char, c_char = test_p_chars[i], test_c_chars[i]
                    alphabet = cls._get_alphabet(p_char)

                    expected_shift = cls._calculate_shift(pos, 'linear', (a, b))
                    actual_shift = (alphabet.index(c_char) - alphabet.index(p_char)) % len(alphabet)

                    if expected_shift % len(alphabet) != actual_shift:
                        match = False
                        break
                if match and cls.encrypt(plaintext, 'linear', (a, b)) == ciphertext:
                    linear_key = (a, b)
                    break
            if linear_key: break
        if linear_key: results['linear'] = linear_key

        nonlinear_key = None
        for a in range(34):
            for b in range(34):
                for c in range(34):
                    match = True
                    for i in range(min(3, len(test_positions))):
                        pos = test_positions[i]
                        p_char, c_char = test_p_chars[i], test_c_chars[i]
                        alphabet = cls._get_alphabet(p_char)

                        expected_shift = cls._calculate_shift(pos, 'nonlinear', (a, b, c))
                        actual_shift = (alphabet.index(c_char) - alphabet.index(p_char)) % len(alphabet)

                        if expected_shift % len(alphabet) != actual_shift:
                            match = False
                            break
                    if match and cls.encrypt(plaintext, 'nonlinear', (a, b, c)) == ciphertext:
                        nonlinear_key = (a, b, c)
                        break
                if nonlinear_key: break
            if nonlinear_key: break
        if nonlinear_key: results['nonlinear'] = nonlinear_key

        keyword_chars = ["?"] * len(plaintext)
        has_uk = False

        for p, (p_char, c_char) in enumerate(zip(plaintext, ciphertext)):
            alphabet = cls._get_alphabet(p_char)
            if alphabet:
                if alphabet in (cls.UK_LOWER, cls.UK_UPPER): has_uk = True
                p_idx, c_idx = alphabet.index(p_char), alphabet.index(c_char)
                shift = (c_idx - p_idx) % len(alphabet)

                base_alphabet = cls.UK_UPPER if alphabet in (cls.UK_LOWER, cls.UK_UPPER) else cls.EN_UPPER
                keyword_chars[p] = base_alphabet[shift % len(base_alphabet)]

        best_pattern = None
        for L in range(1, len(plaintext) // 2 + 1):
            pattern = ["?"] * L
            valid = True
            for i, char in enumerate(keyword_chars):
                if char != "?":
                    if pattern[i % L] == "?":
                        pattern[i % L] = char
                    elif pattern[i % L] != char:
                        valid = False
                        break
            if valid and "?" not in pattern:
                best_pattern = "".join(pattern)
                break

        if best_pattern:
            results['keyword'] = best_pattern
        elif all(c != "?" for c in keyword_chars) and keyword_chars:
            results['keyword'] = "".join(keyword_chars)

        return results
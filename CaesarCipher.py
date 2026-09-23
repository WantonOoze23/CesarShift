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
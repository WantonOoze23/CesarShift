import unittest

from CaesarCipher import CaesarCipher


class TestCaesarCipher(unittest.TestCase):
    def setUp(self):
        self.plain_en = "Hello World!"
        self.plain_uk = "Привіт, Світ!"
        self.key = 5

    def test_validation(self):
        self.assertTrue(CaesarCipher.validate_data("Текст"))
        self.assertFalse(CaesarCipher.validate_data("   "))

        is_valid, key = CaesarCipher.validate_key("10")
        self.assertTrue(is_valid)
        self.assertEqual(key, 10)

        is_valid, _ = CaesarCipher.validate_key("abc")
        self.assertFalse(is_valid)

    def test_encryption_decryption_en(self):
        encrypted = CaesarCipher.encrypt(self.plain_en, self.key)
        self.assertNotEqual(self.plain_en, encrypted)

        decrypted = CaesarCipher.decrypt(encrypted, self.key)
        self.assertEqual(self.plain_en, decrypted)

    def test_encryption_decryption_uk(self):
        encrypted = CaesarCipher.encrypt(self.plain_uk, self.key)
        decrypted = CaesarCipher.decrypt(encrypted, self.key)
        self.assertEqual(self.plain_uk, decrypted)

    def test_byte_encryption(self):
        data = b"Some binary data \x00\xff"
        encrypted = CaesarCipher.encrypt_bytes(data, 10)
        decrypted = CaesarCipher.decrypt_bytes(encrypted, 10)
        self.assertEqual(data, decrypted)


if __name__ == "__main__":
    unittest.main()
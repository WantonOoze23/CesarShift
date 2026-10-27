import unittest

from CaesarCipher import TrithemiusCipher


class TestTrithemiusCipher(unittest.TestCase):
    def setUp(self):
        self.text = "Секретне повідомлення для перевірки 123!"

    def test_validation(self):
        valid, key = TrithemiusCipher.validate_key('linear', "2 3")
        self.assertTrue(valid)
        self.assertEqual(key, (2, 3))

        valid, key = TrithemiusCipher.validate_key('nonlinear', "1 2 3")
        self.assertTrue(valid)
        self.assertEqual(key, (1, 2, 3))

        valid, key = TrithemiusCipher.validate_key('keyword', "КЛЮЧ")
        self.assertTrue(valid)
        self.assertEqual(key, "КЛЮЧ")

    def test_linear_mode(self):
        key = (2, 3)
        encrypted = TrithemiusCipher.encrypt(self.text, 'linear', key)
        decrypted = TrithemiusCipher.decrypt(encrypted, 'linear', key)
        self.assertNotEqual(self.text, encrypted)
        self.assertEqual(self.text, decrypted)

    def test_nonlinear_mode(self):
        key = (1, 2, 3)
        encrypted = TrithemiusCipher.encrypt(self.text, 'nonlinear', key)
        decrypted = TrithemiusCipher.decrypt(encrypted, 'nonlinear', key)
        self.assertNotEqual(self.text, encrypted)
        self.assertEqual(self.text, decrypted)

    def test_keyword_mode(self):
        key = "СИСТЕМА"
        encrypted = TrithemiusCipher.encrypt(self.text, 'keyword', key)
        decrypted = TrithemiusCipher.decrypt(encrypted, 'keyword', key)
        self.assertNotEqual(self.text, encrypted)
        self.assertEqual(self.text, decrypted)

    def test_active_attack(self):
        plain = "атака на шифр"
        lin_key = (2, 5)
        cipher_lin = TrithemiusCipher.encrypt(plain, 'linear', lin_key)

        results = TrithemiusCipher.active_attack(plain, cipher_lin)
        self.assertIn('linear', results)
        self.assertEqual(results['linear'], lin_key)

        keyword = "КОД"
        cipher_kw = TrithemiusCipher.encrypt(plain, 'keyword', keyword)

        results_kw = TrithemiusCipher.active_attack(plain, cipher_kw)
        self.assertIn('keyword', results_kw)

        self.assertIn(keyword, results_kw['keyword'])


if __name__ == "__main__":
    unittest.main()
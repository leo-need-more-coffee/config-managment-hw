import unittest
from hw3 import ConfigParser  # Предполагается, что основной код сохранён в файле hw3.py

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        """Создаёт экземпляр парсера перед каждым тестом"""
        self.parser = ConfigParser()

    def test_single_constant(self):
        """Тест на одну константу"""
        input_text = "name := 'TestName'"
        result = self.parser.parse(input_text)
        self.assertEqual(self.parser.constants["name"], "TestName")
        self.assertEqual(result, {})

    def test_multiple_constants(self):
        """Тест на несколько констант"""
        input_text = """
        name := 'TestName'
        number := 42
        array := { 1. 2. 3 }
        """
        result = self.parser.parse(input_text)
        self.assertEqual(self.parser.constants["name"], "TestName")
        self.assertEqual(self.parser.constants["number"], 42)
        self.assertEqual(self.parser.constants["array"], [1, 2, 3])
        self.assertEqual(result, {})

    def test_key_value_with_constant(self):
        """Тест на использование константы в значении"""
        input_text = """
        name := 'TestName'
        output : #[name]
        """
        result = self.parser.parse(input_text)
        self.assertEqual(result["output"], "TestName")

    def test_array_parsing(self):
        """Тест на корректное парсинг массивов"""
        input_text = """
        numbers : { 10. 20. 30 }
        """
        result = self.parser.parse(input_text)
        self.assertEqual(result["numbers"], [10, 20, 30])

    def test_invalid_syntax(self):
        """Тест на некорректный синтаксис"""
        input_text = "invalid := { 10 20 30 }"  # Пропущены точки
        with self.assertRaises(SyntaxError):
            self.parser.parse(input_text)

    def test_undefined_constant(self):
        """Тест на использование неопределённой константы"""
        input_text = "output : #[undefined]"
        with self.assertRaises(ValueError):
            self.parser.parse(input_text)

    def test_multiline_comment_removal(self):
        """Тест на удаление многострочных комментариев"""
        input_text = """
        =begin
        Это комментарий
        =cut
        name := 'TestName'
        """
        result = self.parser.parse(input_text)
        self.assertIn("name", self.parser.constants)
        self.assertEqual(self.parser.constants["name"], "TestName")

if __name__ == "__main__":
    unittest.main()

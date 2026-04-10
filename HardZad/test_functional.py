import unittest
import requests
import time
import subprocess
import os

class TestPythonRustApp(unittest.TestCase):
    """Функциональные тесты для приложения с Rust-расширением."""

    @classmethod
    def setUpClass(cls):
        """Запускаем docker-compose перед всеми тестами."""
        cls.project_dir = os.path.dirname(os.path.abspath(__file__))
        cls.compose_file = "docker-compose.yml"
        print("Запуск docker-compose...")
        result = subprocess.run(
            ["docker-compose", "-f", cls.compose_file, "up", "-d"],
            capture_output=True,
            text=True,
            cwd=cls.project_dir
        )
        if result.returncode != 0:
            raise Exception(f"Не удалось запустить docker-compose: {result.stderr}")
        # Даем приложению время на запуск
        time.sleep(10)

    @classmethod
    def tearDownClass(cls):
        """Останавливаем docker-compose после всех тестов."""
        print("Остановка docker-compose...")
        subprocess.run(
            ["docker-compose", "-f", cls.compose_file, "down"],
            cwd=cls.project_dir
        )

    def test_main_endpoint(self):
        """Тестируем основной эндпоинт /"""
        url = "http://localhost:8080"
        response = requests.get(url, timeout=10)
        self.assertEqual(response.status_code, 200, "Эндпоинт / должен возвращать 200")
        data = response.json()
        self.assertIn("message", data, "Ответ должен содержать поле 'message'")
        self.assertIn("Rust computed sum:", data["message"], "Сообщение должно содержать результат от Rust")
        # Проверяем, что сумма вычислена верно
        expected_sum = sum([1.0, 2.0, 3.0, 4.0, 5.0])
        self.assertIn(str(expected_sum), data["message"], "Вычисленная сумма должна быть 15.0")

    def test_root_health(self):
        """Тестируем здоровье приложения."""
        url = "http://localhost:8080"
        response = requests.get(url, timeout=10)
        self.assertEqual(response.status_code, 200, "Health check должен возвращать 200")


if __name__ == '__main__':
    unittest.main()
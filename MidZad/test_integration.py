import os
import time
import unittest
import subprocess
import sys

class TestServicesIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Запускается один раз перед всеми тестами"""
        cls.shared_dir = r"C:\Users\Артём\Documents\Новая папка\MidZad\shared_data"
        
        # Проверяем, что папка существует
        if not os.path.exists(cls.shared_dir):
            os.makedirs(cls.shared_dir)
        
        # Запускаем docker-compose перед тестами
        print("\n[SETUP] Starting Docker containers...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True,
            cwd=r"C:\Users\Артём\Documents\Новая папка\MidZad"
        )
        
        if result.returncode != 0:
            print(f"Error starting containers: {result.stderr}")
            sys.exit(1)
        
        print("[SETUP] Waiting for containers to initialize...")
        time.sleep(15)  # Даем время на запуск и создание файлов
    
    @classmethod
    def tearDownClass(cls):
        """Запускается один раз после всех тестов"""
        print("\n[CLEANUP] Stopping Docker containers...")
        subprocess.run(
            ["docker-compose", "down"],
            capture_output=True,
            cwd=r"C:\Users\Артём\Documents\Новая папка\MidZad"
        )
        
    
    def test_shared_data_created(self):
        """Проверка, что все сервисы создали свои файлы."""
        print("\n[TEST 1] Checking if all files were created...")
        
        files = os.listdir(self.shared_dir)
        expected_files = ["from_python.txt", "from_go.txt", "from_rust.txt"]
        
        for expected_file in expected_files:
            self.assertIn(
                expected_file, 
                files, 
                f"❌ Файл {expected_file} не найден в {self.shared_dir}"
            )
            print(f"  ✓ {expected_file} exists")
        
        print("[TEST 1] ✅ PASSED")
    
    def test_files_not_empty(self):
        """Проверка, что файлы не пустые."""
        print("\n[TEST 2] Checking if files are not empty...")
        
        files_to_check = {
            "from_python.txt": "Python service",
            "from_go.txt": "Go service",
            "from_rust.txt": "Rust service"
        }
        
        for filename, service_name in files_to_check.items():
            filepath = os.path.join(self.shared_dir, filename)
            
            self.assertTrue(
                os.path.exists(filepath),
                f"❌ Файл {filename} не существует"
            )
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                self.assertTrue(
                    len(content) > 0,
                    f"❌ Файл {filename} от {service_name} пуст"
                )
                print(f"  ✓ {filename}: '{content}'")
        
        print("[TEST 2] ✅ PASSED")
    
    def test_containers_exit_codes(self):
        """Проверка, что все контейнеры завершились успешно."""
        print("\n[TEST 3] Checking container exit codes...")
        
        containers = ["python_service", "go_service", "rust_service"]
        
        for container in containers:
            result = subprocess.run(
                ["docker", "inspect", container, "--format={{.State.ExitCode}}"],
                capture_output=True,
                text=True
            )
            
            exit_code = result.stdout.strip()
            
            if exit_code == "":
                print(f"  ⏳ {container} is still running, waiting...")
                time.sleep(5)
                result = subprocess.run(
                    ["docker", "inspect", container, "--format={{.State.ExitCode}}"],
                    capture_output=True,
                    text=True
                )
                exit_code = result.stdout.strip()
            
            self.assertEqual(
                exit_code, 
                "0", 
                f"❌ {container} exited with code {exit_code} (expected 0)"
            )
            print(f"  ✓ {container} exited successfully (code 0)")
        
        print("[TEST 3] ✅ PASSED")

if __name__ == '__main__':
    # Настраиваем подробный вывод
    unittest.main(verbosity=2)
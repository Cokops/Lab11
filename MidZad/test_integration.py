import os
import time
import unittest
import subprocess
import sys

class TestServicesIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Запускается один раз перед всеми тестами"""
        # Текущий файл: C:\Users\Артём\Documents\Новая папка\MidZad\test_integration.py
        # Проект - это та же папка, где лежит test_integration.py
        cls.project_root = os.path.dirname(os.path.abspath(__file__))  # .../MidZad
        
        cls.shared_dir = os.path.join(cls.project_root, "shared_data")
        
        print(f"\n[SETUP] Current file: {os.path.abspath(__file__)}")
        print(f"[SETUP] Project root: {cls.project_root}")
        print(f"[SETUP] Shared directory: {cls.shared_dir}")
        
        # Проверяем, что папка shared_data существует
        if not os.path.exists(cls.shared_dir):
            os.makedirs(cls.shared_dir)
        
        # Проверяем наличие docker-compose.yml
        docker_compose_path = os.path.join(cls.project_root, "docker-compose.yml")
        if not os.path.exists(docker_compose_path):
            print(f"❌ ERROR: docker-compose.yml not found at {docker_compose_path}")
            print(f"   Files in {cls.project_root}: {os.listdir(cls.project_root)}")
            sys.exit(1)
        
        print(f"✓ Found docker-compose.yml at {docker_compose_path}")
        
        # Запускаем docker-compose перед тестами
        print("\n[SETUP] Starting Docker containers...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True,
            cwd=cls.project_root
        )
        
        if result.returncode != 0:
            print(f"Error starting containers: {result.stderr}")
            sys.exit(1)
        
        print("[SETUP] Waiting for containers to initialize...")
        time.sleep(15)
    
    @classmethod
    def tearDownClass(cls):
        """Запускается один раз после всех тестов"""
        print("\n[CLEANUP] Stopping Docker containers...")
        subprocess.run(
            ["docker-compose", "down"],
            capture_output=True,
            cwd=cls.project_root
        )
    
    def test_shared_data_created(self):
        """Проверка, что все сервисы создали свои файлы."""
        print("\n[TEST 1] Checking if all files were created...")
        
        self.assertTrue(
            os.path.exists(self.shared_dir),
            f"❌ Shared directory {self.shared_dir} does not exist"
        )
        
        files = os.listdir(self.shared_dir)
        expected_files = ["from_python.txt", "from_go.txt", "from_rust.txt"]
        
        for expected_file in expected_files:
            self.assertIn(
                expected_file, 
                files, 
                f"❌ Файл {expected_file} не найден в {self.shared_dir}\n"
                f"   Существующие файлы: {files}"
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
            
            if exit_code == "":
                print(f"  ⚠️  {container} not found or not running")
                continue
            
            self.assertEqual(
                exit_code, 
                "0", 
                f"❌ {container} exited with code {exit_code} (expected 0)"
            )
            print(f"  ✓ {container} exited successfully (code 0)")
        
        print("[TEST 3] ✅ PASSED")

if __name__ == '__main__':
    unittest.main(verbosity=2)
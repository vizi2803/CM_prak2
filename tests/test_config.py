import os
import tempfile
import unittest

from src.config import ConfigError, load_config

class TestConfigValidation(unittest.TestCase):
    """Тесты парсинга CSV-конфигурации и обработки ошибок параметров."""

    def _create_temp_csv(self, content):
        """Создает временный CSV-файл и возвращает путь к нему."""
        fd, path = tempfile.mkstemp(suffix=".csv", text=True)
        with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
            tmp_file.write(content)
        self.addCleanup(self._remove_file, path)
        return path

    @staticmethod
    def _remove_file(path):
        """Удаляет временный файл после теста."""
        if os.path.exists(path):
            os.remove(path)

    def test_valid_remote_config(self):
        """Проверяет успешную загрузку корректного конфига с URL."""
        expected_url = "https://crates.io/api/v1/crates"
        csv_data = (
            "package_name,repository_url,test_mode,ascii_tree\n"
            "serde,https://crates.io/api/v1/crates,false,true\n"
        )
        path = self._create_temp_csv(csv_data)
        cfg = load_config(path)
        self.assertEqual(cfg["package_name"], "serde")
        self.assertEqual(cfg["repository_url"], expected_url)
        self.assertFalse(cfg["test_mode"])
        self.assertTrue(cfg["ascii_tree"])

    def test_valid_test_mode_config(self):
        """Проверяет загрузку конфига в режиме тестирования с файлом."""
        repo_file = self._create_temp_csv("A: B\n")
        csv_data = (
            "package_name,repository_url,test_mode,ascii_tree\n"
            f"A,{repo_file},true,false\n"
        )
        path = self._create_temp_csv(csv_data)
        cfg = load_config(path)
        self.assertEqual(cfg["package_name"], "A")
        self.assertTrue(cfg["test_mode"])
        self.assertFalse(cfg["ascii_tree"])

    def test_missing_config_file(self):
        """Проверяет ошибку при отсутствии файла конфигурации."""
        with self.assertRaises(ConfigError):
            load_config("non_existent_config.csv")

    def test_invalid_package_name(self):
        """Проверяет ошибку при пустом или содержащем пробелы имени пакета."""
        csv_empty = (
            "package_name,repository_url,test_mode,ascii_tree\n"
            ",https://crates.io/api/v1/crates,false,true\n"
        )
        with self.assertRaises(ConfigError):
            load_config(self._create_temp_csv(csv_empty))

        csv_spaces = (
            "package_name,repository_url,test_mode,ascii_tree\n"
            "bad name,https://crates.io/api/v1/crates,false,true\n"
        )
        with self.assertRaises(ConfigError):
            load_config(self._create_temp_csv(csv_spaces))

    def test_invalid_repository_url(self):
        """Проверяет ошибку при некорректном URL в обычном режиме."""
        csv_data = (
            "package_name,repository_url,test_mode,ascii_tree\n"
            "serde,not_a_valid_url,false,true\n"
        )
        with self.assertRaises(ConfigError):
            load_config(self._create_temp_csv(csv_data))

    def test_missing_test_repository_file(self):
        """Проверяет ошибку при несуществующем файле в тестовом режиме."""
        csv_data = (
            "package_name,repository_url,test_mode,ascii_tree\n"
            "A,missing_graph.txt,true,true\n"
        )
        with self.assertRaises(ConfigError):
            load_config(self._create_temp_csv(csv_data))

    def test_invalid_boolean_flags(self):
        """Проверяет ошибку при некорректных флагах test_mode и ascii_tree."""
        csv_bad_test = (
            "package_name,repository_url,test_mode,ascii_tree\n"
            "serde,https://crates.io/api/v1/crates,maybe,true\n"
        )
        with self.assertRaises(ConfigError):
            load_config(self._create_temp_csv(csv_bad_test))

        csv_bad_ascii = (
            "package_name,repository_url,test_mode,ascii_tree\n"
            "serde,https://crates.io/api/v1/crates,false,123\n"
        )
        with self.assertRaises(ConfigError):
            load_config(self._create_temp_csv(csv_bad_ascii))

if __name__ == "__main__":
    unittest.main()
import csv
import os
from urllib.parse import urlparse

REQUIRED_FIELDS = (
    "package_name",
    "repository_url",
    "test_mode",
    "ascii_tree",
)
VALID_BOOL_TRUE = ("true", "1", "yes")
VALID_BOOL_FALSE = ("false", "0", "no")

class ConfigError(Exception):
    """Исключение при ошибках в файле конфигурации."""

def parse_bool(value, field_name):
    """Преобразует строковое значение параметра в булев тип."""
    normalized = str(value).strip().lower()
    if normalized in VALID_BOOL_TRUE:
        return True
    if normalized in VALID_BOOL_FALSE:
        return False
    raise ConfigError(
        f"Параметр '{field_name}' должен быть true или false, "
        f"получено: '{value}'"
    )

def validate_package_name(name):
    """Проверяет корректность имени анализируемого пакета."""
    clean_name = name.strip()
    if not clean_name:
        raise ConfigError("Параметр 'package_name' не может быть пустым.")
    if any(char.isspace() for char in clean_name):
        raise ConfigError(
            f"Параметр 'package_name' не должен содержать пробелы: "
            f"'{clean_name}'"
        )
    return clean_name

def validate_repository_source(repo_source, test_mode):
    """Проверяет URL репозитория или путь к локальному тестовому файлу."""
    clean_source = repo_source.strip()
    if not clean_source:
        raise ConfigError(
            "Параметр 'repository_url' не может быть пустым."
        )
    if test_mode:
        if not os.path.isfile(clean_source):
            raise ConfigError(
                f"Файл тестового репозитория не найден: '{clean_source}'"
            )
        return clean_source

    parsed = urlparse(clean_source)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ConfigError(
            f"Некорректный URL репозитория: '{clean_source}'"
        )
    return clean_source

def read_csv_row(config_path):
    """Считывает первую строку данных из CSV-файла конфигурации."""
    if not os.path.isfile(config_path):
        raise ConfigError(
            f"Файл конфигурации не найден: '{config_path}'"
        )
    try:
        with open(config_path, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ConfigError("Файл конфигурации пуст.")
            missing = [
                col for col in REQUIRED_FIELDS if col not in reader.fieldnames
            ]
            if missing:
                raise ConfigError(
                    f"Отсутствуют обязательные колонки: {', '.join(missing)}"
                )
            row = next(reader, None)
            if row is None:
                raise ConfigError("В файле конфигурации нет данных.")
            return row
    except csv.Error as err:
        raise ConfigError(f"Ошибка синтаксиса CSV: {err}") from err

def load_config(config_path):
    """Загружает и проверяет все параметры конфигурации."""
    row = read_csv_row(config_path)
    for field in REQUIRED_FIELDS:
        if row.get(field) is None:
            raise ConfigError(f"Не заполнено значение для '{field}'.")

    package_name = validate_package_name(row["package_name"])
    test_mode = parse_bool(row["test_mode"], "test_mode")
    ascii_tree = parse_bool(row["ascii_tree"], "ascii_tree")
    repository_url = validate_repository_source(
        row["repository_url"], test_mode
    )

    return {
        "package_name": package_name,
        "repository_url": repository_url,
        "test_mode": test_mode,
        "ascii_tree": ascii_tree,
    }
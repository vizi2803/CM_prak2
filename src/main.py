import argparse
import sys

from src.config import ConfigError, load_config

DEFAULT_CONFIG_PATH = "config.csv"
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

def parse_args(argv=None):
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов Cargo."
    )
    parser.add_argument(
        "-c",
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Путь к CSV-файлу конфигурации (по умолчанию: config.csv)",
    )
    return parser.parse_args(argv)

def print_config(config):
    """Выводит параметры конфигурации в формате ключ: значение."""
    for key, value in config.items():
        print(f"{key}: {value}")

def main(argv=None):
    """Основная функция запуска приложения."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as err:
        print(f"Ошибка конфигурации: {err}", file=sys.stderr)
        return EXIT_FAILURE
    except OSError as err:
        print(f"Ошибка чтения файла: {err}", file=sys.stderr)
        return EXIT_FAILURE

    print_config(config)
    return EXIT_SUCCESS

if __name__ == "__main__":
    sys.exit(main())
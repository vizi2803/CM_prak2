@echo off
chcp 65001 > nul
echo === Запуск со штатной конфигурацией ===
python -m src.main --config config.csv
echo.
echo === Демонстрация ошибки: файл конфигурации не найден ===
python -m src.main --config missing_config.csv
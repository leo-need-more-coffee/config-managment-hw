import csv
import json
import os
import sys
from pathlib import Path
from typing import Dict, Set


def parse_config(file_path: str) -> Dict[str, str]:
    """
    Считывает конфигурационный файл формата CSV и возвращает параметры.
    """
    config = {}
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 2:
                key, value = row
                config[key.strip()] = value.strip()
    return config


def parse_dependencies(package_name: str, base_path: str) -> Dict[str, Set[str]]:
    """
    Рекурсивно анализирует зависимости JavaScript-пакета.
    """
    dependencies = {}

    def collect_dependencies(package: str, path: str):
        package_json_path = Path(path) / package / "package.json"
        if not package_json_path.exists():
            print(f"Файл {package_json_path} не найден. Пропускаю {package}.", file=sys.stderr)
            return

        with open(package_json_path, 'r', encoding='utf-8') as f:
            try:
                package_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Ошибка чтения {package_json_path}: {e}", file=sys.stderr)
                return

        if "dependencies" in package_data:
            deps = set(package_data["dependencies"].keys())
            dependencies[package] = deps
            for dep in deps:
                if dep not in dependencies:  # Избегаем зацикливания
                    collect_dependencies(dep, path)

    collect_dependencies(package_name, base_path)
    return dependencies


def generate_dot(dependencies: Dict[str, Set[str]]) -> str:
    """
    Генерирует код в формате DOT для графа зависимостей.
    """
    dot = ["digraph G {"]
    for package, deps in dependencies.items():
        for dep in deps:
            dot.append(f'    "{package}" -> "{dep}";')
    dot.append("}")
    return "\n".join(dot)


def main():
    if len(sys.argv) != 2:
        print("Использование: python script.py <путь_к_конфигурационному_файлу>", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    if not os.path.exists(config_path):
        print(f"Конфигурационный файл {config_path} не найден.", file=sys.stderr)
        sys.exit(1)

    # Чтение конфигурации
    config = parse_config(config_path)
    package_name = config.get("1")
    output_path = config.get("2")

    if not all([package_name, output_path]):
        print("Ошибка: Конфигурационный файл должен содержать все обязательные поля.", file=sys.stderr)
        sys.exit(1)

    # Сбор зависимостей
    base_path = "./node_modules"  # Базовый путь для анализа
    dependencies = parse_dependencies(package_name, base_path)

    if not dependencies:
        print(f"Не удалось найти зависимости для пакета {package_name}.", file=sys.stderr)
        sys.exit(1)

    # Генерация DOT-кода
    dot_code = generate_dot(dependencies)

    # Сохранение результата
    with open(output_path, 'w') as f:
        f.write(dot_code)
    print(f"Граф зависимостей сохранен в {output_path}.")

    # Вывод графа в консоль
    print(dot_code)


if __name__ == "__main__":
    main()

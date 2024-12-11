# 1. Клонирование репозитория

Склонируйте репозиторий с исходным кодом и тестами:

```
git clone <URL репозитория>
cd <директория проекта>
```

# 2. Установка зависимостей при запуске

```
pip install subprocess
npm install vue-route  <или название любого другого пакета>
npm install axios
```

# Создайте виртуальное окружение

```bash
# Активируйте виртуальное окружение
python -m venv venv
# Для Windows:
venv\Scripts\activate
# Для MacOS/Linux:
source venv/bin/activate
```


# 3. Структура проекта
Проект содержит следующие файлы и директории:
```bash
unittests.py              # файл для тестирования
config.csv            # конфигурационный файл 
hw2.py                  # файл с программой
output.dot          #файл вывода программы
```

# 4. Запуск проекта
```bash
py hw2.py config.csv     # py название файла <файл с конфигом>
В config.csv необходимо указать название пакета для генерации его зависимостей
```


# 5. Тестирование с vue-route
Вывод программы
```
digraph G {
    "vue-route" -> "page";
    "page" -> "path-to-regexp";
    "path-to-regexp" -> "isarray";
}
```
 
# Тестирование с axios
Вывод программы
```
digraph G {
    "axios" -> "follow-redirects";
    "axios" -> "proxy-from-env";
    "axios" -> "form-data";
    "form-data" -> "combined-stream";
    "form-data" -> "asynckit";
    "form-data" -> "mime-types";
    "combined-stream" -> "delayed-stream";
    "mime-types" -> "mime-db";
}
```


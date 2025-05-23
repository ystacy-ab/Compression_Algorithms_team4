# Дослiдження методiв компресiї даних
Cтворення власної програми-кодека.

## Короткий опис

Цей проєкт — це дослідження сучасних, та не зовсім, алгоритмів стиснення даних, а також реалізація власного “застосунку-кодека” для роботи з текстом, зображеннями, аудіо та відео-файлами. Ми вивчили принципи роботи класичних методів безвтратної компресії, реалізували їх з нуля, та побудували інтерфейс для практичного використання й порівняння.

## Реалізовані алгоритми

- **Huffman Coding**: оптимальне префіксне кодування.
- **LZ77**: стиснення з використанням ковзного вікна.
- **LZW**: модифікація LZ78 з автоматичним розширенням словника.
- **DEFLATE**: поєднання LZ77 та Huffman Coding.

## Функціонал застосунку

- Стиснення та розпакування:
  - Текстових файлів: `.txt`
  - Зображень: `.png`, `.jpg`, `.tiff`, `.bmp`
  - Аудіо: `.wav`, `.mp3`
  - Відео: `.mp4`
- Вибір алгоритму стиснення.
- Порівняння розміру та часу обробки файлів до та після стиснення.
- Побудова графіків ефективності.

## Структура проєкту
<pre> project/
├── algorithms/
│ ├── huffman.py
│ ├── lzw.py
│ ├── lz77.py
│ └── deflate.py
├── static/
│ ├── audio1.mp3
│ ├── audio1.wav
│ ├── audio2.mp3
│ ├── img1.bmp
│ ├── img1.jpg
│ ├── img1.png
│ ├── img1.tiff
│ ├── txt1.txt
│ ├── txt2.txt
│ ├── txt3.txt
│ ├── video1.mp4
│ └── video2.mp4
├── main_argparse.py
├── mini_ui.py
├── latex_report.pdf
├── requirements.txt
└── README.md` </pre>

## Запуск
Програма працює через командний рядок з використанням аргументів. Приклад запуску:

<pre> python3 main_argparse.py hello.txt deflate </pre>

## Команда
- Лизенко Діана: реалізація LZ77, тестування відео файлів
- Пілецька Єлізавета: LZW, DEFLATE, тестування аудіо файлів
- Яблуновська Анастасія: Huffman Coding, тестування текстових файлів
- Гобела Максим: DEFLATE, тестування файлів із зображенням


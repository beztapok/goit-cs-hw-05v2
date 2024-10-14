import asyncio
import aiofiles
import logging
from pathlib import Path
import argparse

logging.basicConfig(level=logging.ERROR, filename='file_sorter_errors.log')

def create_folders(source_path, output_path):
    """
    Створює вихідну та цільову папки, якщо вони не існують.
    """
    if not source_path.exists():
        source_path.mkdir(parents=True, exist_ok=True)
        print(f'Вихідна папка "{source_path}" створена.')
    else:
        print(f'Вихідна папка "{source_path}" вже існує.')

    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
        print(f'Цільова папка "{output_path}" створена.')
    else:
        print(f'Цільова папка "{output_path}" вже існує.')

def create_test_files(source_path):
    """
    Створює кілька тестових файлів з різними розширеннями у вихідній папці.
    """
    if any(source_path.iterdir()):
        print(f'Вихідна папка "{source_path}" не порожня. Тестові файли не створені.')
        return
    else:
        # Створює кілька тестових файлів з різними розширеннями
        extensions = ['txt', 'jpg', 'pdf', 'docx', 'png', 'unknown']
        for i, ext in enumerate(extensions, 1):
            if ext == 'unknown':
                file_name = source_path / f'test_file_{i}'
            else:
                file_name = source_path / f'test_file_{i}.{ext}'
            file_name.touch()
        print(f'Тестові файли створені у папці "{source_path}".')

async def read_folder(folder, output_path):
    """
    Рекурсивно читає всі файли у вихідній папці та її підпапках.
    """
    try:
        for item in folder.iterdir():
            if item.is_dir():
                await read_folder(item, output_path)
            else:
                await copy_file(item, output_path)
    except Exception as e:
        logging.error(f'Помилка при читанні папки {folder}: {e}')

async def copy_file(file, output_path):
    """
    Копіює кожен файл у відповідну підпапку у цільовій папці на основі його розширення.
    """
    try:
        ext = file.suffix[1:]  # Отримуємо розширення без крапки
        if not ext:
            ext = 'unknown'
        dest_folder = output_path / ext
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_file = dest_folder / file.name
        async with aiofiles.open(file, 'rb') as fsrc:
            async with aiofiles.open(dest_file, 'wb') as fdst:
                while True:
                    chunk = await fsrc.read(1024 * 1024)  # Читаємо по 1МБ
                    if not chunk:
                        break
                    await fdst.write(chunk)
    except Exception as e:
        logging.error(f'Помилка при копіюванні файлу {file}: {e}')

def main():
    """
    Функція, що запускає асинхронне сортування файлів.
    """
    parser = argparse.ArgumentParser(description="Сортувальник файлів за розширенням.")
    parser.add_argument('source_folder', nargs='?', default='source_folder', type=str, help='Шлях до вихідної папки')
    parser.add_argument('output_folder', nargs='?', default='output_folder', type=str, help='Шлях до цільової папки')
    args = parser.parse_args()

    source_path = Path(args.source_folder)
    output_path = Path(args.output_folder)

    # Створюємо папки
    create_folders(source_path, output_path)

    # Створюємо тестові файли
    create_test_files(source_path)

    # Запускаємо асинхронне сортування файлів
    asyncio.run(read_folder(source_path, output_path))
    print('Сортування файлів завершено.')

if __name__ == '__main__':
    main()

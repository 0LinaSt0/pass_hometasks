from PIL import Image
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def resize_image():
    try:
        img = Image.open('input.jpg')
        img_resized = img.resize((800, 600))
        img_resized.save('output.jpg')
        logging.info("Изображение успешно обработано и сохранено как output.jpg")
    except FileNotFoundError:
        logging.error("Файл input.jpg не найден")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        

if __name__ == "__main__":
    resize_image()
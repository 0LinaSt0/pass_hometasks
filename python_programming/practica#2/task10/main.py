import pyjokes
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)


def tell_joke():
    try:
        joke = pyjokes.get_joke(language='en', category='all')
        print(joke)
        logging.info("Шутка успешно выведена")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    tell_joke()
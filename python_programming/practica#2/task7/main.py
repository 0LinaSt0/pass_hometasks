from asciimatics.screen import Screen
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def demo(screen):
    try:
        for i in range(100):
            screen.print_at('Hello, Asciimatics!', i % screen.width, 
        screen.height // 2)
            screen.refresh()
            time.sleep(0.05)
            screen.clear()
        logging.info("Анимация успешно выполнена")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    Screen.wrapper(demo)
from art import text2art
import logging 


# Настройка логирования
logging.basicConfig(level=logging.INFO)

def create_ascii_art():
    try:
        message = input("Введите сообщение для ASCII-арта: ")
        art = text2art(message)
        print(art)
        logging.info("ASCII-арт успешно создан")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        

if __name__ == "__main__":
    create_ascii_art()
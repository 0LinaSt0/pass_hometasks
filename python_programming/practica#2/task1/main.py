import cowsay
import logging


logging.basicConfig(level=logging.INFO)


def main():
    try:
        msg = input('Введите сообщение: ')
        cowsay.cow(msg)
        logging.info('Программа выполнена успешно')

    except Exception as e:
        logging.error(f'Произошла ошибка: {e}')


if __name__ == '__main__':
    main()
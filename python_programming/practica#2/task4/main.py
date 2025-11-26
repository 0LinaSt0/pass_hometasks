import numpy as np
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)


def calculate_statistics():
    try:
        data = np.random.rand(100)
        mean = np.mean(data)
        std_dev = np.std(data)
        print(f"Среднее значение: {mean}")
        print(f"Стандартное отклонение: {std_dev}")
        logging.info("Вычисления успешно выполнены")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        

if __name__ == "__main__":
    calculate_statistics()
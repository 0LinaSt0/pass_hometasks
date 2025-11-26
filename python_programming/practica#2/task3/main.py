import pandas as pd
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)
def process_data():
    try:
        df = pd.read_csv('data.csv')
        df['Выручка'] = df['Количество'] * df['Цена']
        total_revenue = df['Выручка'].sum()
        print(df)
        print(f"\nОбщая выручка: {total_revenue}")
        logging.info("Данные успешно обработаны")
    except FileNotFoundError:
        logging.error("Файл data.csv не найден")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    process_data()
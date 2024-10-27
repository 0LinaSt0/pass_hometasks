import json
import requests
import logging

def fetch_data():
    tagret_url = 'https://httpbin.org/get'
    try:
        response = requests.get(tagret_url)
        response.raise_for_status()  # Проверка статуса ответа
        data = response.json()
        print(json.dumps(data, indent=4))  # Красивый вывод JSON
        logging.info("Данные успешно получены")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при выполнении запроса: {e}")


if __name__ == "__main__":
    fetch_data()
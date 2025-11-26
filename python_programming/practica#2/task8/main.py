import ephem
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def calculate_sun_times():
    try:
        lat = input("Введите широту (например, 55.75 для Москвы): ")
        lon = input("Введите долготу (например, 37.61 для Москвы): ")
        observer = ephem.Observer()
        observer.lat = lat
        observer.lon = lon
        observer.date = ephem.now()
        sun = ephem.Sun()
        sunrise = observer.next_rising(sun)
        sunset = observer.next_setting(sun)
        print(f"Восход солнца: {ephem.localtime(sunrise)}")
        print(f"Заход солнца: {ephem.localtime(sunset)}")
        logging.info("Время восхода и захода солнца успешно вычислено")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        

if __name__ == "__main__":
    calculate_sun_times()
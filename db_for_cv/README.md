# Setup: Аналитическая платформа для мониторинга COVID-19

## Структура проекта
- **data_preprocess.ipynb:** Jupyter Notebook с предобработкой, SQL, PySpark и визуализацией.
- **report.pdf:** Презентация в PDF.
- **README.md:** инструкции по развертыванию HDFS и запуску запросов.
- **docker-compose.yml:** файл-сборщик.
- **hadoop_conf:** папка с минимальными конфигурациями для hdfs контейнеров
- **metadata_cleaned.xml & hdfs-site.xml:** предобработанный датасет в двух форматах


## Команды
Сборка и запуск контейнера:
```bash
docker-compose up
```

Проверка статусов контейнеров:
```bash
docker ps -a
```

Коннект к контейнеру через bash:
```bash
docker exec -it --user root <container_name> bash
```


Проверка логов контейнера
```bash
docker logs <container_name>
```



## Настройки после запуска
1. Cоздать каталоги для jovyan и выдать права:
```bash
hdfs dfs -mkdir -p /user/jovyan/covid_dataset/images
hdfs dfs -mkdir -p /user/jovyan/covid_dataset/metadata

hdfs dfs -chown -R jovyan:jovyan /user/jovyan/covid_dataset

hdfs dfs -chmod -R 775 /user/jovyan/covid_dataset
```

4. Создать каталог warehouse и выдать права (в hdfs):
```bash
hdfs dfs -mkdir -p /user/jovyan/warehouse

hdfs dfs -chown -R jovyan:jovyan /user/jovyan/warehouse

hdfs dfs -chmod -R 775 /user/jovyan/warehouse
```


## Источники
Ссылка на целевой датасет:
https://github.com/ieee8023/covid-chestxray-dataset/tree/master

| Компонент     | Адрес                                            |
| ------------- | ------------------------------------------------ |
| NameNode      | [http://localhost:9870](http://localhost:9870)   |
| Spark Worker  | [http://localhost:8081](http://localhost:8080)   |
| Jupyter Server | [http://localhost:8888](http://localhost:8888/) |

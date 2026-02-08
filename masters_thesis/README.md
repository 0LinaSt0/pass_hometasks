# MVP Ителектуальной системы распознавания товаров на полках с возможностью дообучения и интеграции в бизнес-процессы


![Демонстрация](data/materials/gif_demonstration.gif)

Более полное видео с демострацией можно посмотреть в:
`data/materials/full_demonstration.mp4`


## Используемые ресурсы
| Название | Мощности |
| --- | --- |
| Формирование датасета | |
| CPU | Intel Xeon @ 2.00 GHz 31-32 GB |
| OC | Kaggle notebook |
| --- | --- |
| Дообучение YOLO | |
| GPU | NVIDIA Tesla P100 PCIe 16GB |
| OC | Kaggle notebook |
| --- | --- |
| Предиктор и кластеризация на локальном устройстве | |
| Процессор | AMD Ryzen 7 32 GB |
| Видеокарта | NVIDIA GeForce RTX 5060 Laptop GPU 8 GB |
| ОС | Windows 11 (на базе WSL)


## Структура проекта

Основные объекты:
1. `predict.py`: точка входа 
1. `consts.py`: все настраиваемые параметры, используемые пути и общие переменные
1. `requirements.txt`: файл с зависимостями проекта
1. `utils\`: папка с пайплайнами реализации
	1. `analyze_shelf.py`: полный пайплайн по сегментированию, детекции и визуализации товаров
	1. `clip_img2vec.py`: имплементация CLIP модели
	1. `data_preprocess.py`: общие функции с препроцессингом данных 
	1. `create_dataset.py`: пайплайн по формированию целевого датасета из 5000 экземпляров
	1. `dataset&YOLO_train.ipynb`: jupyter ноутбук по формированию датасета и дообучению YOLO на целевых данных. Среда исполнения - Kaggle
	1. `utils.py`: утилитарные фукнции
1. `data/`: дата проекта
	1. `examples/`: содержит в себе примеры потолочных пространств и разметку
	1. `materials/`: демонстрации работы сервиса
	1. `yolo_model/`: папка с yolo моделью
	1. `tmp_results/`: дефолтная папка для сохранения логов предсказаний


## Локальный запуск

### Настройка среды
Первым шагом необходимо настроить виртуальное окружение, установив необходимые зависимости из файла `requirements.txt`. Крайне рекомендуется работать на `Python3.12`. 
В случае возникновения проблем с CLIP рекомендуется устанавливать пакеты из git:
```bash
$ pip install git+https://github.com/openai/CLIP.git
```

### Экскурс в реализацию
Основная точка входа проекта - файл `predict.py` в корневой папке. 

Поддерживаемый функционал:
```bash
$ python predict.py -h

usage: predict.py [-h] [--image IMAGE] [--label LABEL] [--output OUTPUT]
                  [--no-group-in-clusters] [--no-visual]

Product Shelf Analysis

options:
  -h, --help            show this help message and exit
  --image IMAGE, -i IMAGE
                        Path to shelf image
  --label LABEL, -l LABEL
                        Path to label (.txt)
  --output OUTPUT, -o OUTPUT
                        Path to JSON result
  --no-group-in-clusters
                        Do not group bboxes (crops) into clusters
  --no-visual           Do not show bboxes visualization
```

Каждый из флагов является опциональным. При запуске без переданных изображения и лейблов результат будет рассчитан на тестовом примере `data/examples/test_2042.jpg`.

Программу возможно запускать и при отсутсвии разметки. В таком случае в `response.json` будет содержать информацию о кластеризации и предсказанных bbox'ов без метрик.

Для визуализации задетекченных bbox'ов используется утилита python3-tk. Установка на Ubuntu:
```bash
$ sudo apt-get install python3-tk
```

В результате исполнения в консоль программы выводится краткая служебная информация о метках и пути сохранения логов. Основной результат содержит в себе response файл по установленной структуре:
```json
response = {
    "request_id": <req_id>,
    "timestamp": <req_time>,
    "store_id": none,
    "planogram_id": none,

    "detections": [
        {
            "sku": <num_sku>,
            "brand": <cluster_name>,
            "category": none,
            "confidence": confidence,
            "bbox": <x1, y1, x2, y2>
            "area_px": <area_px>
        }
    ],
    "counts": {
        "sku_by_categoty": {
            <cluster_name>:
                "total_sku": none
                "detected_sku": <count_sku_by_cluster>
                "total_area_px": <area_by_cluster>
        },
        "total_sku": none
        "detected_sku": sum(by_clusters)
        "total_area_px": sum(by_clusters)
    },
    "planogram_match": none,

    "metrics": {
        "f1": <f1_if_exists>,
        "osa": none,
        "shelf": none
    },
    "processing_time_ms": <detection_execute_time>
}
```

### Примеры запуска

```bash
$ python predict.py

***> Invalid image path. Return results for img data/examples/test_2042.jpg for demonstration

***> Define analyzer

***> Start analyzing:
        --> Get img and predict bboxes
        --> Calculate metrics
        --> Grouping in clusters
100%|████████████████████████████████████████████| 121/121 [00:01<00:00, 119.31it/s]
Found 5 clusters (+ True noise points)

********** Analyze completed **********
        --> Exec time:  0.80s |  803.64mls
        --> Image path: data/examples/test_2042.jpg
        --> Results path: data/tmp_results/test_2042_20260209001316
        --> Response filepath: data/tmp_results/test_2042_20260209001316/response.json
        --> Metrics: {
  "true_positive": 110,
  "false_positives": 11,
  "false_negative": 2,
  "precision": 0.9090909090909091,
  "recall": 0.9821428571428571,
  "f1": 0.944206008583691,
  "detected_clusters": 5
}

RESPONSE 200: Success
```

```bash
$ python predict.py -i data/examples/without_labels.jpg

***> Invalid label path. Return only groups of clusters

***> Define analyzer

***> Start analyzing:
        --> Get img and predict bboxes
        --> Grouping in clusters
100%|██████████████████████████████████████████████| 71/71 [00:00<00:00, 101.26it/s]
Found 5 clusters (+ True noise points)

********** Analyze completed **********
        --> Exec time:  1.00s |  1001.05mls
        --> Image path: data/examples/without_labels.jpg
        --> Results path: data/tmp_results/without_labels_20260209001218
        --> Response filepath: data/tmp_results/without_labels_20260209001218/response.json
        --> Metrics: {
  "detected_clusters": 5
}

RESPONSE 200: Success
```

```bash
$ python predict.py -i data/examples/test_77.jpg -l data/examples/test_77.txt

***> Define analyzer

***> Start analyzing:
        --> Get img and predict bboxes
        --> Calculate metrics
        --> Grouping in clusters
100%|████████████████████████████████████████████| 237/237 [00:01<00:00, 119.65it/s]
Found 4 clusters (+ True noise points)

********** Analyze completed **********
        --> Exec time:  0.77s |  765.76mls
        --> Image path: data/examples/test_77.jpg
        --> Results path: data/tmp_results/test_77_20260209001437
        --> Response filepath: data/tmp_results/test_77_20260209001437/response.json
        --> Metrics: {
  "true_positive": 230,
  "false_positives": 7,
  "false_negative": 0,
  "precision": 0.9704641350210971,
  "recall": 1.0,
  "f1": 0.9850107066381156,
  "detected_clusters": 4
}

RESPONSE 200: Success
```
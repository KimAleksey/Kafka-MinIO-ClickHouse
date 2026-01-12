# Работа с Kafka

## 💻 Что в проекте

В данном проекте реализовано взаимодействие Kafka, S3 хранилища (MinIO), ClickHouse. 
В проекте используются следующие основные компоненты.

- ✔️ Docker - для сборки проекта.
- ✔️ Kafka + ZooKeeper - для реализации брокера сообщений.
- ✔️ Python - для генерации данных и отправки их в Kafka, а также для считывания из Kafka и записи в S3-MinIO.
- ✔️ S3-MinIO - для сохранения данных, полученных из Kafka, в формате parquet.
- ✔️ ClickHouse - для сохранения данных из Kafka в таблицу.
- ✔️ UV - менеджер зависимостей.

## 📖 Описание

В этом проекте при запуске запускает один исполняемый python файл - `main.py`. 
В `main.py` реализован Kafka producer, который генерирует данные о зарегистрированных пользователях и загружает в Kafka topic.
Так же в нем реализован Kafka consumer, который считывает сообщения из Kafka topic и записывает пакет данных в S3 хранилище.

В проекте реализованы следующие шаги:
- ✔️ Генерируются данные о зарегистрированных пользователях, с использованием библиотеки faker.
- ✔️ Сгенерированные данные записываются в Kafka topic. С периодичностью 1000 сообщений в секунду.
- ✔️ Сообщения из Kafka topic считываются с помощью python и записываются пачками по 10000 в S3-MinIO.
- ✔️ В ClickHouse создана таблица с движком Kafka, которая потребляет данные из Kafka topic. 
- ✔️ Все вышеописанные шаги собраны в один Docker-compose file, для простоты запуска проекта.

📁 Структура проекта

```text
Project-2-Kafka-MinIO-ClickHouse/
│
├── main.py                          # Точка входа: запускает продюсер и консьюмер
├── Dockerfile                       # Образ для запуска Python-приложения
├── docker-compose.yaml              # Оркестрация Kafka, MinIO, ClickHouse и приложение
├── requirements.txt                 # Зависимости Python (pip)
├── pyproject.toml                   # Метаданные и зависимости проекта (uv / poetry)
├── uv.lock                          # Lock-файл зависимостей
├── README.md                        # Документация проекта
├── .python-version                  # Версия Python
├── .dockerignore                    # Что не копировать в Docker image
├── codes/                           # Весь прикладной код проекта
│   ├── simple_producer.py           # Kafka Producer — отправка сообщений в топик
│   ├── simple_consumer.py           # Kafka Consumer — чтение сообщений для отладки
│   ├── kafka_to_s3_minio.py         # Kafka → MinIO: читает сообщения и пишет Parquet в S3
│   ├── read_data_from_s3_minio.py   # Читает данные из MinIO в pandas.DataFrame
│   └── utils/                       # Вспомогательные функции
│       └── utils.py                 # Генерация пользователей, хелперы, валидаторы
└── .git/                            # Репозиторий Git
```

## 🚀 Установка

### Клонировать репозиторий:

```bash
git clone https://github.com/KimAleksey/Kafka-MinIO-ClickHouse.git
cd Kafka-MinIO-ClickHouse
```

### Запуск проекта

```bash
docker compose up -d
```

## Работа с проектом

### Работа с Kafka.

1. Перейти в http://localhost:8888/.
2. Создать  topic - my_topic.
3. Убедиться что в топик идет запись сообщений.

### Работа с S3-MinIO

1. Перейти в http://localhost:9000/.
2. Создать access_key, secret_key.
3. Создать bucket my-bucket.
4. Убедиться, что в bucket загружаются файлы в формате parquet.

## Запись в topic с помощью CLI

```bash
docker exec -it kafka kafka-console-producer \
  --broker-list localhost:9092 \
  --topic my_topic
```

Для выхода из интерактивного режима - ctrl + c.

## Считывание сообщений из topic с помощью CLI

### Просмотр сообщений "Без группы" с самого начала:

```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic my_topic \
  --from-beginning
```

### Просмотр сообщений "Только новые":

```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic my_topic
```

### Просмотр сообщений "Новые не прочитанные":

```bash
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic my_topic \
  --group mygroupcli
```

```text
Processed a total of 39 messages
```

### Прочитанные строки фиксируются в Kafka и мы можем это проверить командой:

```bash
docker exec -it kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group mygroupcli \
  --describe 
```

```text
GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
mygroupcli      my_topic        0          182             190             8 
```

Для выхода из интерактивного режима - ctrl + c.


## Скрипт для создания таблиц в ClickHouse

```sql
DROP TABLE IF EXISTS kafka_users_consumer;
DROP TABLE IF EXISTS kafka_users_phys_table;
DROP TABLE IF EXISTS kafka_users_mat_view;

CREATE TABLE kafka_users_consumer
(
    user_id String,
    created_at String,
    username String,
    password String,
    email String,
    first_name String,
    last_name String
) ENGINE = Kafka SETTINGS
    kafka_broker_list = 'kafka',
    kafka_topic_list = 'my_topic',
    kafka_group_name = 'clickhouse',
    kafka_format = 'JSON';
    
CREATE TABLE kafka_users_phys_table
(
    user_id String,
    created_at String,
    username String,
    password String,
    email String,
    first_name String,
    last_name String
)
ENGINE = MergeTree()
ORDER BY (user_id);

CREATE MATERIALIZED VIEW kafka_users_mat_view TO kafka_users_phys_table 
    AS SELECT * FROM kafka_users_consumer;
```
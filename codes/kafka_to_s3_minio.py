import threading
import uuid
import json
import logging
import datetime
import pandas as pd

from typing import Any
from confluent_kafka import Consumer, TopicPartition, KafkaError

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# MinIO параметры.
STORAGE_OPTIONS = {
    "key": "FGewAOG3bIf6eGiIuC2u",
    "secret": "5XhWPmq8holaejbdqpM6eZ4bjyA0zn9lYKw5acrb",
    "client_kwargs": {"endpoint_url": "http://minio:9000"},
}
BUCKET_NAME = "my-bucket"
BATCH_SIZE = 100


def write_to_s3_minio(batch: list[dict[Any, Any]]) -> None:
    """
    Записывает данные в формате Parquet.

    :param batch: Данные для записи. Список словарей.
    :return: None.
    """
    if not batch:
        return
    file_uuid = uuid.uuid4()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    path = f"s3://{BUCKET_NAME}/{date_str}/{file_uuid}.parquet"
    try:
        df = pd.json_normalize(batch)
        df.to_parquet(
            path=path,
            index=False,
            storage_options=STORAGE_OPTIONS,
        )
        logging.info(f"Загружен файл в S3-MinIO {path}.")
    except Exception as e:
        logging.error(e)


def consume_message(
        topic: str | None = None,
        stop_event: threading.Event | None = None,
        offset: int | None = None,
        batch_size: int | None = BATCH_SIZE
) -> None:
    """
    Функция считывает сообщения из топика с заданным оффсетом и выводит считанное сообщение в консоль.

    :param stop_event: Внешний stop_event.
    :param batch_size: Размер пакета.
    :param topic: Имя топика.
    :param offset: Оффсет.
    :return: None.
    """

    # Конфигурация Consumer
    conf = {
        "bootstrap.servers": "kafka:9092",
        "group.id": "s3",
        "auto.offset.reset": "earliest",
    }

    # Создаем Consumer
    consumer = Consumer(conf)

    if not topic:
        raise ValueError("Необходимо передать параметр topic.")

    if offset is not None:
        # Получаем список партиций топика.
        partitions = consumer.list_topics(topic).topics[topic].partitions
        for partition in partitions:
            # Ручное назначение топика, партиции и оффсета.
            consumer.assign([TopicPartition(topic, partition, offset)])
    else:
        # Обычная подписка на топик.
        consumer.subscribe([topic])

    batch = []
    try:
        while not stop_event or not stop_event.is_set():
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError:
                    logging.error("Reached end of partition.")
                else:
                    logging.error(f"Error: {msg.error()}")
            else:
                try:
                    event = json.loads(msg.value().decode("utf-8"))
                    logging.info(f"Получено сообщение {event}")
                except Exception as e:
                    logging.error(e)
                    continue
                batch.append(event)
                if len(batch) >= batch_size:
                    write_to_s3_minio(batch)
                    batch = []
    except KeyboardInterrupt:
        write_to_s3_minio(batch)
    finally:
        if batch:
            write_to_s3_minio(batch)
        consumer.close()


if __name__ == "__main__":
    consume_message(topic="my_topic")
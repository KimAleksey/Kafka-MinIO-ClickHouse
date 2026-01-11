import json
import logging

from confluent_kafka import Consumer, KafkaError, TopicPartition

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def consume_message(topic: str | None = None, offset: int | None = None) -> None:
    """
    Функция считывает сообщения из топика с заданным оффсетом и выводит считанное сообщение в консоль.

    :param topic: Имя топика.
    :param offset: Оффсет.
    :return: None.
    """

    # Конфигурация Consumer
    conf = {
        "bootstrap.servers": "localhost:19092",
        "group.id": "mygroup",
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

    try:
        while True:
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
                    raw = msg.value().decode("utf-8")
                    obj = json.loads(raw)
                    logging.info(f"Received message {obj}")
                except Exception as e:
                    logging.error(f"Error: {e}")
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    # Читаем с начала
    # consume_message("my_topic")

    # Читаем с определенного оффсета
    consume_message(topic="my_topic", offset=5)
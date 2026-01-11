import json
import threading
import time
import logging

from confluent_kafka import Producer
from codes.utils.utils import generate_new_user

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# Определяем конфигурацию Kafka Producer
conf = {
    "bootstrap.servers": "kafka:9092",
    "client.dns.lookup": "use_all_dns_ips",
}

# Создание экземпляр Producer с вышеупомянутыми настройками
producer = Producer(conf)

# RPS - интервал, с которым будут отправляться сообщения
interval = 1.0 / 1


def write_to_kafka(stop_event: threading.Event | None = None) -> None:
    """
    С заданным интервалом отправляет сообщение в topic.
    Сообщение содержит информацию о новом пользователе, которое было сгенерировано в отдельной функции.

    :return: None.
    """
    try:
        while not stop_event or not stop_event.is_set():
            start = time.perf_counter()
            user_data = generate_new_user()

            # Сериализация в JSON str
            user_data_json = json.dumps(user_data)

            # Отправляем сообщение в топик
            producer.produce(
                topic="my_topic",
                value=user_data_json,
            )

            # Ждем когда все сообщения в очереди Producer будут доставлены.
            producer.flush()

            logging.info(f"Данные отправлены в топик: {user_data_json}")

            # Спим пока не пройдет секунда с момента начала.
            end = time.perf_counter() - start
            sleet_time = max(0, interval - end)
            time.sleep(sleet_time)
    except KeyboardInterrupt:
        pass
    finally:
        logging.info("Завершен процесс отправки сообщений в Kafka.")


if __name__ == "__main__":
    write_to_kafka()
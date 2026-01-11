import time
import threading
import logging

from concurrent.futures import ThreadPoolExecutor

from codes.simple_producer import write_to_kafka
from codes.kafka_to_s3_minio import consume_message

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

stop_event = threading.Event()

def main():
    executor = ThreadPoolExecutor(max_workers=2)
    executor.submit(write_to_kafka, stop_event)
    executor.submit(consume_message, "my_topic", stop_event)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping...")
        stop_event.set()
        executor.shutdown(wait=True)
        logging.info("Stopped.")

if __name__ == "__main__":
    main()
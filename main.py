from codes.simple_producer import write_to_kafka


def main():
    while True:
        # Простая запись в topic
        write_to_kafka()

if __name__ == "__main__":
    main()
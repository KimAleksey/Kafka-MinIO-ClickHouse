import io
import boto3
import logging
import pandas as pd

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

STORAGE_OPTIONS = {
    "aws_access_key_id": "6yNqhb70NGHykaRP5KeM",
    "aws_secret_access_key": "Yw7DyDbWZftnQK3BzOUeI9d0L9GrVvvjp6eNQRST",
    "endpoint_url": "http://localhost:9000",
}

def read_data_from_s3(bucket_name: str | None = "my-bucket", filename: str | None = None) -> pd.DataFrame:
    """

    :param bucket_name: Имя bucket.
    :param filename: Имя файла, по-умолчанию считываются все
    :return:
    """
    # Подключение к S3 MinIO
    s3 = boto3.resource("s3", **STORAGE_OPTIONS)

    # Получаем объект Bucket
    bucket = s3.Bucket(bucket_name)

    # Если передано имя файла - считываем только его, иначе все файлы.
    files = []
    if not filename is None:
        files.append(filename)
    else:
        for file in bucket.objects.all():
            files.append(file.key)

    df = pd.DataFrame()
    for file in files:
        logging.info(f"Считываем данные файла: {file}.")
        # Буффер для хранения данных.
        buffer = io.BytesIO()
        # Объект в Bucket
        obj = s3.Object("my-bucket", file)
        # Скачиваем объект из S3 в бинарный объект buffer.
        obj.download_fileobj(buffer)
        # Считываем данные в DataFrame
        buffer.seek(0)
        # проверяем размер файла
        logging.info(f"Размер файла {file} в байтах: {len(buffer.getvalue())}")
        df_buff = pd.read_parquet(buffer)
        df = pd.concat([df, df_buff], axis=0, ignore_index=True)
    logging.info(f"Данные считаны в DataFrame.")
    logging.info(f"Количество считанных файлов: {len(files)}.")
    logging.info(f"Количество строк в итоговом DataFrame: {len(df)}")
    return df


if __name__ == "__main__":
    df = read_data_from_s3()
    with pd.option_context('display.max_columns', None, 'display.width', 1000):
        print(df.head(100000))
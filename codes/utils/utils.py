import uuid
import faker
import datetime

from typing import Any

def generate_new_user() -> dict[str, Any]:
    """
    Функция генерирует строку в формате словаря.
    Данная строка является имитацией данных нового пользователя.

    :return: Dict.
    """
    fake = faker.Faker(locale="ru_RU")

    result = {
        "user_id": str(uuid.uuid4()),
        "created_at": str(fake.date_time_ad(
            start_datetime=datetime.datetime(2022, 1, 1),
            end_datetime=datetime.datetime(2026, 1, 10),
        )),
        "username": fake.user_name(),
        "password": fake.password(),
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }

    return result


if __name__ == "__main__":
    print(generate_new_user())
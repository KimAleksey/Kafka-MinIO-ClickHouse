# Работа с Kafka

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
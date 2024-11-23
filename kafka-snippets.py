############################################################
# SECTION 1: DOCKER COMPOSE FOR KAFKA ECOSYSTEM
############################################################
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    hostname: zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
      ZOOKEEPER_SYNC_LIMIT: 2

  kafka:
    image: confluentinc/cp-kafka:latest
    hostname: kafka
    container_name: kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181

############################################################
# SECTION 2: PYTHON KAFKA PRODUCER
############################################################
from kafka import KafkaProducer
import json
import time

# Initialize producer with retry settings
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    acks='all',
    retries=3,
    retry_backoff_ms=1000,
    max_in_flight_requests_per_connection=1
)

# Example producer function
def send_to_kafka(topic, data):
    try:
        # Send data asynchronously
        future = producer.send(topic, value=data)
        # Wait for send to complete
        record_metadata = future.get(timeout=10)
        print(f"Message sent to topic {record_metadata.topic}, "
              f"partition {record_metadata.partition}, "
              f"offset {record_metadata.offset}")
    except Exception as e:
        print(f"Error sending message: {str(e)}")
    finally:
        producer.flush()

# Example usage
data = {"timestamp": time.time(), "value": "test_message"}
send_to_kafka("test_topic", data)
```

############################################################
# SECTION 3: PYTHON KAFKA CONSUMER
############################################################
```python
from kafka import KafkaConsumer
import json

# Initialize consumer with configuration
consumer = KafkaConsumer(
    'test_topic',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my_consumer_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    session_timeout_ms=30000,
    heartbeat_interval_ms=10000
)

# Consume messages
def consume_messages():
    try:
        for message in consumer:
            print(f"Topic: {message.topic}, "
                  f"Partition: {message.partition}, "
                  f"Offset: {message.offset}, "
                  f"Key: {message.key}, "
                  f"Value: {message.value}")
    except Exception as e:
        print(f"Error consuming message: {str(e)}")
    finally:
        consumer.close()
```

############################################################
# SECTION 4: PYSPARK STRUCTURED STREAMING WITH KAFKA
############################################################
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Initialize Spark with Kafka packages
spark = SparkSession.builder \
    .appName("KafkaStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()

# Define schema for your data
schema = StructType([
    StructField("timestamp", TimestampType(), True),
    StructField("value", StringType(), True)
])

# Read from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "test_topic") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# Process the stream
parsed_df = df.select(
    from_json(
        col("value").cast("string"),
        schema
    ).alias("data")
).select("data.*")

# Write stream to console (for testing)
query = parsed_df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()
```

############################################################
# SECTION 5: KAFKA ADMIN OPERATIONS
############################################################
```python
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

# Initialize admin client
admin_client = KafkaAdminClient(
    bootstrap_servers=['localhost:9092'],
    client_id='admin_client'
)

# Create topics
def create_topic(topic_name, num_partitions=3, replication_factor=1):
    try:
        topic_list = [
            NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor
            )
        ]
        admin_client.create_topics(new_topics=topic_list)
        print(f"Topic {topic_name} created successfully")
    except TopicAlreadyExistsError:
        print(f"Topic {topic_name} already exists")
    except Exception as e:
        print(f"Error creating topic: {str(e)}")

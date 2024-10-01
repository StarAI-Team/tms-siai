# from flask import Flask, jsonify
# import psycopg2
# import logging
# import os
# from confluent_kafka import Consumer
# from confluent_kafka.schema_registry.avro import AvroDeserializer
# from confluent_kafka.serialization import MessageField, SerializationContext
# from schema_registry_client import SchemaClient
# import utils
# import threading
# from bson import ObjectId 
# import logging_config

# app = Flask(__name__)

# # Initialize PostgreSQL connection
# conn = psycopg2.connect(
#     dbname=os.environ.get('POSTGRES_DB'),
#     user=os.environ.get('POSTGRES_USER'),
#     password=os.environ.get('POSTGRES_PASSWORD'),
#     host='db',
#     port='5432'
# )
# cur = conn.cursor()

# @app.before_first_request
# def start_consumer():
#     utils.load_env()
#     logging_config.configure_logging()

#     bootstrap_server = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
#     topic = os.environ.get("KAFKA_TOPIC")
#     group_id = os.environ.get("CONSUMER_GROUP_ID", "consumer-group-id")
#     schema_registry_url = os.environ.get("SCHEMA_REGISTRY_URL")
#     schema_type = "AVRO"

#     with open("./schemas/schema.avsc") as avro_schema_file:
#         avro_schema = avro_schema_file.read()
#     schema_client = SchemaClient(schema_registry_url, topic, avro_schema, schema_type)
#     schema_str = schema_client.get_schema_str()
    
#     consumer = Consumer({
#         "bootstrap.servers": bootstrap_server,
#         "group.id": group_id,
#         "auto.offset.reset": "earliest",
#     })
#     avro_deserializer = AvroDeserializer(schema_client.schema_registry_client, schema_str)
#     consumer.subscribe([topic])

#     def consume_messages():
#         try:
#             while True:
#                 msg = consumer.poll(1.0)
#                 if msg is None:
#                     continue
#                 if msg.error():
#                     logging.error(f"Consumer error: {msg.error()}")
#                     continue
#                 byte_message = msg.value()
#                 decoded_message = avro_deserializer(byte_message, SerializationContext(topic, MessageField.VALUE))
#                 logging.info(f"Decoded message: {decoded_message}, Type: {type(decoded_message)}")

#                 task_name = decoded_message['event_name'] if isinstance(decoded_message, dict) else decoded_message
#                 if task_name:
#                     logging.info(f"Received data for committing: {task_name}")
#                     insert_query = """
#                         INSERT INTO tasks (name)
#                         VALUES (%s)
#                         ON CONFLICT (name) DO NOTHING
#                     """
#                     cur.execute(insert_query, (task_name,))
#                     conn.commit()
#                     logging.info("Data inserted into PostgreSQL.")
#                 else:
#                     logging.warning("No valid task name received.")
#         except KeyboardInterrupt:
#             pass
#         finally:
#             consumer.close()

#     consumer_thread = threading.Thread(target=consume_messages)
#     consumer_thread.start()
#     logging.info("Consumer started automatically on application startup.")

# @app.route('/')
# def index():
#     cur.execute("SELECT * FROM tasks")
#     tasks = cur.fetchall()
#     return jsonify({"message": "Tasks:", "data": [{"id": t[0], "name": t[1]} for t in tasks]})

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=7000, debug=True)

from flask import Flask, jsonify
import psycopg2
import logging
import os
from confluent_kafka import Consumer
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import MessageField, SerializationContext
from schema_registry_client import SchemaClient
import utils
import threading
from bson import ObjectId 
import logging_config

app = Flask(__name__)

# Initialize PostgreSQL connection
conn = psycopg2.connect(
    dbname=os.environ.get('POSTGRES_DB'),
    user=os.environ.get('POSTGRES_USER'),
    password=os.environ.get('POSTGRES_PASSWORD'),
    host='db',
    port='5432'
)
cur = conn.cursor()

def init_database():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
    """)
    conn.commit()
    logging.info("Database and tables initialized successfully")

@app.before_first_request
def start_consumer():
    utils.load_env()
    logging_config.configure_logging()

    bootstrap_server = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
    topic = os.environ.get("KAFKA_TOPIC")
    group_id = os.environ.get("CONSUMER_GROUP_ID", "consumer-group-id")
    schema_registry_url = os.environ.get("SCHEMA_REGISTRY_URL")
    schema_type = "AVRO"

    with open("./schemas/schema.avsc") as avro_schema_file:
        avro_schema = avro_schema_file.read()
    schema_client = SchemaClient(schema_registry_url, topic, avro_schema, schema_type)
    schema_str = schema_client.get_schema_str()
    
    consumer = Consumer({
        "bootstrap.servers": bootstrap_server,
        "group.id": group_id,
        "auto.offset.reset": "earliest",
    })
    avro_deserializer = AvroDeserializer(schema_client.schema_registry_client, schema_str)
    consumer.subscribe([topic])

    def consume_messages():
        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logging.error(f"Consumer error: {msg.error()}")
                    continue
                byte_message = msg.value()
                decoded_message = avro_deserializer(byte_message, SerializationContext(topic, MessageField.VALUE))
                logging.info(f"Decoded message: {decoded_message}, Type: {type(decoded_message)}")

                task_name = decoded_message['event_name'] if isinstance(decoded_message, dict) else decoded_message
                if task_name:
                    logging.info(f"Received data for committing: {task_name}")
                    insert_query = """
                        INSERT INTO tasks (name)
                        VALUES (%s)
                        ON CONFLICT (name) DO NOTHING
                    """
                    cur.execute(insert_query, (task_name,))
                    conn.commit()
                    logging.info("Data inserted into PostgreSQL.")
                else:
                    logging.warning("No valid task name received.")
        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()

    consumer_thread = threading.Thread(target=consume_messages)
    consumer_thread.start()
    logging.info("Consumer started automatically on application startup.")

@app.route('/')
def index():
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    return jsonify({"message": "Tasks:", "data": [{"id": t[0], "name": t[1]} for t in tasks]})

if __name__ == '__main__':
    init_database()
    app.run(host="0.0.0.0", port=7000, debug=True)


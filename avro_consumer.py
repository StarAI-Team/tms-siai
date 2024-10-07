# import logging
# import os

# from confluent_kafka import Consumer
# from confluent_kafka.schema_registry.avro import AvroDeserializer
# from confluent_kafka.serialization import MessageField, SerializationContext

# import logging_config
# import utils
# from schema_registry_client import SchemaClient


# class AvroConsumerClass:
#     def __init__(
#         self, bootstrap_server, topic, group_id, schema_registry_client, schema_str
#     ):
#         """Initializes the consumer."""
#         self.bootstrap_server = bootstrap_server
#         self.topic = topic
#         self.group_id = group_id
#         self.consumer = Consumer(
#             {
#                 "bootstrap.servers": bootstrap_server,
#                 "group.id": self.group_id,
#                 "auto.offset.reset": "earliest",
#             }
#         )
#         self.schema_registry_client = schema_registry_client
#         self.schema_str = schema_str
#         self.avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)

#     def consume_messages(self):
#         """Consume Messages from Kafka."""
#         self.consumer.subscribe([self.topic])
#         logging.info(f"Successfully subscribed to topic: {self.topic}")

#         try:
#             while True:
#                 msg = self.consumer.poll(1.0)
#                 if msg is None:
#                     continue
#                 if msg.error():
#                     logging.error(f"Consumer error: {msg.error()}")
#                     continue
#                 byte_message = msg.value()
#                 decoded_message = self.avro_deserializer(
#                     byte_message, SerializationContext(topic, MessageField.VALUE)
#                 )
#                 logging.info(
#                     f"Decoded message: {decoded_message}, Type: {type(decoded_message)}"  # noqa: E501
#                 )
#         except KeyboardInterrupt:
#             pass
#         finally:
#             self.consumer.close()


# if __name__ == "__main__":
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

#     # Schema already in Schema Registry, So fetch from Schema Registry
#     schema_str = schema_client.get_schema_str()
#     consumer = AvroConsumerClass(
#         bootstrap_server,
#         topic,
#         group_id,
#         schema_client.schema_registry_client,
#         schema_str,
#     )
#     consumer.consume_messages()

from flask import Flask, jsonify
import threading
import logging
import os
import psycopg2
from confluent_kafka import Consumer
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import MessageField, SerializationContext
from pymongo import MongoClient 
from bson import ObjectId 
import logging_config
import utils
from schema_registry_client import SchemaClient

app = Flask(__name__)

client = MongoClient(host='test_mongodb',port=27017, username='root', password='pass',authSource="admin") 
db = client.mytododb 
tasks_collection = db.tasks 

class AvroConsumerClass:
    def __init__(self, bootstrap_server, topic, group_id, schema_registry_client, schema_str):
        """Initializes the consumer."""
        self.bootstrap_server = bootstrap_server
        self.topic = topic
        self.group_id = group_id
        self.consumer = Consumer(
            {
                "bootstrap.servers": bootstrap_server,
                "group.id": self.group_id,
                "auto.offset.reset": "earliest",
            }
        )
        self.schema_registry_client = schema_registry_client
        self.schema_str = schema_str
        self.avro_deserializer = AvroDeserializer(schema_registry_client, schema_str)
        self.running = False


    def consume_messages(self):
        """Consume Messages from Kafka."""
        self.consumer.subscribe([self.topic])
        logging.info(f"Successfully subscribed to topic: {self.topic}")
        self.running = True

        try:
            while self.running:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logging.error(f"Consumer error: {msg.error()}")
                    continue
                byte_message = msg.value()
                decoded_message = self.avro_deserializer(
                    byte_message, SerializationContext(self.topic, MessageField.VALUE)
                )
                logging.info(f"Decoded message: {decoded_message}, Type: {type(decoded_message)}")

                # coonect to Postgres macro database
                # Insert message into PostgreSQL database
                try:
                    task_name = decoded_message 
                    if task_name: 
                        logging.info(f"recieved data for commiting. {task_name}")
                        tasks_collection.insert_one({'name': task_name}) 
                    logging.info("Data inserted into Mongodb.")
                except Exception as e:
                    logging.error(f"Error inserting data into Mongodb: {e}")
                    self.conn.rollback()
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    def start(self):
        """Start the consumer in a separate thread."""
        self.thread = threading.Thread(target=self.consume_messages)
        self.thread.start()

    def stop(self):
        """Stop the consumer."""
        self.running = False
        self.thread.join()

consumer_instance = None

@app.before_first_request
def start_consumer():
    global consumer_instance
    if consumer_instance is None:
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
        
        consumer_instance = AvroConsumerClass(
            bootstrap_server,
            topic,
            group_id,
            schema_client.schema_registry_client,
            schema_str,
        )
        consumer_instance.start()
        logging.info("Consumer started automatically on application startup.")

# @app.teardown_appcontext
# def shutdown_consumer(exception=None):
#     global consumer_instance
#     if consumer_instance:
#         consumer_instance.stop()
#         consumer_instance = None
#         logging.info("Consumer stopped on application shutdown.")

@app.route('/')
def index():
    tasks = tasks_collection.find() 
    logging.info(f"tasts>>> {tasks}")
    return jsonify({"message": "Kafka consumer is running."})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000, debug=True)

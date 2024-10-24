from flask import Flask, request, jsonify
import logging
import os
import psycopg2
from psycopg2 import OperationalError  
from uuid import uuid4
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    StringSerializer,
)
import logging_config
import utils
from admin import Admin
from producer import ProducerClass
from schema_registry_client import SchemaClient
from confluent_kafka import KafkaException

app = Flask(__name__)

# # Initialize PostgreSQL connection
# def create_connection():
#     # try:
#     conn = psycopg2.connect(
#         dbname=os.environ.get('POSTGRES_DB'),
#         user=os.environ.get('POSTGRES_USER'),
#         password=os.environ.get('POSTGRES_PASSWORD'),
#         host='db',
#         port='5432'
#     )
#     return conn
# # except OperationalError as e:
#         # logging.error(f"Could not connect to the database: {e}")
#         # return None

# def init_database():
#     conn = create_connection()
#     if conn is None:
#         logging.error("Database connection was not established.")
#         return

#     try:
#         with conn.cursor() as cur:
#             # Create client table
#             cur.execute("""
#                 CREATE TABLE IF NOT EXISTS client (
#                     id SERIAL PRIMARY KEY,
#                     company_email TEXT UNIQUE NOT NULL,
#                     company_location TEXT UNIQUE NOT NULL,
#                     company_name TEXT UNIQUE NOT NULL,
#                     first_name TEXT NOT NULL,
#                     id_number TEXT UNIQUE NOT NULL,
#                     last_name TEXT NOT NULL,
#                     phone_number TEXT UNIQUE NOT NULL,
#                     registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#                 );
#             """)
#             logging.info("client table initialized successfully")

#             # Create user table
#             cur.execute("""
#                 CREATE TABLE IF NOT EXISTS user (
#                     id SERIAL PRIMARY KEY,
#                     username TEXT UNIQUE NOT NULL,
#                     email TEXT UNIQUE NOT NULL,
#                     password TEXT NOT NULL,
#                     registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#                 );
#             """)
#             logging.info("user table initialized successfully")

#         conn.commit()  # Commit the changes
#     except Exception as e:
#         logging.error(f"An error occurred while initializing the database: {e}")
#     finally:
#         conn.close()  # Ensure the connection is closed

# Configure MinIO client
from minio import Minio
from minio.error import S3Error

minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Ensure bucket exists
bucket_name = "uploads"
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

@app.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Save the file to MinIO
    try:
        file_path = file.filename
        minio_client.put_object(
            bucket_name, 
            file_path, 
            file.stream, 
            length=-1, 
            part_size=10*1024*1024,  # 10MB part size
            content_type=file.mimetype
        )
        # Generate file URL
        file_url = f"http://minio:9000/{bucket_name}/{file_path}"
        return file_url, 200
    except S3Error as e:
        return f"Failed to upload file: {e}", 500

class AvroProducer(ProducerClass):
    def __init__(
        self,
        bootstrap_server,
        topic,
        schema_registry_client,
        schema_str,
        compression_type=None,
        message_size=None,
        batch_size=None,
        waiting_time=None,
    ):
        super().__init__(
            bootstrap_server,
            topic,
            compression_type,
            message_size,
            batch_size,
            waiting_time,
        )
        self.schema_registry_client = schema_registry_client
        self.schema_str = schema_str
        print(self.schema_str)
        self.avro_serializer = AvroSerializer(schema_registry_client, schema_str)
        self.string_serializer = StringSerializer("utf-8")

    def send_message(self, key=None, value=None):
        try:
            if value:
                logging.info(f"*** {value}")
                byte_value = self.avro_serializer(
                    value, SerializationContext(self.topic, MessageField.VALUE)
                )
            else:
                byte_value = None
            self.producer.produce(
                topic=self.topic,
                key=self.string_serializer(str(key)),
                value=byte_value,
                headers={"correlation_id": str(uuid4())},
                on_delivery=delivery_report,
            )
            logging.info("Message Successfully Produced by the Producer")
        except KafkaException as e:
            kafka_error = e.args[0]
            if kafka_error.MSG_SIZE_TOO_LARGE:
                logging.error(
                    f"{e} , Current Message size is {len(value) / (1024 * 1024)} MB"
                )
        except Exception as e:
            logging.error(f"Error while sending message: {e}")

def delivery_report(err, msg):
    if err is not None:
        logging.error(
            f"Delivery failed for record with key {msg.key()} with error {err}"
        )
        return
    logging.info(
        f"Successfully produced record: key - {msg.key()}, topic - {msg.topic}, partition - {msg.partition()}, offset - {msg.offset()}"
    )

@app.route('/process_user', methods=['POST'])
def process_user():
    try:
        # Receive JSON payload from request
        user_data = request.get_json()
        logging.info(f"test: {user_data}")

        if not user_data:
            return jsonify({"error": "No data received"}), 400
        
        # Generate a unique ID if not provided in the JSON
        user_data['user_id'] = 1
        user_id = user_data['user_id']

        # if field is a file, store in file server and sned url to kafka instead
        logging.info(f"user data: {user_data}")

        # Produce message to Kafka
        
        producer.send_message(key=user_id, value=user_data)

        return jsonify({"status": "success", "user_id": user_id}), 200

    except Exception as e:
        logging.error(f"Error processing user data: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # init_database()
    utils.load_env()
    logging_config.configure_logging()

    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
    topic = os.environ.get("KAFKA_TOPIC")
    schema_registry_url = os.environ.get("SCHEMA_REGISTRY_URL")
    schema_type = "AVRO"

    # Create Topic
    admin = Admin(bootstrap_servers)
    admin.create_topic(topic, 2)

    # Register the Schema
    with open("./schemas/schema.avsc") as avro_schema_file:
        avro_schema = avro_schema_file.read()

    schema_client = SchemaClient(schema_registry_url, topic, avro_schema, schema_type)
    schema_client.set_compatibility("BACKWARD")
    schema_client.register_schema()

    # Fetch schema_str from Schema Registry
    schema_str = schema_client.get_schema_str()

    # Initialize producer
    producer = AvroProducer(
        bootstrap_servers,
        topic,
        schema_client.schema_registry_client,
        schema_str,
        compression_type="snappy",
        message_size=3 * 1024 * 1024,
        batch_size=10_00_00,
        waiting_time=10_000,
    )

    # Start Flask app
    app.run(host="0.0.0.0", port=6000)

# from flask import Flask, jsonify
# import psycopg2
# from psycopg2 import OperationalError  
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
#                     if task_name == "transporterRegistration(Basic Details)":
#                         logging.info(f"Received data for committing: {task_name}")
                        
#                         user_id = decoded_message["user_id"]
#                         company_email = decoded_message["company_email"]
#                         company_name = decoded_message["company_name"]
#                         company_location = decoded_message["company_location"]
#                         first_name = decoded_message["first_name"]
#                         id_number = decoded_message["id_number"]
#                         last_name = decoded_message["last_name"]
#                         phone_number = decoded_message["phone_number"]

#                         conn = create_connection()
#                         with conn.cursor() as cur:
#                             insert_query = """
#                                 INSERT INTO client (user_id, company_email, company_name, company_location, first_name, id_number, last_name, phone_number)
#                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                                 ON CONFLICT (company_email) DO NOTHING
#                             """

#                             # Execute the insert with all values
#                             cur.execute(insert_query, (user_id, company_email, company_name, company_location, first_name, id_number, last_name, phone_number))
#                             conn.commit()
#                             logging.info("Data inserted into client.")
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
#     conn = create_connection()
#     with conn.cursor() as cur:
#         cur.execute("SELECT * FROM client")
#         tasks = cur.fetchall()
#         return jsonify({"message": "Tasks:", "data": [{"id": t[0], "name": t[1]} for t in tasks]})

# if __name__ == '__main__':
#     # init_database()
#     app.run(host="0.0.0.0", port=7000, debug=True)

from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import OperationalError  
import logging
import os
from confluent_kafka import Consumer
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import MessageField, SerializationContext
from schema_registry_client import SchemaClient
import utils
import threading
# from bson import ObjectId 
import logging_config
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'starinternational_key' 
csrf = CSRFProtect(app)

# Initialize PostgreSQL connection
def create_connection():
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host='db',
        port='5432'
    )
    return conn

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
                    if task_name == "transporterRegistration_Representative Details":
                        logging.info(f"Received data for committing: {task_name}")
                        
                        user_id = decoded_message["user_id"]
                        company_email = decoded_message["company_email"]
                        company_name = decoded_message["company_name"]
                        company_location = decoded_message["company_location"]
                        first_name = decoded_message["first_name"]
                        id_number = decoded_message["id_number"]
                        last_name = decoded_message["last_name"]
                        phone_number = decoded_message["phone_number"]

                        conn = create_connection()
                        with conn.cursor() as cur:
                            insert_query = """
                                INSERT INTO transporter (user_id, company_email, company_name, company_location, first_name, id_number, last_name, phone_number)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (company_email) DO NOTHING
                            """

                            # Execute the insert with all values
                            cur.execute(insert_query, (user_id, company_email, company_name, company_location, first_name, id_number, last_name, phone_number))
                            conn.commit()
                            logging.info("Data inserted into transporter.")
                            

                            # return response to client (succefful insertion or cokmpany already exists)
                    if task_name == "transporterRegistration_Company Details":
                        user_id  = decoded_message["user_id"]
                        account_name = decoded_message["account_name"]
                        account_number = decoded_message["account_number"]
                        bank_name = decoded_message["bank_name"]
                        company_contact = decoded_message["company_contact"]
                        directorship = decoded_message["directorship"]
                        proof_of_current_address = decoded_message["proof_of_current_address"]

                        conn = create_connection()
                        with conn.cursor() as cur:
                            insert_query = """
                                INSERT INTO transporter_account_information (user_id, account_name, account_number, bank_name, company_contact, directorship, proof_of_current_address)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (user_id) DO NOTHING
                            """

                            # Execute the insert with all values
                            cur.execute(insert_query, (user_id, account_name,  account_number, bank_name, company_contact, directorship, proof_of_current_address))
                            conn.commit()
                            logging.info("transporterRegistration_Company Details inserted")

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
    conn = create_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM transporter")
        tasks = cur.fetchall()
        return jsonify({"message": "Tasks:", "data": [{"id": t[0], "name": t[1]} for t in tasks]})

@app.route('/api/v1/client', methods=['GET'])
@csrf.exempt
def get_client_data():
    conn = create_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM client")
        tasks = cur.fetchall()
        return jsonify({"message": "Client Data:", "data": [{"id": t[0], "name": t[1]} for t in tasks]})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000, debug=True)

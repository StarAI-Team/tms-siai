set -a
source .env

exec python3 ./avro_producer.py &
exec python3 ./avro_consumer.py
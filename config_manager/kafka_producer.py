
import json
import logging
from kafka import KafkaProducer
from django.conf import settings

# Set up a logger for this module
logger = logging.getLogger(__name__)


def get_kafka_producer():
    """Initializes and returns a KafkaProducer instance."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        return producer
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer: {e}")
        return None

def publish_config_update(config_name, config_value):
    """
    Publishes a message to the Kafka topic about a config update.
    """
    producer = get_kafka_producer()
    if not producer:
        logger.error("Kafka producer is not available. Cannot publish message.")
        return

    message = {
        'name': config_name,
        'value': config_value
    }
    
    try:
        producer.send(settings.KAFKA_CONFIG_TOPIC, value=message)
        producer.flush() # Ensure all messages are sent before exiting
        logger.info(f"Successfully published update for config: {config_name}")
    except Exception as e:
        logger.error(f"Failed to publish config update for '{config_name}': {e}")
    finally:
        producer.close()
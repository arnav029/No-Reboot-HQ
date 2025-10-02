import threading
import time
import requests
import json
from kafka import KafkaConsumer

# --- Configuration ---
CONFIG_API_URL = "http://127.0.0.1:8000/api/configs/"
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
KAFKA_CONFIG_TOPIC = 'config_updates'

# In-memory store for our application's configurations.
# In a real app, this might be a more sophisticated config object.
config_store = {}

def fetch_initial_config():
    """
    Fetches the full set of active configurations from the API on startup.
    """
    global config_store
    try:
        response = requests.get(CONFIG_API_URL)
        response.raise_for_status()  # Raises an exception for bad status codes
        
        configs = response.json()
        temp_store = {c['name']: c['value'] for c in configs}
        config_store = temp_store
        
        print("✅ Successfully fetched initial configurations.")
        print(f"   Current Configs: {config_store}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not fetch initial configurations from API: {e}")

def start_kafka_listener():
    """
    Starts a Kafka consumer in a background thread to listen for config updates.
    """
    print("👂 Starting Kafka listener...")
    consumer = KafkaConsumer(
        KAFKA_CONFIG_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='latest', # Start reading at the end of the topic
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    
    for message in consumer:
        update_data = message.value
        config_name = update_data.get('name')
        config_value = update_data.get('value')

        if config_name and config_name in config_store:
            print(f"\n🔄 Received update for '{config_name}': Old value '{config_store[config_name]}', New value '{config_value}'")
            # Update the in-memory store
            config_store[config_name] = config_value
        else:
            print(f"\n✨ Received new config '{config_name}': Value '{config_value}'")
            config_store[config_name] = config_value




if __name__ == "__main__":
    fetch_initial_config()

    kafka_thread = threading.Thread(target=start_kafka_listener, daemon=True)
    kafka_thread.start()
    
    print("\n🚀 Main application is running. Monitoring config changes...")
    print("---------------------------------------------------------")
    try:
        while True:

            heartbeat_msg = config_store.get('heartbeat_message', 'System running...')
            
            if config_store.get('enable_greeting', False):
                print(f"\r   [Heartbeat] {heartbeat_msg} - Hello! The time is {time.strftime('%H:%M:%S')}", end="")
            else:
                print(f"\r   [Heartbeat] {heartbeat_msg}", end="")
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down client application.")
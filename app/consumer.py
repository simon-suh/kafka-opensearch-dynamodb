import json
from confluent_kafka import Consumer, KafkaError
from opensearchpy import OpenSearch
import boto3

# --- Kafka Consumer Configuration ---
kafka_conf = {
    'bootstrap.servers': 'localhost:29092',  # External listener for host machine access
    'group.id': 'events-consumer-group',     # Consumer group ID — tracks offset per group
    'auto.offset.reset': 'earliest'          # Start reading from beginning if no offset exists
}

# Create Kafka consumer instance
consumer = Consumer(kafka_conf)

# Subscribe to the events topic
consumer.subscribe(['events'])

# --- OpenSearch Configuration ---
# Uses localhost because consumer runs on host machine, not inside a container
os_client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    use_ssl=False,
    verify_certs=False
)

# --- DynamoDB Configuration ---
# boto3 automatically uses credentials from ~/.aws/credentials
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Reference to the events table provisioned via Terraform
table = dynamodb.Table('events')

print('Consumer started. Waiting for messages...')

try:
    while True:
        # Poll Kafka for new messages
        # 1.0 = wait up to 1 second for a message before continuing the loop
        msg = consumer.poll(1.0)

        # No message received within the poll timeout — keep looping
        if msg is None:
            continue

        # Check for Kafka errors
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # Reached end of partition — not an error, just no new messages
                print('End of partition reached')
            else:
                print(f'Error: {msg.error()}')
            continue

        # Decode the message value from bytes to a Python dictionary
        event = json.loads(msg.value().decode('utf-8'))
        print(f'Received event: {event}')

        # --- Write to OpenSearch ---
        os_client.index(
            index='events',        # OpenSearch index name
            body=event             # Event data to index
        )
        print(f'Written to OpenSearch: event_id {event["event_id"]}')

        # --- Write to DynamoDB ---
        table.put_item(Item={
            'id': str(event['event_id']),  # DynamoDB requires hash key as string
            'timestamp': event['@timestamp'],
            'message': event['message'],
            'status': event['status'],
            'service': event['service']
        })
        print(f'Written to DynamoDB: event_id {event["event_id"]}')

# Gracefully handle Ctrl+C to stop the consumer
except KeyboardInterrupt:
    print('Consumer stopped.')

finally:
    # Always close the consumer to release resources and commit offsets
    consumer.close()
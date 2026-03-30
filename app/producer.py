import time
import json
from confluent_kafka import Producer

# Kafka configuration
conf = {
    'bootstrap.servers': 'localhost:29092'
}

# Create producer instance
producer = Producer(conf)

# Callback function - confirms message was delivered or reports error
def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} partition {msg.partition()}')

# Generate and send 10 test events
for i in range(10):
    event = {
        '@timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'event_id': i,
        'message': f'Test event {i}',
        'status': 'success',
        'service': 'producer'
    }

    producer.produce(
        topic='events',
        value=json.dumps(event).encode('utf-8'),
        callback=delivery_report
    )

    # Poll to trigger delivery callbacks
    producer.poll(0)
    time.sleep(1)

# Wait for all messages to be delivered
producer.flush()
print('All messages sent.')
'''Test calls to RabbitMQ'''

import json
import pytest
import pika
from netx_to_emu_mq import publish_to_rabbitmq, rmq_host, rmq_port, rmq_que

@pytest.fixture
def rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='0.0.0.0',
                                                                   port=rmq_port))
    channel = connection.channel()
    channel.queue_declare(queue=rmq_que)
    yield channel
    channel.queue_delete(queue=rmq_que)
    connection.close()

def test_publish_to_rabbitmq(rabbitmq_connection):
    message = {'key': 'value'}
    message_str = json.dumps(message)
    
    publish_to_rabbitmq(message_str)
    
    method_frame, header_frame, body = rabbitmq_connection.basic_get(queue=rmq_que, auto_ack=True)
    assert method_frame is not None
    assert json.loads(body) == message

if __name__ == '__main__':
    pytest.main()
'''Test calls to RabbitMQ'''

import json
import pytest
import pika
from netx_to_emu_mq import publish_to_rabbitmq, rmq_host, rmq_port, rmq_que, rmq_cred

@pytest.fixture
def rabbitmq_connection():
    '''setup a rabbitMQ connection'''
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rmq_host,
                                                                   port=rmq_port,
                                                                   credentials=rmq_cred))
    channel = connection.channel()
    channel.queue_declare(queue=rmq_que)
    yield channel
    channel.queue_delete(queue=rmq_que)
    connection.close()

def test_publish_to_rabbitmq(rabbitmq_connection):
    '''test-publish a message to rabbitMQ'''
    message = {'key': 'value'}
    message_str = json.dumps(message)

    publish_to_rabbitmq(message_str)

    method_frame, header_frame, body = rabbitmq_connection.basic_get(queue=rmq_que, auto_ack=True)
    assert method_frame is not None
    assert json.loads(body) == message

if __name__ == '__main__':
    pytest.main()
    
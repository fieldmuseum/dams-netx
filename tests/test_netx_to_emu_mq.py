'''Test rabbit MQ functions '''

import json
from unittest.mock import patch, MagicMock
import pika
import pytest
from netx_to_emu_mq import app, publish_to_rabbitmq
from dotenv import dotenv_values

config = dotenv_values('.env')
test_rmq_host = config['RABBITMQ_HOST']
test_rmq_port = config['RABBITMQ_PORT']
test_rmq_exch = config['RABBITMQ_EXCHANGE']
test_rmq_que = config['RABBITMQ_QUEUE']
test_rmq_key = config['RABBITMQ_ROUTING_KEY']
test_rmq_id = config['RABBITMQ_USER_ID'],
test_rmq_pw = config['RABBITMQ_USER_PW']

@pytest.fixture
def client():
    '''
    mockup test where properly-constructed msg gets to rabbitmq
    '''
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        yield testing_client

def test_handle_webhook_success(client):
    '''test if a successful call of handle_webhook() returns `200` status and json'''
    payload = {'key': 'value'}

    with patch('netx_to_emu_mq.publish_to_rabbitmq') as mock_publish:
        mock_publish.return_value = None

        response = client.post('/webhook',
                               data = json.dumps(payload),
                               content_type = 'application/json')
        assert response.status_code == 200
        assert response.json == {'status':'success', 'message':'Message sent to RabbitMQ'}

def test_handle_webhook_invalid_payload(client):
    '''test if an invalid call of handle_webhook() returns `400` status and error-json'''
    response = client.post('/webhook', data='invalid json', content_type='application/json')
    print('\n ~ ')
    print(response.headers)
    print('\n ~ ')
    print(response.status)
    print('\n ~ ')
    print(response.text)

    assert response.status_code == 400
    assert response.text == '''<!doctype html>
<html lang=en>
<title>400 Bad Request</title>
<h1>Bad Request</h1>
<p>The browser (or proxy) sent a request that this server could not understand.</p>
'''
    # assert response.text == {'status': 'error',
    #                          'message': 'The browser (or proxy) sent a request that this server could not understand'}

def test_publish_to_rabbitmq():
    '''test publishing a message to rabbitMQ queue'''
    message = json.dumps({'key': 'value'})

    with patch('pika.BlockingConnection') as mock_connection:
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel

        publish_to_rabbitmq(message=message,
                            rmq_host='localhost',
                            rmq_port=8080,
                            rmq_exch='',
                            rmq_que='test_queue',
                            rmq_key='test_queue',
                            rmq_cred=pika.PlainCredentials(test_rmq_id, test_rmq_pw))

        mock_connection.assert_called_once_with(pika.ConnectionParameters(host='localhost', port=8080))
        mock_channel.queue_declare.assert_called_once_with(queue='test_queue')
        mock_channel.basic_publish.assert_called_once_with(exchange='',
                                                           routing_key='test_queue',
                                                           body=message)
        mock_connection.return_value.close.assert_called_once()
        print('--- test ---')
        print(mock_channel[1])
        print('--- test ---')

def test_publish_to_rabbitmq_real():
    '''test publishing a message to rabbitMQ queue'''
    message = json.dumps({'key': 'value'})

    # with patch('pika.BlockingConnection') as mock_connection:
        # mock_channel = MagicMock()
        # mock_connection.return_value.channel.return_value = mock_channel

    app.run(host='0.0.0.0', port=8080, ssl_context="adhoc")

    test = publish_to_rabbitmq(message=message,
                                rmq_host='0.0.0.0', # test_rmq_host,
                                rmq_port=8080, # test_rmq_port,
                                rmq_exch=test_rmq_exch,
                                rmq_que=test_rmq_que,
                                rmq_key=test_rmq_key)

    print('--- live ---')
    print(test)
    print('--- live ---')

    # mock_connection.assert_called_once_with(pika.ConnectionParameters(host=test_rmq_host))
    # mock_channel.queue_declare.assert_called_once_with(queue=test_rmq_que)
    # mock_channel.basic_publish.assert_called_once_with(exchange=test_rmq_exch,
    #                                                    routing_key=test_rmq_key,
    #                                                    body=message)
    # mock_connection.return_value.close.assert_called_once()

if __name__ == '__main__':
    pytest.main()

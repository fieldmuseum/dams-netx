'''Tools for handling rabbitMQ messages'''

import pika
from dotenv import dotenv_values

def get_live_or_test_rmq(env:str='LIVE'):
    '''select live or test rabbitMQ environemt'''

    config = dotenv_values('.env')
    rmq_config = {}

    if env == 'LIVE':
        rmq_config = {
            'HOST' : config['RABBITMQ_HOST'],
            'PORT' : config['RABBITMQ_PORT'],
            'EXCHANGE' :config['RABBITMQ_EXCHANGE'],
            'QUEUE' : config['RABBITMQ_QUEUE'],
            'ROUTING_KEY' : config['RABBITMQ_ROUTING_KEY'],
            'credentials' : pika.PlainCredentials(config['RABBITMQ_USER_ID'],
                                        config['RABBITMQ_USER_PW']),
            'env' : env
        }

    else:
        rmq_config = {
            'HOST' : config['TEST_RABBITMQ_HOST'],
            'PORT' : config['TEST_RABBITMQ_PORT'],
            'EXCHANGE' :config['TEST_RABBITMQ_EXCHANGE'],
            'QUEUE' : config['TEST_RABBITMQ_QUEUE'],
            'ROUTING_KEY' : config['TEST_RABBITMQ_ROUTING_KEY'],
            'credentials' : pika.PlainCredentials(config['TEST_RABBITMQ_USER_ID'],
                                        config['TEST_RABBITMQ_USER_PW']),
            'env' : env,
        }

    return rmq_config

def publish_to_rabbitmq(message:str='', env:str='LIVE'):
    '''
    Connect and publish a message to rabbitMQ.
    Given a message (formatted as JSON) and env (LIVE or TEST),
    Returns a connection to a rabbitMQ queue
    '''

    rmq_config = get_live_or_test_rmq(env)

    print(rmq_config)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rmq_config['HOST'],
                                  port=rmq_config['PORT'],
                                  virtual_host='/',
                                  credentials=rmq_config['credentials']))


    print(connection)
    channel = connection.channel()
    channel.queue_declare(queue=rmq_config['QUEUE'], durable=True)
    channel.basic_publish(exchange=rmq_config['EXCHANGE'],
                          routing_key=rmq_config['ROUTING_KEY'],
                          body=message)

    connection.close()

'''
Test RabbitMQ basic 
https://www.rabbitmq.com/tutorials/tutorial-one-python
'''

import pika
from dotenv import dotenv_values

config = dotenv_values('.env')
rmq_creds = pika.PlainCredentials(
    username=config['TEST_RABBITMQ_USER_ID'],
    password=config['TEST_RABBITMQ_USER_PW']
    )

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=config['TEST_RABBITMQ_HOST'],
        port=config['TEST_RABBITMQ_PORT'],
        credentials=rmq_creds
        )
    )

channel = connection.channel()

channel.queue_declare(queue='rabbit-test')

channel.basic_publish(exchange='', routing_key='rabbit-test', body='Test rabbit blabla')
print(" [x] Sent 'Test rabbit blabla'")
connection.close()

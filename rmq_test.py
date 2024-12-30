'''
Test RabbitMQ basic 
https://www.rabbitmq.com/tutorials/tutorial-one-python
'''

import pika
from dotenv import dotenv_values

config = dotenv_values('.env')
rmq_creds = pika.PlainCredentials(
    username=config['RABBITMQ_USER_ID'],
    password=config['RABBITMQ_USER_PW']
    )

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='0.0.0.0',
        port=5672,
        credentials=rmq_creds
        )
    )

channel = connection.channel()

channel.queue_declare(queue='rabbit-test')

channel.basic_publish(exchange='', routing_key='rabbit-test', body='Test rabbit blabla')
print(" [x] Sent 'Test rabbit blabla'")
connection.close()

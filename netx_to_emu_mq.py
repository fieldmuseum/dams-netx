'''Handle NetX webhooks via RabbitMQ'''

import json
import pika
from flask import Flask, request, jsonify
from dotenv import dotenv_values

app = Flask(__name__)

# RabbitMQ connection setup
config = dotenv_values('.env')
webhook_url = config['WEBHOOK_URL']
webhook_port = config['WEBHOOK_PORT']
rmq_host = config['RABBITMQ_HOST']
rmq_port = config['RABBITMQ_PORT']
rmq_exch = config['RABBITMQ_EXCHANGE']
rmq_que = config['RABBITMQ_QUEUE']
rmq_key = config['RABBITMQ_ROUTING_KEY']
rmq_cred = pika.PlainCredentials(config['RABBITMQ_USER_ID'],
                                 config['RABBITMQ_USER_PW'])

def publish_to_rabbitmq(message='',
                        rmq_host=rmq_host,
                        rmq_port=rmq_port,
                        rmq_exch=rmq_exch,
                        rmq_que=rmq_que,
                        rmq_key=rmq_key,
                        rmq_cred=rmq_cred):
    '''publish a message to rabbitMQ'''
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rmq_host,
                                  port=rmq_port,
                                  credentials=rmq_cred))
    channel = connection.channel()
    channel.queue_declare(queue=rmq_que)
    channel.basic_publish(exchange=rmq_exch, routing_key=rmq_key, body=message)
    print(channel)
    connection.close()
    # return channel

@app.route('/webhook', methods=['POST'])
def handle_webhook():

    # '''Receive JSON payload from NetX'''
    # print(f"Headers: {request.headers}")
    # print(f"Body: {request.get_data()}")    
    # data = request.get_json()

    # Mockup for a start
    # # # # #
    netx_example = {
        "event": {
            "assetId": 101,
            "systemEventType": "ASSET_CREATE",
            "eventId": "0c218a59-8d6c-4c20-b5fe-372f75162d13",
            "eventTime": 1674076946,
            "userId": 1
        },
        "token": "6od7VUynjVQbDgLUdzeNvc5KuRs",
        "messageTime": 1674076946,
        "messageId": "78480073-b8d2-4494-85a9-638f5a15e409",
        "subscriptionId": 201
        }
    data = json.dumps(netx_example)
    # # # # Mockup # # # #

    print(data)

    # if data:
    # Publish to RabbitMQ
    publish_to_rabbitmq(json.dumps(data))
    webhook_msg = {'status':'success','message': 'Message sent to RabbitMQ'}
    return jsonify(webhook_msg), 200
    # else:
    #     webhook_msg = {'status':'error','message': 'Invalid payload'}
    #     return jsonify(webhook_msg), 400

    # try:
    #     publish_to_rabbitmq(json.dumps(data))
    # except Exception as e:
    #     app.logger.error(f"Failed to publish message: {e}")
    #     return jsonify({'status': 'error', 'message': 'Failed to process webhook'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=webhook_port, ssl_context="adhoc")

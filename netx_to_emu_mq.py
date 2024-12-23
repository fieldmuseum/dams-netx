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
rmq_exch = config['RABBITMQ_EXCHANGE']
rmq_que = config['RABBITMQ_QUEUE']

def publish_to_rabbitmq(message):
    '''publish a message to rabbitMQ'''
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=rmq_que)
    channel.basic_publish(exchange='', routing_key=rmq_que, body=message)
    connection.close()

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    '''Receive JSON payload from NetX'''
    print(f"Headers: {request.headers}")
    print(f"Body: {request.get_data()}")    
    data = request.get_json()
    if data:
        # Publish to RabbitMQ
        publish_to_rabbitmq(json.dumps(data))
        webhook_msg = {'status':'success','message': 'Message sent to RabbitMQ'}
        return jsonify(webhook_msg), 200
    else:
        webhook_msg = {'status':'error','message': 'Invalid payload'}
        return jsonify(webhook_msg), 400

    # try:
    #     publish_to_rabbitmq(json.dumps(data))
    # except Exception as e:
    #     app.logger.error(f"Failed to publish message: {e}")
    #     return jsonify({'status': 'error', 'message': 'Failed to process webhook'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=webhook_port)

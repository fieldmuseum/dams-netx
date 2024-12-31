'''Handle NetX webhooks via RabbitMQ'''

import json
from flask import Flask, request, jsonify
from dotenv import dotenv_values
import utils.rabbit_tools as ur

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    '''Receive JSON payload from NetX'''

    print(f"Headers: {request.headers}")
    print(f"Body: {request.get_data()}")
    data = None

    if request.is_json:
        data = request.get_json()

    else:
        print('Not json')
        data = request.get_data()

    print(data)

    if data:

        # Publish to RabbitMQ
        try:
            ur.publish_to_rabbitmq(json.dumps(data))
            webhook_msg = {'status':'success','message':'Message sent to RabbitMQ'}
            return jsonify(webhook_msg), 200

        except Exception as e:
            app.logger.exception("Failed to publish message: %s", e)
            return jsonify({'status': 'error', 'message': 'Failed to process webhook'}), 500

    else:
        webhook_msg = {'status':'error','message':'Invalid payload'}
        return jsonify(webhook_msg), 400


if __name__ == '__main__':
    config = dotenv_values('.env')
    app.run(host='0.0.0.0',
            port=config['WEBHOOK_PORT'],
            # ssl_context="adhoc"
            )

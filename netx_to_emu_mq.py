'''Handle NetX webhooks via RabbitMQ'''

import json
from flask import Flask, request, jsonify
from dotenv import dotenv_values
import utils.rabbit_tools as ur

app = Flask(__name__)

config = dotenv_values('.env')

@app.route('/webhook', methods=['GET'])
def handle_webhook():
    '''Receive JSON payload from NetX'''

    print("Headers: {'Content-Type': 'text/plain'}")  #  {request.headers}")
    print(f"Body: {request.get_data()}")
    data = None

    if request.is_json:
        data = request.get_json()

    else:
        print('Not json')
        data = request.get_data()

    print(data)

    if data:

        rmq_env = config['RMQ_ENV']

        # Publish to RabbitMQ
        try:
            ur.publish_to_rabbitmq(json.dumps(data), env=rmq_env)
            webhook_msg = {'status':'success','message':'Message sent to RabbitMQ'}
            print(webhook_msg)
            return jsonify(webhook_msg), 200

        except Exception as e:
            app.logger.exception("Failed to publish message: %s", e)
            print(f"Failed to publish message: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to process webhook'}), 500

    else:
        webhook_msg = {'status':'error','message':'Invalid payload'}
        return jsonify(webhook_msg), 400


if __name__ == '__main__':
    config = dotenv_values('.env')
    app.run(host='0.0.0.0',
            port=config['WEBHOOK_PORT'],
            # debug=True,
            # ssl_context="adhoc"
            )

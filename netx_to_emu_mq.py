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

    # # Mockup for a start
    # # # # # #
    # netx_example = {
    #     "event": {
    #         "assetId": 101,
    #         "systemEventType": "ASSET_CREATE",
    #         "eventId": "0c218a59-8d6c-4c20-b5fe-372f75162d13",
    #         "eventTime": 1674076946,
    #         "userId": 1
    #     },
    #     "token": "6od7VUynjVQbDgLUdzeNvc5KuRs",
    #     "messageTime": 1674076946,
    #     "messageId": "78480073-b8d2-4494-85a9-638f5a15e409",
    #     "subscriptionId": 201
    #     }
    # data = json.dumps(netx_example)
    # # # # # Mockup # # # #

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
            ssl_context="adhoc"
            )

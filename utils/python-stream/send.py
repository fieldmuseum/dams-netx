'''
Test RabbitMQ stream
from: https://www.rabbitmq.com/tutorials/tutorial-one-python-stream
'''

import asyncio
from dotenv import dotenv_values
from rstream import Producer

config = dotenv_values('.env')

STREAM_NAME = "test-python-stream"
# 5GB
STREAM_RETENTION = 5000000000

async def send():
    async with Producer(
        host=config['TEST_RABBITMQ_HOST'],
        username=config['TEST_RABBITMQ_USER_ID'],
        password=config['TEST_RABBITMQ_USER_PW'],
    ) as producer:

        await producer.create_stream(
                    STREAM_NAME, exists_ok=True, arguments={"max-length-bytes": STREAM_RETENTION}
                    )

        await producer.send(stream=STREAM_NAME, message=b"Hello, World!")

        print(" [x] Test message bla bla")

        input(" ... Hit Enter to close the producer ...")

with asyncio.Runner() as runner:
    runner.run(send())
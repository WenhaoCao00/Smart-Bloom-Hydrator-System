from hbmqtt.broker import Broker
import asyncio

broker_config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '127.0.0.1:1883',
        }
    },
    'sys_interval': 10,
    'auth': {
        'allow-anonymous': True
    }
}

broker = Broker(broker_config)

async def start_broker():
    await broker.start()

loop = asyncio.get_event_loop()
loop.run_until_complete(start_broker())
loop.run_forever()

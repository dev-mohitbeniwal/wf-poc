from pyzeebe import ZeebeClient, create_insecure_channel, ZeebeWorker
from os import environ

if environ.get('ZEEBE_ADDRESS', '') == '':
    print("ZEEBE_ADDRESS is not set, defaulting to 0.0.0.0:26500")

channel = create_insecure_channel()
client = ZeebeClient(channel)
worker = ZeebeWorker(channel)
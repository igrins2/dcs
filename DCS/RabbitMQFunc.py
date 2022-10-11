# -*- coding: utf-8 -*-

"""
Created on Sep 2, 2022

Modified on , 2022

@author: hilee
"""

# RabbitMQ communication

import pika

def connect_to_server(host_ip, id, password):

    id_pwd = pika.PlainCredentials(id, password)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host_ip, port=5672, credentials=id_pwd))
    channel = connection.channel()

    return channel


# as producer
def define_producer(channel, _exchange, _type):
    
    channel.exchange_declare(exchange=_exchange, exchange_type=_type)


# as consumer
def binding(channel, _exchange, _type, _routing_key):
    
    channel.exchange_declare(exchange=_exchange, exchange_type=_type)
    result = channel.queue_declare(queue='', exclusive=True)
    queue = result.method.queue
    channel.queue_bind(exchange=_exchange, queue=queue, routing_key=_routing_key)

    return queue


    


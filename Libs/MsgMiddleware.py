# -*- coding: utf-8 -*-

"""
Created on Nov 22, 2022

Modified on Nov 22, 2022

@author: hilee, Francisco
"""

import pika

# RabbitMQ communication
class MsgMiddleware():
    
    def __init__(self, iam, ip_addr, id, pwd, exchange, type, producer = False):
        
        self.iam = iam
        self.ip_addr = ip_addr
        self.id = id
        self.pwd = pwd
        
        self.exchange = exchange
        self.type = type
        self.producer = producer
        
        self.channel = None
        self.connection = None
        
        self.queue = None
        
        
    def __del__(self):
        if self.producer:
            print('Closed rabbitmq queue and connections (producer)')
        else:
            print('Closed rabbitmq queue and connections (consumer)')
        if self.queue:
            self.channel.stop_consuming()    
            self.connection.close()
                    

    def connect_to_server(self):
        try:       
            id_pwd = pika.PlainCredentials(self.id, self.pwd)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.ip_addr, port=5672, credentials=id_pwd, heartbeat=0, tcp_options={"TCP_KEEPIDLE":60}))
            self.channel = self.connection.channel()
            
        except Exception as ex:
            print(self.iam, "cannot connect to RabbitMQ server.\r\nPlease check the server and try again!")
            print (ex)
            raise 

        
    # as producer
    def define_producer(self):
        try:
            self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.type)
                    
        except Exception as e:
            print(self.iam, "cannot define producer.\r\nPlease check the server and try again!")
            print (e)
            raise
        
    
    def send_message(self, target, _routing_key, _message):
        try:
            self.channel.basic_publish(exchange=self.exchange, routing_key=_routing_key, body=_message.encode())
            msg = '[%s->%s] %s' % (self.iam, target, _message)
            print(msg)
        except Exception as e:
            print("Cannot send the {_message} for the {_routing_key} provider.")
            print(e)
            raise
            
    
    # as consumer
    def define_consumer(self, _routing_key, _callback):
        if self.producer:
            return
        
        try:
            #if self.queue is None:
            self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.type)
            result = self.channel.queue_declare(queue='', exclusive=True)
            self.queue = result.method.queue
            print(f"queueName= {self.queue}")
            
            #self.connection.add_timeout(0.5, _callback)
            self.connection.add_callback_threadsafe(_callback)
            self.channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=_routing_key)
            #self.channel.basic_consume(queue=self.queue, on_message_callback=_callback, auto_ack=True)
            
        except Exception as e:
            print(self.iam, "cannot define consumer for the {_routing_key} provider.")
            print(e)
            raise 
        
        
    def start_consumer(self):
        if self.producer:
            return
        
        try:
            if self.queue:
                self.channel.start_consuming()
        except Exception as e:
            print("Error starting consuming msg")
            print(e)
            raise
        
    '''    
    def stop_consumer(self):
        if self.producer:
            return
        
        try:
            if self.queue:
                #print('q 1')
                self.connection.close()
                self.channel.stop_consuming()
                self.queue = None
        except Exception as e:
            print("Error stopping consuming msg")
            print(e)
            raise
    '''

        

    
        

            
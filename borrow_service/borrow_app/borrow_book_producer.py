import pika
import json
from decouple import config


def BookProducer(book):
    print("BookProducer")
    amqp_url = config("RABBITMQ")  # Use your environment variable for the AMQP URL
    connection = pika.BlockingConnection(pika.URLParameters(amqp_url))
    channel = connection.channel()
    channel.queue_declare(queue="borrow_book_queue")
    channel.basic_publish(
        exchange="borrow_book_exchange",
        routing_key="borrow_book_queue",
        body=json.dumps({"book_id": book}),
    )
    print(f" [x] Book request published: {book}")
    connection.close()

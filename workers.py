import os
import dramatiq
import logging
import json
from dotenv import load_dotenv
from redis import Redis
from dramatiq.brokers.redis import RedisBroker
from odoo_rpc_client import Client

load_dotenv()

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

# configure message broker
dramatiq_broker = RedisBroker(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=False
)
dramatiq.set_broker(dramatiq_broker)

# configure direct redis connection for results
cache_db = Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

# configure odoo connection client
odoo = Client(
    host=os.getenv('ODOO_RPC_HOST'),
    port=int(os.getenv('ODOO_RPC_PORT')),
    dbname=os.getenv('ODOO_RPC_DB'),
    user=os.getenv('ODOO_RPC_USER'),
    pwd=os.getenv('ODOO_RPC_PASS'),
    protocol='json-rpc' if os.getenv('ODOO_RPC_HOST') in ['localhost', '127.0.0.1'] else 'json-rpcs'
)


@dramatiq.actor(queue_name='inbound')
def create_inbound_order(*args, **kwargs):
    _logger.info(f'Creating inbound order for request')
    try:
        # execute operation
        odoo['stock.picking'].create_inbound_order([], **kwargs)
        # write successful result to a redis db
        cache_db.set(f"inbound:{kwargs.get('uuid')}", json.dumps({
            'uuid': kwargs.get('uuid'),
            'state': 'draft'
        }))
    except Exception as e:
        _logger.error(str(e))
        raise e
    return None


# if __name__ == '__main__':
#     data = {
#         "uuid": str(uuid4()),
#         "partner_id": 23,
#         "reference": "20240423/04",
#         "inbound_date": "2024-04-26",
#         "representative_name": "",
#         "representative_tel": "",
#         "products": [
#             {
#                 "default_code": "ART123123",
#                 "barcode": "801212002022",
#                 "name": "Назва першого товару",
#                 "description": "Короткий опис товару",
#                 "quantity": 4,
#                 "price": 0.0
#             },
#         ]
#     }
#     create_inbound_order.send(**data)

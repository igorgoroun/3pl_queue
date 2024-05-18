import os
import bjoern
import dramatiq
from dotenv import load_dotenv
from dramatiq.brokers.redis import RedisBroker
from dramatiq_dashboard import DashboardApp

load_dotenv()

broker = RedisBroker(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    username=os.getenv("REDIS_USER"),
    password=os.getenv("REDIS_PASSWORD")
)

broker.declare_queue("default")
broker.declare_queue("inbound")
broker.declare_queue("outbound")
broker.declare_queue("invoicing")
broker.declare_queue("stock")

dramatiq.set_broker(broker)
app = DashboardApp(broker=broker, prefix="")
bjoern.run(app, os.getenv("DASH_BINDING_HOST"), int(os.getenv("DASH_BINDING_PORT")))


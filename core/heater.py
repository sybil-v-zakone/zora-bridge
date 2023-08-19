import random

from config import eth_rpc, sleep_time
from core.client import ZoraBridgeClient
from utils import generate_pairs, sleep
from loguru import logger


class Heater:
    def __init__(self):
        self.data = generate_pairs()

    def warmup(self):
        while len(self.data) > 0:
            active_wallet = random.choice(list(self.data))

            client = ZoraBridgeClient(rpc=eth_rpc, private_key=active_wallet)

            try:
                tx_res, tx_message = client.bridge(self.data[active_wallet])

                if tx_res:
                    logger.success(tx_message)

                    self.data.pop(active_wallet)

                    sleep(sleep_time)
                else:
                    logger.error(tx_message)

            except Exception as ex:
                logger.error(ex)
        else:
            logger.success("Script has ended its work.")

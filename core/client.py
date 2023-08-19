from models.client_base import ClientBase
from utils import *
from constants import *
from config import gas_threshold, gas_delay_range


class ZoraBridgeClient(ClientBase):
    def __init__(self, rpc: str, private_key: str):
        super().__init__(rpc=rpc, private_key=private_key)

        self.zora_bridge = self.w3.eth.contract(
            address=ZORA_BRIDGE_ADDRESS,
            abi=ZORA_BRIDGE_ABI
        )

    @gas_delay(gas_threshold=gas_threshold, delay_range=gas_delay_range)
    def bridge(self, amount: float) -> tuple[bool, str]:
        value = ETH_TOKEN.to_wei(amount)

        eth_balance = ETH_TOKEN.from_wei(self.w3.eth.get_balance(self.public_key))
        if eth_balance < amount:
            log_to_file(LOW_BALANCES_FILE, self.private_key)
            return False, f"Insufficient balance to bridge: {eth_balance} < {amount}\nSkipping wallet"

        data = self.zora_bridge.encodeABI('depositTransaction', args=(
            self.public_key,
            value,
            GAS_LIMIT,
            IS_CREATION,
            '0x'
        ))

        tx = self.send_tx(to_adr=ZORA_BRIDGE_ADDRESS, value=value, data=data)
        if self.verify_tx(tx):
            return (True, (
                f"Successfuly bridged {amount} {ETH_TOKEN.signature}\n "
                f"https://etherscan.io/tx/{tx.hex()}"))

        log_to_file(TX_ERRORS_FILE, self.private_key)
        return False, f"Failed to bridge {amount} {ETH_TOKEN.signature} "

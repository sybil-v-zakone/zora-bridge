from web3 import Web3
from web3.contract import Contract
from web3.middleware import geth_poa_middleware
from models.token import Token
from loguru import logger
from utils import sleep
from config import eth_rpc, gas_multiplier


class ClientBase:
    def __init__(self, rpc: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        self.private_key = private_key
        self.public_key = Web3.to_checksum_address(self.w3.eth.account.from_key(private_key=private_key).address)

    def send_tx(
            self,
            to_adr: str,
            from_adr: str = None,
            data=None,
            value=None
    ):
        if not from_adr:
            from_adr = self.public_key

        txn = {
            "chainId": self.w3.eth.chain_id,
            "nonce": self.w3.eth.get_transaction_count(self.public_key),
            "from": Web3.to_checksum_address(from_adr),
            "to": Web3.to_checksum_address(to_adr),
            # "maxPriorityFeePerGas": self.w3.eth.max_priority_fee,
            # "maxFeePerGas": self.w3.eth.gas_price
        }

        gas_params = self.get_eip1559_params()
        txn['maxPriorityFeePerGas'] = gas_params[0]
        txn['maxFeePerGas'] = gas_params[1]

        if data:
            txn["data"] = data

        if value:
            txn["value"] = value

        try:
            txn["gas"] = int(self.w3.eth.estimate_gas(txn) * gas_multiplier)
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            return None

        sign = self.w3.eth.account.sign_transaction(txn, self.private_key)
        return self.w3.eth.send_raw_transaction(sign.rawTransaction)

    def get_eip1559_params(self) -> tuple[int, int]:
        w3 = Web3(provider=Web3.HTTPProvider(endpoint_uri=eth_rpc))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        last_block = w3.eth.get_block("latest")
        max_priority_fee_per_gas = self.get_max_priority_fee_per_gas(w3=w3, block=last_block)
        base_fee = int(last_block["baseFeePerGas"] * gas_multiplier)
        max_fee_per_gas = base_fee + max_priority_fee_per_gas
        return max_priority_fee_per_gas, max_fee_per_gas

    @staticmethod
    def get_max_priority_fee_per_gas(w3: Web3, block: dict) -> int:
        block_number = block["number"]
        latest_block_transaction_count = w3.eth.get_block_transaction_count(block_number)
        max_priority_fee_per_gas_list = []
        for i in range(latest_block_transaction_count):
            try:
                transaction = w3.eth.get_transaction_by_block(block_number, i)
                if "maxPriorityFeePerGas" in transaction:
                    max_priority_fee_per_gas_list.append(transaction["maxPriorityFeePerGas"])
            except Exception as e:
                continue

        if not max_priority_fee_per_gas_list:
            max_priority_fee_per_gas = w3.eth.max_priority_fee
        else:
            max_priority_fee_per_gas_list.sort()
            max_priority_fee_per_gas = max_priority_fee_per_gas_list[len(max_priority_fee_per_gas_list) // 2]
        return max_priority_fee_per_gas

    def verify_tx(self, tx_hash) -> bool:
        try:
            data = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)
            if "status" in data and data["status"] == 1:
                return True
            else:
                logger.error(f'Transaction failed: {data["transactionHash"].hex()}')
                return False
        except Exception as e:
            logger.error(f"Unexpected error in verify_tx function: {e}")
            return False

    def get_allowance(self, token_contract: Contract, spender: str, owner: str = None):
        if not owner:
            owner = self.public_key

        return token_contract.functions.allowance(owner, spender).call()

    def balance_of(self, token: Token):
        return int(self.w3.eth.contract(
            address=token.contract_address,
            abi=token.abi
        ).functions.balanceOf(self.public_key).call())

    def approve(self, spender: str, token: Token, value: int):
        if token.is_native:
            return True

        contract = self.w3.eth.contract(address=token.contract_address, abi=token.abi)

        allowance = self.get_allowance(token_contract=contract, spender=spender)
        if allowance >= value:
            logger.info(f"Allowance is greater than approve value. {allowance} >= {value}")
            return True

        data = contract.encodeABI("approve", args=(spender, value))
        tx_hash = self.send_tx(contract.address, data=data)
        if self.verify_tx(tx_hash=tx_hash):
            logger.success(f"Successful approve: {allowance} {token.signature}")
            sleep([10, 15])
            return True
        logger.warning("Error while approving transaction")
        return False

import os
import json

from models.token import Token

LOW_BALANCES_FILE = "errors/low_balances.txt"
TX_ERRORS_FILE = "errors/tx_errors.txt"

ZORA_BRIDGE_ADDRESS = "0x1a0ad011913A150f69f6A19DF447A0CfD9551054"
ZORA_BRIDGE_ABI = json.load(open(os.path.abspath("abis/zora_bridge.json")))

GAS_LIMIT = 100000

IS_CREATION = False

ETH_TOKEN = Token(
    contract_address="0xc3761EB917CD790B30dAD99f6Cc5b4Ff93C4F9eA",
    abi=json.load(open(os.path.abspath("abis/erc20.json"))),
    decimals=18,
    signature="ETH",
    is_native=True
)

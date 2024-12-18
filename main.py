import os
from dotenv import load_dotenv
from web3 import Web3

from scripts import (
    get_current_markets_data,
    get_current_tvl,
    read_constants,
    round_up,
    recalculate_max_market,
)

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("POLYNOMIAL_RPC")))
w3t = Web3(Web3.HTTPProvider(os.getenv("POLYNOMIAL_SEP_RPC")))

constants = read_constants()
current_tvl = round_up(get_current_tvl(), 5)
market_data, current_prices, raw_data = get_current_markets_data()

updated_market_data = recalculate_max_market(
    market_data, current_prices, constants, current_tvl, True
)

for market_id, data in updated_market_data.items():
    print(market_id, data.max_market_value, data.max_market_size)

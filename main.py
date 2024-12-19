import os
from dotenv import load_dotenv
from web3 import Web3
from binance import Client

from scripts import (
    calculate_new_market_values,
    get_current_markets_data,
    get_current_tvl,
    read_constants,
    rewrite_all,
    round_up,
    recalculate_max_market,
    get_new_market_id,
    add_new_market,
    generate_toml_new_market,
)

load_dotenv()

client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

constants = read_constants()
current_tvl = round_up(get_current_tvl(), 5)
market_data, current_prices, raw_data = get_current_markets_data()

updated_market_data, max_market_value_each = recalculate_max_market(
    market_data, current_prices, constants, current_tvl, True
)

new_market_id = get_new_market_id(market_data)

market_name = input("Enter market name (e.g. 'Pudgy Penguins'): ")
market_ticker = input("Enter market ticker (e.g. 'PUDGY'): ")
print("Get feed id from https://pyth.network/developers/price-feed-ids")
feed_id = input(
    "Enter Pyth feed id (e.g. '0x9a4df90b25497f66b1afb012467e316e801ca3d839456db028892fe8c70c8016'): "
)
print()
print("Calculating new market values...")
print("=================================")

new_market_info = calculate_new_market_values(
    market_ticker,
    market_name,
    max_market_value_each,
    feed_id,
    new_market_id,
    client,
)

mainnet_new_market = add_new_market(new_market_info)
testnet_new_market = add_new_market(new_market_info, True)

generate_toml_new_market(new_market_info, mainnet_new_market)
generate_toml_new_market(new_market_info, testnet_new_market, True)

print()
print("=================================")
print("Done!")

print()
print("Repopulating existing markets...")
rewrite_all(raw_data, updated_market_data)

print()
print("=================================")
print("Done!")

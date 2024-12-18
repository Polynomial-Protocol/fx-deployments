import glob
import os
import re
from dataclasses import dataclass
import tomli
from pythclient.hermes import HermesClient
import asyncio


data_path = "polynomial-mainnet/tomls/polynomial-mainnet-andromeda/perps"


@dataclass
class MarketData:
    feed_id: str
    max_market_size: float
    max_market_value: int
    skew_scale: int
    max_funding_velocity: int
    name: str


def get_current_markets_data():
    feed_ids_reverse = {}
    current_prices = {}
    market_data = {}
    raw_data = {}
    feedRegex = ".*FeedId.*"
    marketRegex = ".*MarketId.*"
    skew_scale_regex = ".*SkewScale.*"
    max_funding_velocity_regex = ".*MaxFundingVelocity.*"
    max_market_size_regex = ".*MaxMarketSize.*"
    max_market_value_regex = ".*MaxMarketValue.*"
    invoke_files = glob.glob(f"{data_path}/*-invokes.toml")

    for invoke_file in invoke_files:
        data_file = invoke_file.replace("-invokes.toml", ".toml")
        name = data_file.split("/")[-1].split(".")[0]
        with open(data_file, "rb") as f:
            data = tomli.load(f)
            raw_data[market_id] = data
            data = data["setting"]
            feed_id = [
                v["defaultValue"] for k, v in data.items() if re.match(feedRegex, k)
            ][0]
            market_id = [
                v["defaultValue"] for k, v in data.items() if re.match(marketRegex, k)
            ][0]

            skew_scale = int(extract_val(data, skew_scale_regex))
            max_funding_velocity = int(extract_val(data, max_funding_velocity_regex))
            max_market_size = float(extract_val(data, max_market_size_regex))
            max_market_value = int(extract_val(data, max_market_value_regex))

            market_data[market_id] = MarketData(
                feed_id=feed_id,
                max_market_size=max_market_size,
                max_market_value=max_market_value,
                skew_scale=skew_scale,
                max_funding_velocity=max_funding_velocity,
                name=name,
            )
            feed_ids_reverse[feed_id] = market_id

    feed_ids_list = list(feed_ids_reverse.keys())
    hermes_client = HermesClient(feed_ids_list, os.getenv("HERMES_RPC"))
    prices_latest = asyncio.run(hermes_client.get_all_prices(version=1))

    for feed_id, price_data in prices_latest.items():
        feed_id = "0x" + feed_id
        price_str = price_data["price"].price
        price_expo = price_data["price"].expo
        current_price = float(price_str) * (10**price_expo)
        current_prices[feed_ids_reverse[feed_id]] = current_price

    return market_data, current_prices, raw_data


def extract_value(value: str):
    return (
        value["defaultValue"]
        .replace("<%= String(", "")
        .replace(") %>", "")
        .replace("_", "")
    )


def extract_val(data: dict, regex: str):
    return [extract_value(v) for k, v in data.items() if re.match(regex, k)][0]

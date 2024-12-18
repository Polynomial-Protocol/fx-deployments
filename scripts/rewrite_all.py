from . import rewrite_toml
from . import replace_market_data


def rewrite_all(raw_data, market_data):
    raw_data = replace_market_data(raw_data, market_data)
    for market_id in raw_data.keys():
        rewrite_toml(raw_data[market_id])

import re
import tomli_w


def rewrite_toml(raw_data):
    data = raw_data["setting"]
    max_market_value_regex = ".*MaxMarketValue.*"
    key = [k for k in data.keys() if re.match(max_market_value_regex, k)][0]
    market_name = key.replace("perps", "").replace("MaxMarketValue", "").lower()
    with open(
        f"polynomial-sepolia/tomls/polynomial-sepolia-andromeda/perps/{market_name}.toml",
        "wb",
    ) as f:
        tomli_w.dump(raw_data, f)
    with open(
        f"polynomial-mainnet/tomls/polynomial-mainnet-andromeda/perps/{market_name}.toml",
        "wb",
    ) as f:
        tomli_w.dump(raw_data, f)

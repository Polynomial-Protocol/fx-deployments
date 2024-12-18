import tomli_w


def generate_toml_new_market(market_info, market_config, is_testnet=False):
    if is_testnet:
        with open(
            f"polynomial-sepolia/tomls/polynomial-sepolia-andromeda/perps/{market_info['ticker']}.toml",
            "wb",
        ) as f:
            tomli_w.dump(market_config["values"], f)
        with open(
            f"polynomial-sepolia/tomls/polynomial-sepolia-andromeda/perps/{market_info['ticker']}-invokes.toml",
            "wb",
        ) as f:
            tomli_w.dump(market_config["invokes"], f)
        with open(
            f"polynomial-sepolia/tomls/oracles/pyth-{market_info['ticker']}.toml",
            "wb",
        ) as f:
            tomli_w.dump(market_config["oracle"], f)
    else:
        with open(
            f"polynomial-mainnet/tomls/polynomial-mainnet-andromeda/perps/{market_info['ticker']}.toml",
            "wb",
        ) as f:
            tomli_w.dump(market_config["values"], f)
        with open(
            f"polynomial-mainnet/tomls/polynomial-mainnet-andromeda/perps/{market_info['ticker']}-invokes.toml",
            "wb",
        ) as f:
            tomli_w.dump(market_config["invokes"], f)
        with open(
            f"polynomial-mainnet/tomls/oracles/pyth-{market_info['ticker']}.toml",
            "wb",
        ) as f:
            tomli_w.dump(market_config["oracle"], f)

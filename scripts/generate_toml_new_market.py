import tomli
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

        with open(
            f"polynomial-sepolia/cannonfile.toml",
            "rb",
        ) as f:
            data = tomli.load(f)
            include = data["include"]
            include.append(
                f"tomls/polynomial-sepolia-andromeda/perps/{market_info['ticker']}-invokes.toml"
            )
            include.append(f"tomls/oracles/pyth-{market_info['ticker']}.toml")
            include.append(
                f"tomls/polynomial-sepolia-andromeda/perps/{market_info['ticker']}.toml"
            )
            data["include"] = include
            with open(
                f"polynomial-sepolia/cannonfile.toml",
                "wb",
            ) as f:
                tomli_w.dump(data, f)
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

        with open(
            f"polynomial-mainnet/cannonfile.toml",
            "rb",
        ) as f:
            data = tomli.load(f)
            include = data["include"]
            include.append(
                f"tomls/polynomial-mainnet-andromeda/perps/{market_info['ticker']}-invokes.toml"
            )
            include.append(f"tomls/oracles/pyth-{market_info['ticker']}.toml")
            include.append(
                f"tomls/polynomial-mainnet-andromeda/perps/{market_info['ticker']}.toml"
            )
            data["include"] = include
            with open(f"polynomial-mainnet/cannonfile.toml", "wb") as f:
                tomli_w.dump(data, f)

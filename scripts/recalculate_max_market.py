def recalculate_max_market(
    market_data, current_prices, constants, current_tvl, new_market=False
):
    total_market_value = 0
    for data in market_data.values():
        total_market_value += data.max_market_value

    reserved = sum(constants["max_market_value"].values()) * total_market_value
    reserved_markets = len(constants["max_market_value"])
    total_markets = len(market_data)
    if new_market:
        total_markets += 1

    remainder = current_tvl - reserved
    max_market_value_each = remainder / (total_markets - reserved_markets)

    for market_id, data in market_data.items():
        if market_id in constants["max_market_value"].keys():
            data.max_market_value = (
                constants["max_market_value"][market_id] * current_tvl
            )
            data.max_market_size = round(
                data.max_market_value / current_prices[market_id], 2
            )
        else:
            data.max_market_value = max_market_value_each
            data.max_market_size = round(
                data.max_market_value / current_prices[market_id], 2
            )
    return market_data, max_market_value_each

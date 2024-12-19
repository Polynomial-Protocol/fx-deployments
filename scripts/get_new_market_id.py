def get_new_market_id(market_data):
    next_market_id = 1000
    for market_id in market_data.keys():
        if int(market_id) > next_market_id:
            next_market_id = int(market_id)
    return str(next_market_id + 100)

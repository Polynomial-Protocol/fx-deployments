from binance import Client


def get_depth(ticker: str, client: Client):
    ob = client.get_order_book(symbol=ticker, limit=1000)
    price = (float(ob["bids"][0][0]) + float(ob["asks"][0][0])) / 2
    high_ask = price * 1.02
    low_bid = price * 0.98
    # Sum the liquidity till low_bid
    liquidity_bids = 0
    liquidity_asks = 0
    for bid in ob["bids"]:
        liquidity_bids += float(bid[1]) * float(bid[0])
        if float(bid[0]) <= low_bid:
            break
    for ask in ob["asks"]:
        liquidity_asks += float(ask[1]) * float(ask[0])
        if float(ask[0]) >= high_ask:
            break

    average_depth = (liquidity_bids + liquidity_asks) / 2

    return average_depth

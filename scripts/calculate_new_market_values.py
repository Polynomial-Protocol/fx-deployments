import asyncio
import os
from pythclient.hermes import HermesClient

from . import get_depth
from .calculate_skew_scale import calculate_skew_scale


def calculate_new_market_values(
    ticker,
    name,
    max_market_value_each,
    feed_id,
    market_id,
    binance_client,
    is_binance=True,
    default_depth=200000.0,
):
    hermes_client = HermesClient([feed_id], os.getenv("HERMES_RPC"))
    prices_latest = asyncio.run(hermes_client.get_all_prices(version=1))
    price = prices_latest[feed_id[2:]]["price"].price
    price_expo = prices_latest[feed_id[2:]]["price"].expo
    current_price = float(price) * (10**price_expo)

    tier_constant = 50

    if is_binance:
        average_depth = get_depth(ticker + "USDT", binance_client)
    else:
        average_depth = default_depth

    skew_scale = calculate_skew_scale(ticker, current_price, binance_client)
    max_market_size = max_market_value_each / current_price
    inverse_leverage = 0.05
    maintenance_margin_scalar = 0.317

    min_margin = 50
    expected_lev = 18
    notional = 10000
    size_10k = notional / current_price
    # impact_on_skew_10k = size_10k / skew_scale
    # expected_imr_10k = 1.00 / 18.00
    initial_margin_ratio = (skew_scale / size_10k) * (
        (((notional / expected_lev) - min_margin) / notional) - inverse_leverage
    )

    print(f"Market name: {name}")
    print(f"Ticker: {ticker}")
    print(f"Market id: {market_id}")
    print(f"Feed id: {feed_id}")
    print(f"Current price (Pyth): {'${:,.4f}'.format(current_price)}")
    print(f"Max market value: {'${:,.2f}'.format(max_market_value_each)}")
    print(f"Max market size: {'{:,.4f}'.format(max_market_size)}")
    print(f"Average depth: {'${:,.2f}'.format(average_depth)}")
    print(f"Skew scale: {skew_scale}")
    print(f"Minimum initial margin ratio: {inverse_leverage}")
    print(f"Maintenance margin scalar: {maintenance_margin_scalar}")
    print(f"Initial margin ratio: {initial_margin_ratio}")

    return {
        "name": name,
        "ticker": ticker.lower(),
        "market_id": market_id,
        "feed_id": feed_id,
        "skew_scale": skew_scale,
        "max_market_size": max_market_size,
        "max_market_value": max_market_value_each,
        "initial_margin_ratio": initial_margin_ratio,
        "maintenance_margin_scalar": maintenance_margin_scalar,
        "inverse_leverage": inverse_leverage,
    }

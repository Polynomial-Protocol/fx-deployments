from binance import Client
import pandas as pd


def calculate_slippage(symbol, order_size_usd, side="buy"):
    """
    Calculate slippage for a large order in Binance

    Parameters:
    - symbol: Trading pair (e.g., "BTCUSDT")
    - order_size_usd: Order size in USD
    - side: "buy" or "sell"

    Returns:
    - Slippage information dictionary
    """
    # Initialize Binance client (no API key needed for public endpoints)
    client = Client("", "")

    try:
        # Get order book data
        depth = client.get_order_book(symbol=symbol, limit=5000)

        # Get current price (mid price)
        ticker = client.get_ticker(symbol=symbol)
        best_ask = float(ticker["askPrice"])
        best_bid = float(ticker["bidPrice"])
        current_price = (best_ask + best_bid) / 2

        # Process order book data
        if side.lower() == "buy":
            # For buy orders, we'll walk through the asks
            orders = depth["asks"]
        else:
            # For sell orders, we'll walk through the bids
            orders = depth["bids"]

        # Convert to DataFrame for easier processing
        df = pd.DataFrame(orders, columns=["price", "quantity"])
        df["price"] = df["price"].astype(float)
        df["quantity"] = df["quantity"].astype(float)

        # Calculate values for each level
        df["notional"] = df["price"] * df["quantity"]
        df["cumulative_notional"] = df["notional"].cumsum()
        df["cumulative_quantity"] = df["quantity"].cumsum()

        # Check if order book has enough liquidity
        total_available = df["notional"].sum()
        if total_available < order_size_usd:
            print(
                f"Warning: Order book has only ${total_available:,.2f} available, not enough to fill ${order_size_usd:,.2f}"
            )
            filled_size = total_available
        else:
            filled_size = order_size_usd

        # Find all levels needed to fill the order
        df_needed = df[df["cumulative_notional"] <= filled_size].copy()

        # Calculate the partial fill at the next level
        if len(df_needed) < len(df) and filled_size > (
            df_needed["cumulative_notional"].iloc[-1] if not df_needed.empty else 0
        ):
            next_level_idx = len(df_needed)
            next_level_price = df["price"].iloc[next_level_idx]

            remaining_to_fill = filled_size - (
                df_needed["cumulative_notional"].sum() if not df_needed.empty else 0
            )
            next_level_qty_needed = remaining_to_fill / next_level_price

            # Add partial fill row
            partial_fill = pd.DataFrame(
                {
                    "price": [next_level_price],
                    "quantity": [next_level_qty_needed],
                    "notional": [remaining_to_fill],
                    "cumulative_notional": [filled_size],
                    "cumulative_quantity": [
                        (
                            df_needed["cumulative_quantity"].iloc[-1]
                            if not df_needed.empty
                            else 0
                        )
                        + next_level_qty_needed
                    ],
                }
            )

            df_needed = pd.concat([df_needed, partial_fill])

        # Calculate weighted average execution price
        executed_notional = df_needed["notional"].sum()
        executed_quantity = df_needed["quantity"].sum()
        weighted_avg_price = executed_notional / executed_quantity

        # Calculate slippage
        if side.lower() == "buy":
            # For buys, we pay more than the mid price
            slippage_pct = (weighted_avg_price - current_price) / current_price * 100
        else:
            # For sells, we receive less than the mid price
            slippage_pct = (current_price - weighted_avg_price) / current_price * 100

        slippage_usd = filled_size * slippage_pct / 100

        return {
            "symbol": symbol,
            "order_size_usd": order_size_usd,
            "filled_size_usd": filled_size,
            "side": side,
            "current_price": current_price,
            "weighted_avg_price": weighted_avg_price,
            "slippage_percentage": slippage_pct,
            "slippage_usd": slippage_usd,
            "quantity": executed_quantity,
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def calculate_skew_scale(ticker, current_price):
    """
    Calculate the skew_scale needed to achieve a specific slippage percentage.

    Parameters:
    - skew: Current skew value
    - size: Order size in base units
    - expected_slippage_percent: Target slippage percentage

    Returns:
    - skew_scale value that would result in the expected slippage
    """
    buy_result = calculate_slippage(ticker + "USDT", 500000)
    if buy_result is None:
        expected_slippage_percent = 8
        size = 500000 / current_price
    else:
        expected_slippage_percent = buy_result["slippage_percentage"] * 4
        size = 500000 / buy_result["current_price"]
    return (2 * (size)) * 50 / expected_slippage_percent

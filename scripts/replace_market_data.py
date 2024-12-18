import re


def replace_market_data(raw_data, market_data):
    skew_scale_regex = ".*SkewScale.*"
    max_market_size_regex = ".*MaxMarketSize.*"
    max_market_value_regex = ".*MaxMarketValue.*"
    for market_id, market_data in market_data.items():
        key = [
            k for k in raw_data["setting"].keys() if re.match(max_market_value_regex, k)
        ][0]
        raw_data[market_id]["setting"][key][
            "defaultValue"
        ] = f"<%= String({int(market_data.max_market_value):_}) %>"
        key = [
            k for k in raw_data["setting"].keys() if re.match(max_market_size_regex, k)
        ][0]
        raw_data[market_id]["setting"][key][
            "defaultValue"
        ] = f"<%= String({market_data.max_market_size:.2f}) %>"
        key = [k for k in raw_data["setting"].keys() if re.match(skew_scale_regex, k)][
            0
        ]
        raw_data[market_id]["setting"][key][
            "defaultValue"
        ] = f"<%= String({int(market_data.skew_scale):_}) %>"
    return raw_data

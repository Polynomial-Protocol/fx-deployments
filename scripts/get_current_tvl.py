import requests


def get_current_tvl():
    url = "https://perps-api-mainnet.polynomial.finance/vaults/all?chainId=8008"
    response = requests.get(url)
    data = response.json()
    tvl = sum(v["tvl"] for v in data)
    return tvl
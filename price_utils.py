import requests

def get_current_price(token_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data[token_id]['usd']
    except requests.RequestException as e:
        print(f"Error querying CoinGecko API: {e}")
        return None

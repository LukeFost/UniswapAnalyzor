#!/usr/bin/env python3

import requests
from web3 import Web3
from uniswap_utils import get_pool_address
from price_utils import get_current_price

Q96 = 2 ** 96

def price_to_sqrt_price(price):
    return int((price ** 0.5) * Q96)

def get_liquidity_for_amounts(sqrtPriceX96, sqrtPriceAX96, sqrtPriceBX96, amount0, amount1):
    if sqrtPriceAX96 > sqrtPriceBX96:
        sqrtPriceAX96, sqrtPriceBX96 = sqrtPriceBX96, sqrtPriceAX96
    
    if sqrtPriceX96 <= sqrtPriceAX96:
        liquidity0 = amount0 * (sqrtPriceBX96 - sqrtPriceAX96) / (sqrtPriceBX96 - sqrtPriceX96)
        liquidity1 = amount1
    elif sqrtPriceX96 < sqrtPriceBX96:
        liquidity0 = amount0
        liquidity1 = amount1 * (sqrtPriceBX96 - sqrtPriceX96) / (sqrtPriceBX96 - sqrtPriceAX96)
    else:
        liquidity0 = amount0
        liquidity1 = amount1
    
    liquidity = liquidity0 * sqrtPriceX96 + liquidity1 * Q96 / sqrtPriceX96
    
    return liquidity

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

def calculate_total_liquidity(amount0, amount1, current_price, lower_bound_price, upper_bound_price):
    sqrtPriceX96 = price_to_sqrt_price(current_price)
    sqrtPriceAX96 = price_to_sqrt_price(lower_bound_price)
    sqrtPriceBX96 = price_to_sqrt_price(upper_bound_price)

    liquidity = get_liquidity_for_amounts(sqrtPriceX96, sqrtPriceAX96, sqrtPriceBX96, amount0, amount1)

    return liquidity
def calculate_token_ratios(total_amount, current_price, lower_bound_price, upper_bound_price):
    sqrtPriceAX96 = price_to_sqrt_price(lower_bound_price)
    sqrtPriceBX96 = price_to_sqrt_price(upper_bound_price)
    
    # Assuming equal allocation initially
    amount0 = total_amount / 2 / current_price  # Convert half of total amount to ETH
    amount1 = total_amount / 2  # Half of total amount in USDC
    
    sqrtPriceX96 = price_to_sqrt_price(current_price)
    liquidity = get_liquidity_for_amounts(sqrtPriceX96, sqrtPriceAX96, sqrtPriceBX96, amount0, amount1)
    
    return {
        "liquidity": liquidity
    }

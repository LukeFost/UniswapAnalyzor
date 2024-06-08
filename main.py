# main.py
from web3 import Web3
from dotenv import load_dotenv
import os
import json
import requests
from liquidity import calculate_concentrated_liquidity_multiplier
from price_utils import get_current_price
from liquidity_calculator import calculate_total_liquidity
from uniswap_utils import get_pool_address

# Load environment variables from .env file
load_dotenv()

# Setup
alchemy_url = os.getenv('ALCHEMY_API_KEY')
w3 = Web3(Web3.HTTPProvider(alchemy_url))

# Print if web3 is successfully connected
print(w3.is_connected())

# Get the latest block number
latest_block = w3.eth.block_number
print(latest_block)

# UniswapV3Factory contract address
uniswap_v3_factory_address = "0x1F98431c8aD98523631AE4a59f267346ea31F984"

# Load ABI from the uniswapfactoryabi.json file
with open('uniswapfactoryabi.json', 'r') as abi_file:
    uniswap_v3_factory_abi = json.load(abi_file)

# Create contract instance
uniswap_v3_factory = w3.eth.contract(address=uniswap_v3_factory_address, abi=uniswap_v3_factory_abi)

def get_pool_address(token0, token1, fee):
    try:
        pool_address = uniswap_v3_factory.functions.getPool(Web3.to_checksum_address(token0), Web3.to_checksum_address(token1), fee).call()
        return pool_address
    except Exception as e:
        print(f"Error calling getPool: {e}")
        return None

def query_gecko_terminal(pool_address):
    url = f"https://api.geckoterminal.com/api/v2/networks/arbitrum/pools/{pool_address}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        base_token_price_usd = float(data['data']['attributes']['base_token_price_usd'])
        return data, base_token_price_usd
    except requests.RequestException as e:
        print(f"Error querying GeckoTerminal API: {e}")
        return None, None

def calculate_fees_earned(data, position_value_in_usd):
    fee_rate = 0.003  # 0.3%
    try:
        volume_24h = float(data['data']['attributes']['volume_usd']['h24'])
        volume_6h = float(data['data']['attributes']['volume_usd']['h6'])
        reserve_in_usd = float(data['data']['attributes']['reserve_in_usd'])

        fees_24h = ((volume_24h * fee_rate) / (reserve_in_usd + position_value_in_usd)) * (reserve_in_usd + position_value_in_usd)
        fees_6h = ((volume_6h * fee_rate) / (reserve_in_usd + position_value_in_usd)) * (reserve_in_usd + position_value_in_usd)

        print(f"Calculated fees - 24h: {fees_24h}, 6h: {fees_6h}")
        return fees_24h, fees_6h
    except (KeyError, ValueError) as e:
        print(f"Error calculating fees: {e}")
        return None, None


# Get current price from CoinGecko
token_id = "ethereum"  # CoinGecko ID for Ethereum
current_price = get_current_price(token_id)
if not current_price:
    print("Failed to retrieve the current price.")
    exit(1)

# Example usage
token0 = "0x18c11fd286c5ec11c3b683caa813b77f5163a122"
token1 = "0xaf88d065e77c8cc2239327c5edb3a432268e5831"
fee = 3000
percentage_change = 0.1  # Example percentage change (10%)
amount0 = 1000  # Example amount0
amount1 = 2000  # Example amount1

pool_address = get_pool_address(token0, token1, fee)
if pool_address:
    print(f"Pool address: {pool_address}")
    data, base_token_price_usd = query_gecko_terminal(pool_address)
    if data and base_token_price_usd:
        lower_bound_price = base_token_price_usd * (1 - percentage_change)
        upper_bound_price = base_token_price_usd * (1 + percentage_change)
        
        # Calculate total liquidity
        total_liquidity = calculate_total_liquidity(amount0, amount1, base_token_price_usd, lower_bound_price, upper_bound_price)
        
        fees_24h, fees_6h = calculate_fees_earned(data, total_liquidity)
        
        # Calculate price_min and price_max based on base_token_price_usd
        price_min = base_token_price_usd * (1 - percentage_change)
        price_max = base_token_price_usd * (1 + percentage_change)
        if fees_24h is not None and fees_6h is not None:
            print(f"Fees earned in 24 hours: {fees_24h}")
            print(f"Fees earned in 6 hours: {fees_6h}")
            
        # Calculate the Concentrated Liquidity Multiplier
        leverage = 1  # Example leverage value
        amount0 = 1000  # Example amount0
        amount1 = 2000  # Example amount1
        clm = calculate_concentrated_liquidity_multiplier(base_token_price_usd, price_min, price_max, leverage, amount0, amount1)
        print(f"Concentrated Liquidity Multiplier: {clm}")


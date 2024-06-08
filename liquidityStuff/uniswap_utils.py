from web3 import Web3

def get_pool_address(uniswap_v3_factory, token0, token1, fee):
    try:
        pool_address = uniswap_v3_factory.functions.getPool(Web3.to_checksum_address(token0), Web3.to_checksum_address(token1), fee).call()
        return pool_address
    except Exception as e:
        print(f"Error calling getPool: {e}")
        return None

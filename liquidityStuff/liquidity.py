def calculate_concentrated_liquidity_multiplier(price_current, price_min, price_max, leverage, amount0, amount1):
    # Constants
    Q96 = 2 ** 96

    # Calculate square root prices
    sqrt_price_current = price_current ** 0.5
    sqrt_price_min = price_min ** 0.5
    sqrt_price_max = price_max ** 0.5
    sqrt_price_max_inf = 2 ** 96  # Simulating a very large price
    sqrt_price_min_inf = 1  # Simulating a very small price

    print(f"sqrt_price_current: {sqrt_price_current}, sqrt_price_min: {sqrt_price_min}, sqrt_price_max: {sqrt_price_max}")
    print(f"sqrt_price_max_inf: {sqrt_price_max_inf}, sqrt_price_min_inf: {sqrt_price_min_inf}")

    # Calculate liquidity for specific range
    liquidity0 = (amount0 * sqrt_price_min * sqrt_price_max) / ((sqrt_price_max - sqrt_price_min) * Q96)
    liquidity1 = (amount1 * Q96) / (sqrt_price_max - sqrt_price_min)
    print(f"Intermediate values for liquidity0: amount0 * sqrt_price_min * sqrt_price_max = {amount0 * sqrt_price_min * sqrt_price_max}, (sqrt_price_max - sqrt_price_min) * Q96 = {(sqrt_price_max - sqrt_price_min) * Q96}")
    print(f"Intermediate values for liquidity1: amount1 * Q96 = {amount1 * Q96}, (sqrt_price_max - sqrt_price_min) = {sqrt_price_max - sqrt_price_min}")
    total_liquidity = liquidity0 + liquidity1

    # Calculate liquidity for maximum range
    max_liquidity0 = (amount0 * sqrt_price_max_inf * sqrt_price_min_inf) / ((sqrt_price_max_inf - sqrt_price_min_inf) * Q96)
    max_liquidity1 = (amount1 * Q96) / (sqrt_price_max_inf - sqrt_price_min_inf)
    max_total_liquidity = max_liquidity0 + max_liquidity1

    # Calculate the contracted liquidity multiplier
    if max_total_liquidity == 0:
        return float('inf')  # Prevent division by zero
    print(f"Liquidity0: {liquidity0}, Liquidity1: {liquidity1}, Total Liquidity: {total_liquidity}")
    print(f"Max_Liquidity0: {max_liquidity0}, Max_Liquidity1: {max_liquidity1}, Max Total Liquidity: {max_total_liquidity}")
    contracted_liquidity_multiplier = total_liquidity / max_total_liquidity

    return contracted_liquidity_multiplier * leverage

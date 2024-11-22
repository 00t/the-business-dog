import numpy as np

def monte_carlo_valuation(fcf, growth_rate, discount_rate, terminal_rate, iterations=1000):
    """
    Perform a Monte Carlo simulation for business valuation.
    
    Parameters:
        fcf (float): Free Cash Flow.
        growth_rate (tuple): Expected growth rate (low, high).
        discount_rate (float): Discount rate.
        terminal_rate (float): Terminal growth rate.
        iterations (int): Number of simulations.
    
    Returns:
        dict: Simulation results including mean and percentiles.
    """
    valuations = []
    for _ in range(iterations):
        # Simulate random growth rate within provided bounds
        simulated_growth_rate = np.random.uniform(growth_rate[0], growth_rate[1])
        
        # Calculate terminal value and DCF
        terminal_value = fcf * (1 + terminal_rate) / (discount_rate - terminal_rate)
        discounted_fcf = [
            fcf * (1 + simulated_growth_rate) ** t / (1 + discount_rate) ** t
            for t in range(1, 6)  # Assuming a 5-year projection
        ]
        
        total_valuation = sum(discounted_fcf) + terminal_value / (1 + discount_rate) ** 5
        valuations.append(total_valuation)
    
    # Calculate results
    mean_valuation = np.mean(valuations)
    p10 = np.percentile(valuations, 10)
    p90 = np.percentile(valuations, 90)
    
    return {
        "mean": mean_valuation,
        "p10": p10,
        "p90": p90,
        "all_valuations": valuations,
        "simulations": valuations
    }
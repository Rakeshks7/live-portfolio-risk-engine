import numpy as np
from scipy.stats import norm

class BlackScholes:
    
    @staticmethod
    def d1(S, K, T, r, sigma):
        T = np.maximum(T, 1e-5) 
        return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    @staticmethod
    def d2(S, K, T, r, sigma):
        T = np.maximum(T, 1e-5)
        return BlackScholes.d1(S, K, T, r, sigma) - sigma * np.sqrt(T)

    @staticmethod
    def price(S, K, T, r, sigma, is_call=True):
        """Calculates Option Price."""
        d1 = BlackScholes.d1(S, K, T, r, sigma)
        d2 = BlackScholes.d2(S, K, T, r, sigma)
        
        if is_call:
            return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    @staticmethod
    def get_greeks(S, K, T, r, sigma, is_call=True):
        d1 = BlackScholes.d1(S, K, T, r, sigma)
        
        if is_call:
            delta = norm.cdf(d1)
        else:
            delta = norm.cdf(d1) - 1

        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(np.maximum(T, 1e-5)))

        vega = S * norm.pdf(d1) * np.sqrt(np.maximum(T, 1e-5))
        
        return {"delta": delta, "gamma": gamma, "vega": vega / 100}
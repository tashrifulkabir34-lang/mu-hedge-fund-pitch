"""
Micron Technology (MU) Valuation Model
Includes:
1. Discounted Cash Flow (DCF) Analysis
2. Comparable Company Analysis (Comps)
3. Implied Share Price Calculation

Author: Tasriful Kabir
Date: 2026-04-13
"""

import numpy as np
import pandas as pd

class MicronValuation:
    def __init__(self):
        # Current Market Data (as of April 2026)
        self.current_price = 245.00  # Estimated current price based on search
        self.shares_outstanding = 1140  # in millions
        self.market_cap = self.current_price * self.shares_outstanding
        self.total_debt = 13500  # in millions (approx from 10-K)
        self.cash_and_equiv = 16700  # in millions (from FQ2-26)
        self.enterprise_value = self.market_cap + self.total_debt - self.cash_and_equiv
        
        # Financial Projections (in millions)
        self.fy2026_rev_guidance = 33500 * 4  # Annualized FQ3 guidance
        self.fy2026_ebitda_margin = 0.70  # High margin due to HBM3E
        self.tax_rate = 0.15
        self.wacc = 0.10  # Weighted Average Cost of Capital
        self.terminal_growth = 0.03

    def run_dcf(self):
        """
        Simplified 5-year DCF Model
        """
        years = np.array([1, 2, 3, 4, 5])
        
        # Projections: Super-cycle peak in 2026, followed by normalization
        revenue = np.array([134000, 145000, 130000, 120000, 125000])
        ebitda_margin = np.array([0.75, 0.70, 0.55, 0.45, 0.45])
        ebitda = revenue * ebitda_margin
        
        # D&A and Capex (High capex for memory)
        capex_margin = 0.35
        capex = revenue * capex_margin
        depreciation = capex * 0.8  # Lagged D&A
        
        ebit = ebitda - depreciation
        nopat = ebit * (1 - self.tax_rate)
        
        # Free Cash Flow to Firm (FCFF)
        # FCFF = NOPAT + D&A - Capex - Change in NWC (NWC assumed neutral for simplicity)
        fcff = nopat + depreciation - capex
        
        # Discounting
        discount_factors = (1 + self.wacc) ** years
        pv_fcff = fcff / discount_factors
        
        # Terminal Value
        terminal_value = (fcff[-1] * (1 + self.terminal_growth)) / (self.wacc - self.terminal_growth)
        pv_terminal_value = terminal_value / (1 + self.wacc) ** 5
        
        enterprise_value_dcf = np.sum(pv_fcff) + pv_terminal_value
        equity_value_dcf = enterprise_value_dcf - self.total_debt + self.cash_and_equiv
        price_per_share_dcf = equity_value_dcf / self.shares_outstanding
        
        return {
            "Enterprise Value": enterprise_value_dcf,
            "Equity Value": equity_value_dcf,
            "Price per Share": price_per_share_dcf,
            "FCFF Projections": fcff.tolist()
        }

    def run_comps(self):
        """
        Comparable Company Analysis
        Peers: Samsung, SK Hynix (Memory), NVIDIA (AI Proxy)
        """
        peers = {
            "SK Hynix": {"EV/EBITDA": 5.5, "P/E": 8.0},
            "Samsung": {"EV/EBITDA": 8.6, "P/E": 12.0},
            "NVIDIA": {"EV/EBITDA": 25.0, "P/E": 35.0},
            "Peer Median": {"EV/EBITDA": 8.6, "P/E": 12.0}
        }
        
        # MU Forward Estimates (FY2026)
        mu_ebitda_2026 = 134000 * 0.75
        mu_eps_2026 = 19.15 * 4  # Annualized FQ3 guidance
        
        # Valuation based on Median
        val_ev_ebitda = (mu_ebitda_2026 * peers["Peer Median"]["EV/EBITDA"]) - self.total_debt + self.cash_and_equiv
        price_ev_ebitda = val_ev_ebitda / self.shares_outstanding
        
        val_pe = (mu_eps_2026 * peers["Peer Median"]["P/E"]) * self.shares_outstanding
        price_pe = val_pe / self.shares_outstanding
        
        return {
            "Price (EV/EBITDA)": price_ev_ebitda,
            "Price (P/E)": price_pe,
            "Peers": peers
        }

if __name__ == "__main__":
    model = MicronValuation()
    dcf_results = model.run_dcf()
    comps_results = model.run_comps()
    
    print("--- DCF Results ---")
    for k, v in dcf_results.items():
        print(f"{k}: {v}")
        
    print("\n--- Comps Results ---")
    for k, v in comps_results.items():
        print(f"{k}: {v}")
    
    # Final Target Price (Weighted Average)
    target_price = (dcf_results["Price per Share"] * 0.6) + (comps_results["Price (EV/EBITDA)"] * 0.4)
    print(f"\nFinal Target Price: ${target_price:.2f}")
    print(f"Current Price: ${model.current_price:.2f}")
    print(f"Upside/Downside: {((target_price/model.current_price)-1)*100:.2f}%")

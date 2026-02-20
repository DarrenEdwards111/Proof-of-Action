#!/usr/bin/env python3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.use("Agg")
"""
Sybil Resistance and Economic Stability Analysis
Implements Section 6 of the paper: Economic Stability

Analyzes:
- Economic stability condition: R(a)·P ≤ C(a)
- Sybil profitability under varying token prices
- Sensitivity to cost parameters
- Conditions for farming unprofitability
"""

import numpy as np
matplotlib.use("Agg")
import os

# Action cost parameters (Section 6)
# Example: computational verification task
COST_COMPUTE = 0.10      # $ per task (electricity + amortization)
COST_VERIFICATION = 0.02 # $ per task (oracle fees)
COST_NETWORK = 0.01      # $ per task (gas fees)

# Total production cost C(a)
C_ACTION = COST_COMPUTE + COST_VERIFICATION + COST_NETWORK  # $0.13 per action

# Reward parameters
R_BASE = 10.0  # Base reward: 10 tokens per verified action
R_MIN = 1.0    # Minimum reward (when burn/mint ratio is low)
R_MAX = 20.0   # Maximum reward (when burn/mint ratio is high)

# Token price range (USD per token)
PRICE_MIN = 0.001
PRICE_MAX = 0.100
PRICE_STEPS = 100

def compute_profitability(token_price, reward, cost):
    """
    Compute profitability: Profit = R(a)·P - C(a)
    
    Positive profit → farming is profitable (Sybil risk)
    Negative profit → farming is unprofitable (Sybil resistant)
    """
    revenue = reward * token_price
    profit = revenue - cost
    return profit, revenue

def sybil_threshold_price(reward, cost):
    """
    Compute threshold token price where farming becomes unprofitable
    P_threshold = C(a) / R(a)
    
    Below this price, Sybil attacks are economically irrational
    """
    return cost / reward

def sensitivity_analysis():
    """
    Analyze Sybil resistance under varying parameters
    """
    print("=" * 70)
    print("Sybil Resistance & Economic Stability Analysis")
    print("Implementing Section 6: Economic Stability Condition")
    print("=" * 70)
    print()
    
    print("Cost structure:")
    print(f"  Compute cost:       ${COST_COMPUTE:.3f}")
    print(f"  Verification cost:  ${COST_VERIFICATION:.3f}")
    print(f"  Network cost:       ${COST_NETWORK:.3f}")
    print(f"  Total cost C(a):    ${C_ACTION:.3f} per action")
    print()
    
    print("Reward structure:")
    print(f"  Base reward R(a):   {R_BASE:.1f} tokens")
    print(f"  Adaptive range:     [{R_MIN:.1f}, {R_MAX:.1f}] tokens")
    print()
    
    # Compute threshold prices for different reward levels
    rewards = [R_MIN, R_BASE, R_MAX]
    print("Sybil resistance threshold prices:")
    for R in rewards:
        P_threshold = sybil_threshold_price(R, C_ACTION)
        print(f"  R={R:5.1f} tokens → P_threshold = ${P_threshold:.4f}/token")
        print(f"             → Sybil-resistant when P < ${P_threshold:.4f}")
    print()
    
    # Price sweep
    prices = np.linspace(PRICE_MIN, PRICE_MAX, PRICE_STEPS)
    
    # Compute profitability curves for different reward levels
    results = {}
    for R in rewards:
        profits = []
        revenues = []
        for P in prices:
            profit, revenue = compute_profitability(P, R, C_ACTION)
            profits.append(profit)
            revenues.append(revenue)
        results[R] = (profits, revenues)
    
    return prices, results, rewards

def plot_stability_analysis(prices, results, rewards):
    """
    Generate stability and Sybil resistance plots
    """
    os.makedirs('simulation/figures', exist_ok=True)
    
    # Figure 1: Profitability vs Token Price
    plt.figure(figsize=(12, 7))
    
    colors = ['blue', 'green', 'red']
    for i, R in enumerate(rewards):
        profits, revenues = results[R]
        P_threshold = sybil_threshold_price(R, C_ACTION)
        
        plt.plot(prices, profits, color=colors[i], linewidth=2.5, 
                label=f'R(a) = {R:.1f} tokens (threshold: ${P_threshold:.4f})')
        
        # Mark threshold point
        plt.axvline(P_threshold, color=colors[i], linestyle='--', alpha=0.5, linewidth=1.5)
    
    # Zero profit line
    plt.axhline(0, color='black', linestyle='-', linewidth=1.5, alpha=0.7, 
               label='Break-even (profit = 0)')
    
    # Sybil-resistant region
    plt.fill_between(prices, -0.5, 0, alpha=0.15, color='green', 
                     label='Sybil-resistant region (profit < 0)')
    
    # Sybil-vulnerable region
    plt.fill_between(prices, 0, 0.5, alpha=0.15, color='red', 
                     label='Sybil-vulnerable region (profit > 0)')
    
    plt.xlabel('Token Price (USD)', fontsize=12)
    plt.ylabel('Profit per Action (USD)', fontsize=12)
    plt.title('Sybil Resistance: Profitability vs Token Price\nCondition: R(a)·P ≤ C(a)', 
              fontsize=14, fontweight='bold')
    plt.legend(fontsize=10, loc='upper left')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('simulation/figures/sybil_resistance.png', dpi=300)
    print("  📊 Saved: simulation/figures/sybil_resistance.png")
    
    # Figure 2: Revenue vs Cost
    plt.figure(figsize=(12, 7))
    
    for i, R in enumerate(rewards):
        profits, revenues = results[R]
        plt.plot(prices, revenues, color=colors[i], linewidth=2.5, 
                label=f'Revenue: R(a)·P (R={R:.1f} tokens)')
    
    # Constant cost line
    cost_line = [C_ACTION] * len(prices)
    plt.plot(prices, cost_line, 'k--', linewidth=2.5, label=f'Cost: C(a) = ${C_ACTION:.3f}')
    
    plt.xlabel('Token Price (USD)', fontsize=12)
    plt.ylabel('Value per Action (USD)', fontsize=12)
    plt.title('Economic Stability: Revenue vs Cost\nFarming unprofitable when Revenue < Cost', 
              fontsize=14, fontweight='bold')
    plt.legend(fontsize=11, loc='upper left')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('simulation/figures/revenue_vs_cost.png', dpi=300)
    print("  📊 Saved: simulation/figures/revenue_vs_cost.png")
    
    # Figure 3: Cost sensitivity analysis
    plt.figure(figsize=(12, 7))
    
    cost_multipliers = [0.5, 1.0, 1.5, 2.0]
    R_fixed = R_BASE
    
    for mult in cost_multipliers:
        C_scaled = C_ACTION * mult
        P_threshold = sybil_threshold_price(R_fixed, C_scaled)
        profits = [R_fixed * P - C_scaled for P in prices]
        
        plt.plot(prices, profits, linewidth=2.5, 
                label=f'Cost = {mult:.1f}× baseline (${C_scaled:.3f}), threshold: ${P_threshold:.4f}')
        plt.axvline(P_threshold, linestyle='--', alpha=0.4)
    
    plt.axhline(0, color='black', linestyle='-', linewidth=1.5, alpha=0.7)
    plt.fill_between(prices, -1, 0, alpha=0.1, color='green')
    
    plt.xlabel('Token Price (USD)', fontsize=12)
    plt.ylabel('Profit per Action (USD)', fontsize=12)
    plt.title(f'Cost Sensitivity Analysis (R={R_fixed:.1f} tokens fixed)', 
              fontsize=14, fontweight='bold')
    plt.legend(fontsize=11, loc='upper left')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('simulation/figures/cost_sensitivity.png', dpi=300)
    print("  📊 Saved: simulation/figures/cost_sensitivity.png")
    
    plt.close('all')

def main():
    """
    Main execution: run stability analysis and generate figures
    """
    # Run analysis
    prices, results, rewards = sensitivity_analysis()
    
    # Key findings
    print("Key findings:")
    print(f"  1. At low token prices (P < ${sybil_threshold_price(R_BASE, C_ACTION):.4f}),")
    print(f"     farming is unprofitable → Sybil-resistant")
    print(f"  2. At high prices, adaptive reward reduction (R_t ↓) maintains resistance")
    print(f"  3. Cost structure dominates profitability: C(a) = ${C_ACTION:.3f}")
    print()
    
    # Generate plots
    print("📈 Generating figures...")
    plot_stability_analysis(prices, results, rewards)
    
    print("\n" + "=" * 70)
    print("✅ Stability analysis complete! Check simulation/figures/ for results.")
    print("=" * 70)

if __name__ == "__main__":
    main()

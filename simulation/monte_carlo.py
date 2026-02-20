#!/usr/bin/env python3
"""
Monte Carlo Simulation for Proof-of-Action Economic Model
Implements Section 10 of the paper: Stochastic Supply Convergence

Demonstrates:
- Logistic user growth: n_t = K / (1 + e^(-r(t-t0)))
- Stochastic minting: M(t) ~ Normal(μ_m, σ_m) per user
- Stochastic burning: B(t) ~ Normal(μ_b, σ_b) per user
- Supply evolution: S(t) = S(t-1) + M(t) - B(t)
- Adaptive rewards: R_t(a) = R_0(a) · B(t)/M(t)
- Equilibrium convergence under rational behavior
"""

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import expit
import os

# Simulation parameters (Section 10 of paper)
N_SIMULATIONS = 100  # Number of Monte Carlo runs
T_YEARS = 10          # Simulation horizon (years)
T_STEPS = T_YEARS * 12  # Monthly timesteps

# User growth parameters (logistic model)
K_MAX_USERS = 100_000  # Carrying capacity
r_GROWTH_RATE = 0.05     # Monthly growth rate
t0_INFLECTION = 36       # Inflection point (3 years)

# Minting parameters (tokens per user per month)
mu_MINT = 10.0   # Mean mint per user
sigma_MINT = 3.0 # Std dev mint per user

# Burning parameters (tokens per user per month)
mu_BURN_INITIAL = 2.0   # Initial mean burn per user
sigma_BURN = 1.0        # Std dev burn per user

# Initial conditions
S0_INITIAL_SUPPLY = 0   # Start with zero supply
R0_INITIAL_REWARD = 1.0 # Base reward coefficient

# Adaptive burn adjustment factor
ALPHA_ADAPTATION = 0.1  # How aggressively burn adapts to mint

def logistic_growth(t, K, r, t0):
    """
    Logistic user growth model
    n_t = K / (1 + exp(-r(t - t0)))
    """
    return K / (1 + np.exp(-r * (t - t0)))

def simulate_single_run(seed=None):
    """
    Single Monte Carlo simulation run
    Returns: (time, supply, users, mint_total, burn_total, rewards)
    """
    if seed is not None:
        np.random.seed(seed)
    
    time = np.arange(T_STEPS)
    users = np.array([logistic_growth(t, K_MAX_USERS, r_GROWTH_RATE, t0_INFLECTION) 
                      for t in time])
    
    supply = np.zeros(T_STEPS)
    mint_total = np.zeros(T_STEPS)
    burn_total = np.zeros(T_STEPS)
    rewards = np.ones(T_STEPS) * R0_INITIAL_REWARD
    
    supply[0] = S0_INITIAL_SUPPLY
    
    for t in range(1, T_STEPS):
        n_t = users[t]
        
        # Stochastic minting per user
        mint_per_user = np.maximum(0, np.random.normal(mu_MINT, sigma_MINT, int(n_t)))
        M_t = np.sum(mint_per_user)
        
        # Adaptive burning: increases as supply grows
        # Rational actors burn more when token value is low relative to holding cost
        mu_burn_adaptive = mu_BURN_INITIAL * (1 + ALPHA_ADAPTATION * (supply[t-1] / (n_t + 1)))
        burn_per_user = np.maximum(0, np.random.normal(mu_burn_adaptive, sigma_BURN, int(n_t)))
        B_t = np.sum(burn_per_user)
        
        # Supply evolution
        supply[t] = supply[t-1] + M_t - B_t
        supply[t] = max(0, supply[t])  # Non-negative supply
        
        mint_total[t] = M_t
        burn_total[t] = B_t
        
        # Adaptive reward coefficient (Section 9)
        # R_t(a) = R_0(a) · B(t)/M(t)
        # Prevents farming when burn rate is low
        if M_t > 0:
            rewards[t] = R0_INITIAL_REWARD * (B_t / M_t)
        else:
            rewards[t] = R0_INITIAL_REWARD
    
    return time, supply, users, mint_total, burn_total, rewards

def run_monte_carlo():
    """
    Run N Monte Carlo simulations and compute statistics
    """
    print(f"Running {N_SIMULATIONS} Monte Carlo simulations...")
    print(f"Horizon: {T_YEARS} years ({T_STEPS} months)")
    print(f"User growth: logistic with K={K_MAX_USERS:,}, r={r_GROWTH_RATE}")
    print(f"Mint: μ={mu_MINT}, σ={sigma_MINT} per user/month")
    print(f"Burn: μ_initial={mu_BURN_INITIAL}, σ={sigma_BURN} per user/month (adaptive)")
    print()
    
    # Storage for all runs
    all_supplies = np.zeros((N_SIMULATIONS, T_STEPS))
    all_rewards = np.zeros((N_SIMULATIONS, T_STEPS))
    
    for i in range(N_SIMULATIONS):
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i+1}/{N_SIMULATIONS} simulations complete")
        
        time, supply, users, mint, burn, rewards = simulate_single_run(seed=i)
        all_supplies[i] = supply
        all_rewards[i] = rewards
    
    # Compute statistics
    mean_supply = np.mean(all_supplies, axis=0)
    std_supply = np.std(all_supplies, axis=0)
    percentile_5 = np.percentile(all_supplies, 5, axis=0)
    percentile_95 = np.percentile(all_supplies, 95, axis=0)
    
    mean_reward = np.mean(all_rewards, axis=0)
    
    print(f"\n✅ Simulation complete!")
    print(f"\nFinal supply statistics (month {T_STEPS}):")
    print(f"  Mean: {mean_supply[-1]:,.0f} tokens")
    print(f"  Std Dev: {std_supply[-1]:,.0f} tokens")
    print(f"  5th percentile: {percentile_5[-1]:,.0f} tokens")
    print(f"  95th percentile: {percentile_95[-1]:,.0f} tokens")
    print(f"\nFinal reward coefficient: {mean_reward[-1]:.3f}")
    
    return (time, all_supplies, mean_supply, std_supply, 
            percentile_5, percentile_95, mean_reward, users)

def plot_results(time, all_supplies, mean_supply, std_supply, 
                percentile_5, percentile_95, mean_reward, users):
    """
    Generate publication-quality plots
    """
    os.makedirs('simulation/figures', exist_ok=True)
    
    # Convert time to years
    time_years = time / 12.0
    
    # Figure 1: Supply trajectories with confidence bands
    plt.figure(figsize=(12, 6))
    
    # Plot 50 sample trajectories
    for i in range(0, min(50, all_supplies.shape[0]), 5):
        plt.plot(time_years, all_supplies[i], alpha=0.1, color='blue', linewidth=0.5)
    
    # Mean trajectory
    plt.plot(time_years, mean_supply, 'b-', linewidth=2.5, label='Mean supply')
    
    # Confidence bands
    plt.fill_between(time_years, percentile_5, percentile_95, 
                     alpha=0.2, color='blue', label='90% confidence interval')
    
    plt.xlabel('Time (years)', fontsize=12)
    plt.ylabel('Token Supply', fontsize=12)
    plt.title('Monte Carlo Simulation: Supply Evolution (N=1000 runs)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('simulation/figures/supply_convergence.png', dpi=300)
    print("  📊 Saved: simulation/figures/supply_convergence.png")
    
    # Figure 2: Supply convergence with user growth
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Supply
    ax1.plot(time_years, mean_supply, 'b-', linewidth=2)
    ax1.fill_between(time_years, mean_supply - std_supply, mean_supply + std_supply, 
                     alpha=0.3, color='blue')
    ax1.set_ylabel('Token Supply (mean ± σ)', fontsize=11)
    ax1.set_title('Stochastic Equilibrium Convergence', fontsize=14, fontweight='bold')
    ax1.grid(alpha=0.3)
    
    # User growth
    ax2.plot(time_years, users / 1000, 'g-', linewidth=2)
    ax2.set_ylabel('Active Users (thousands)', fontsize=11)
    ax2.grid(alpha=0.3)
    
    # Adaptive reward coefficient
    ax3.plot(time_years, mean_reward, 'r-', linewidth=2)
    ax3.set_ylabel('Reward Coefficient R_t', fontsize=11)
    ax3.set_xlabel('Time (years)', fontsize=12)
    ax3.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='R_0 = 1.0')
    ax3.legend(fontsize=10)
    ax3.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('simulation/figures/equilibrium_analysis.png', dpi=300)
    print("  📊 Saved: simulation/figures/equilibrium_analysis.png")
    
    # Figure 3: Distribution at final timestep
    plt.figure(figsize=(10, 6))
    final_supplies = all_supplies[:, -1]
    plt.hist(final_supplies, bins=50, alpha=0.7, color='blue', edgecolor='black')
    plt.axvline(mean_supply[-1], color='red', linestyle='--', linewidth=2, 
                label=f'Mean: {mean_supply[-1]:,.0f}')
    plt.axvline(percentile_5[-1], color='orange', linestyle='--', linewidth=1.5, 
                label=f'5th percentile: {percentile_5[-1]:,.0f}')
    plt.axvline(percentile_95[-1], color='orange', linestyle='--', linewidth=1.5, 
                label=f'95th percentile: {percentile_95[-1]:,.0f}')
    plt.xlabel('Final Supply (tokens)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title(f'Supply Distribution at T={T_YEARS} years (N={N_SIMULATIONS} simulations)', 
              fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('simulation/figures/supply_distribution.png', dpi=300)
    print("  📊 Saved: simulation/figures/supply_distribution.png")
    
    plt.close('all')

def main():
    """
    Main execution: run simulations and generate figures
    """
    print("=" * 70)
    print("Proof-of-Action Monte Carlo Simulation")
    print("Implementing Section 10: Stochastic Supply Convergence")
    print("=" * 70)
    print()
    
    # Run simulations
    results = run_monte_carlo()
    
    # Generate plots
    print("\n📈 Generating figures...")
    plot_results(*results)
    
    print("\n" + "=" * 70)
    print("✅ Simulation complete! Check simulation/figures/ for results.")
    print("=" * 70)

if __name__ == "__main__":
    main()

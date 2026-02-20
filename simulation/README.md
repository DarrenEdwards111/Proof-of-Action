# Economic Simulation for Proof-of-Action

Python-based Monte Carlo simulation implementing the stochastic economic model from Section 10 of the paper.

## Overview

This simulation demonstrates:

1. **Supply Convergence** — Token supply stabilizes despite stochastic minting/burning
2. **Sybil Resistance** — Economic conditions under which farming becomes unprofitable
3. **Adaptive Rewards** — Dynamic reward coefficient maintains equilibrium

## Files

- **`monte_carlo.py`** — Main simulation (Section 10)
  - Logistic user growth: `n_t = K / (1 + e^(-r(t-t0)))`
  - Stochastic minting: `M(t) ~ Normal(μ_m, σ_m)` per user
  - Stochastic burning: `B(t) ~ Normal(μ_b, σ_b)` per user
  - Adaptive rewards: `R_t(a) = R_0(a) · B(t)/M(t)`
  - Runs N=1000 simulations over T=10 years

- **`stability_analysis.py`** — Sybil resistance analysis (Section 6)
  - Economic stability condition: `R(a)·P ≤ C(a)`
  - Profitability vs token price
  - Cost sensitivity analysis

- **`figures/`** — Generated plots (created by running simulations)

## Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `numpy` — Numerical computations
- `scipy` — Statistical functions (logistic growth)
- `matplotlib` — Plotting

## Running the Simulation

### Monte Carlo Supply Convergence

```bash
python simulation/monte_carlo.py
```

**Output:**
- `figures/supply_convergence.png` — Supply trajectories with 90% confidence bands
- `figures/equilibrium_analysis.png` — Supply, user growth, and adaptive rewards over time
- `figures/supply_distribution.png` — Final supply distribution histogram

**Expected behavior:**
- Supply converges to stochastic equilibrium around mean value
- Adaptive reward coefficient stabilizes near 1.0
- 90% of simulations fall within narrow confidence band

### Sybil Resistance Analysis

```bash
python simulation/stability_analysis.py
```

**Output:**
- `figures/sybil_resistance.png` — Profitability vs token price for varying rewards
- `figures/revenue_vs_cost.png` — Revenue vs cost comparison
- `figures/cost_sensitivity.png` — How production cost affects resistance

**Expected behavior:**
- At low token prices (P < threshold), profit is negative → Sybil-resistant
- Threshold price depends on reward/cost ratio: `P_threshold = C(a)/R(a)`
- Higher production costs increase resistance

## Key Parameters

### Monte Carlo Simulation (`monte_carlo.py`)

```python
N_SIMULATIONS = 1000      # Number of Monte Carlo runs
T_YEARS = 10              # Simulation horizon
K_MAX_USERS = 1_000_000   # Logistic carrying capacity
r_GROWTH_RATE = 0.05      # Monthly growth rate
mu_MINT = 10.0            # Mean tokens minted per user/month
mu_BURN_INITIAL = 2.0     # Initial mean tokens burned per user/month
ALPHA_ADAPTATION = 0.1    # Burn adaptation rate
```

### Stability Analysis (`stability_analysis.py`)

```python
COST_COMPUTE = 0.10       # $ per action (computational cost)
COST_VERIFICATION = 0.02  # $ per action (oracle verification)
COST_NETWORK = 0.01       # $ per action (gas fees)
R_BASE = 10.0             # Base reward (tokens per action)
```

## Interpreting Results

### Supply Convergence

**Figure: `supply_convergence.png`**

Shows N=1000 individual simulation trajectories (light blue) overlaid with mean supply (dark blue) and 90% confidence interval (shaded region).

**Key observation:** Despite stochastic minting/burning, supply converges to stable range after ~5 years, demonstrating **Proposition 2** from the paper:

```
If E[M(t)] → E[B(t)] then E[dS/dt] → 0
```

### Equilibrium Analysis

**Figure: `equilibrium_analysis.png`**

Three-panel plot showing:
1. **Supply evolution** — Mean ± standard deviation over 10 years
2. **User growth** — Logistic curve reaching carrying capacity K
3. **Adaptive reward** — R_t coefficient adjusting to maintain equilibrium

**Key observation:** As user base saturates, mint/burn rates equilibrate, and adaptive reward stabilizes near R_0 = 1.0.

### Sybil Resistance

**Figure: `sybil_resistance.png`**

Profit per action as function of token price for different reward levels.

**Green region (Sybil-resistant):** Profit < 0 → farming unprofitable  
**Red region (Sybil-vulnerable):** Profit > 0 → farming profitable

**Key observation:** For baseline reward R=10 tokens and cost C=$0.13, threshold price is ~$0.013. Below this price, Sybil attacks are economically irrational.

### Cost Sensitivity

**Figure: `cost_sensitivity.png`**

Shows how production cost C(a) affects resistance. Higher costs (2× baseline) shift break-even point rightward, increasing resistance across broader price range.

**Strategic implication:** Protocol designers can enhance Sybil resistance by:
1. Increasing verification complexity (raises C_compute)
2. Requiring stake/bond deposits (raises opportunity cost)
3. Adding gas fees via on-chain verification (raises C_network)

## Mathematical Foundation

### Supply Evolution (Section 10)

```
S(t) = S(t-1) + M(t) - B(t)
```

where:
- `M(t) = Σ_i m_i(t)` — Total minting at time t
- `B(t) = Σ_i b_i(t)` — Total burning at time t
- `m_i(t) ~ Normal(μ_m, σ_m)` — Stochastic mint per user
- `b_i(t) ~ Normal(μ_b, σ_b)` — Stochastic burn per user

### Adaptive Reward (Section 9)

```
R_t(a) = R_0(a) · B(t)/M(t)
```

**Negative feedback mechanism:**
- If minting > burning → R_t decreases → less incentive to mint → equilibrium restored
- If burning > minting → R_t increases → more incentive to mint → equilibrium restored

### Economic Stability (Section 6)

**Condition for Sybil resistance:**
```
R(a)·P ≤ C(a)
```

**Derivation:**
- Revenue per action: `Rev = R(a)·P`
- Cost per action: `C(a)`
- Profit: `π = Rev - C(a)`
- Sybil-resistant when `π ≤ 0` → `R(a)·P ≤ C(a)`

## Extending the Simulation

### Custom User Growth Model

Replace `logistic_growth()` in `monte_carlo.py`:

```python
def custom_growth(t):
    # Example: exponential growth with saturation
    return 100_000 * (1 - np.exp(-0.01 * t))
```

### Dynamic Cost Model

Modify `stability_analysis.py` to include time-varying costs:

```python
def dynamic_cost(t, base_cost):
    # Example: costs decrease with technological improvement
    return base_cost * np.exp(-0.02 * t)  # 2% monthly reduction
```

### Multi-Action Types

Extend to multiple action categories with different rewards/costs:

```python
actions = {
    'compute': {'reward': 10, 'cost': 0.13},
    'data-annotation': {'reward': 5, 'cost': 0.05},
    'storage': {'reward': 2, 'cost': 0.02}
}
```

## Citation

If you use this simulation in your research, please cite the paper:

```bibtex
@article{edwards2026proofofaction,
  title={Proof-of-Action: A Verifiable Minting Policy for Utility-Backed Digital Economies},
  author={Edwards, Darren J.},
  year={2026},
  institution={Mikoshi Ltd}
}
```

## License

Apache 2.0 — See [../LICENSE](../LICENSE)

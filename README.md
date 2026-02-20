# Proof-of-Action: A Verifiable Minting Policy for Utility-Backed Digital Economies

[![PDF](https://img.shields.io/badge/PDF-Download-blue)](paper/proof_of_action.pdf)
[![LaTeX](https://img.shields.io/badge/LaTeX-Source-green)](paper/proof_of_action.tex)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange.svg)](LICENSE)

**Author:** Darren J. Edwards  
**Affiliation:** Department of Public Health, Swansea University, Swansea, UK  
**Contact:** d.j.edwards@swansea.ac.uk

---

## Abstract

This paper introduces **Proof-of-Action (PoAct)**, a novel blockchain minting policy where tokens are issued exclusively upon deterministic verification of useful work. Unlike traditional mechanisms (Proof-of-Work, Proof-of-Stake, Proof-of-Authority) that couple token issuance with consensus, PoAct operates independently, enabling utility-backed token creation on any secure blockchain substrate.

**Key Contributions:**

- **Complete Provenance**: Every token traces to a unique productive action via collision-resistant hash commitments
- **Sybil Resistance**: Achieved through real economic cost of useful production, not artificial computational waste or capital lockup
- **Consensus Independence**: Modular design compatible with any underlying blockchain (PoW, PoS, PoA, or novel protocols)
- **Economic Stability**: Formal analysis of mint-burn equilibrium with adaptive reward mechanisms
- **Stochastic Convergence**: Monte Carlo simulations demonstrating supply stabilization under rational adversarial behavior

---

## Paper Structure

The paper is organized as follows:

1. **Introduction**: Motivation and separation of consensus from issuance
2. **System Model**: Blockchain substrate, deterministic verifier, and minting contract architecture
3. **Formal Validity**: Mathematical definition of action validity via hash commitments
4. **Provenance Theorem**: Proof of injective mapping from tokens to productive actions
5. **Consensus Distinction**: Formal separation of minting policy from consensus mechanisms
6. **Economic Stability**: Conditions for Sybil resistance and cost-based equilibrium
7. **Comparative Analysis**: Table comparing PoAct with PoW, PoS, and PoA
8. **Adversarial Model**: Four threat scenarios with mitigation hierarchies
9. **Dynamic Supply**: Adaptive reward coefficient and negative feedback stabilization
10. **Monte Carlo Simulation**: Stochastic equilibrium demonstration with logistic user growth
11. **Governance**: Parameter adjustment and DAO-based adaptive control
12. **Discussion**: Implications for verifiable production networks and computational governance
13. **Limitations**: Deterministic verification requirements and oracle centralization concerns
14. **Conclusion**: Summary of contributions and future work

---

## Key Formulas

### Action Validity
```
Valid(a) ⟺ H(output(a)) = h_chain(a)
```
where `H` is SHA-256 and `h_chain` is the on-chain hash commitment.

### Economic Stability Condition
```
R(a)·P ≤ C(a)
```
where `R(a)` is token reward, `P` is market price, and `C(a)` is production cost.

### Dynamic Supply Model
```
S(t) = S(t-1) + M(t) - B(t)
```
with adaptive reward coefficient:
```
R_t(a) = R_0(a) · B(t)/M(t)
```

### Stochastic Stability (Proposition 2)
```
If E[M(t)] → E[B(t)] then E[dS/dt] → 0
```

---

## Compiling the Paper

The paper is written in LaTeX and compiled using [Tectonic](https://tectonic-typesetting.github.io/), a modern, self-contained TeX/LaTeX engine.

### Prerequisites
```bash
# Install tectonic (if not already installed)
# On Ubuntu/Debian:
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh

# On macOS with Homebrew:
brew install tectonic

# On Windows with Chocolatey:
choco install tectonic
```

### Compilation
```bash
cd paper
tectonic proof_of_action.tex
```

The compiled PDF will be saved as `proof_of_action.pdf`.

**Note:** Do not use `pdflatex` or other traditional TeX compilers. Tectonic handles package management automatically and ensures reproducible builds.

---

## Citation

If you use this work in your research, please cite:

```bibtex
@article{edwards2026proofofaction,
  title={Proof-of-Action: A Verifiable Minting Policy for Utility-Backed Digital Economies},
  author={Edwards, Darren J.},
  journal={arXiv preprint},
  year={2026},
  institution={Swansea University}
}
```

---

## Potential Applications

- **Decentralized Compute Marketplaces**: Tokenize verified computations (ML training, rendering, simulations)
- **Supply Chain Tracking**: Mint tokens for each logistics step (manufacturing, shipping, delivery)
- **Data Annotation Platforms**: Compensate contributors for verified labeled datasets
- **Scientific Computing Grids**: Reward computational contributions to distributed research projects

---

## Related Work

- **Bitcoin (PoW)**: Nakamoto, S. (2008). Bitcoin: A peer-to-peer electronic cash system.
- **Ethereum (PoS)**: Buterin, V. (2014). A next-generation smart contract and decentralized application platform.
- **PPCoin (PoS)**: King, S. & Nadal, S. (2012). PPCoin: Peer-to-peer crypto-currency with proof-of-stake.
- **Proof-of-Useful-Work**: Ball, M. et al. (2017). Proofs of useful work.

---

## License

This work is licensed under the **Apache License 2.0**. See [LICENSE](LICENSE) for details.

---

## Contact

For questions, collaborations, or feedback:

**Darren J. Edwards**  
Department of Public Health  
Swansea University, Swansea, UK  
📧 d.j.edwards@swansea.ac.uk

---

## Acknowledgments

The author thanks anonymous reviewers and colleagues at Swansea University for insightful discussions on cryptoeconomic mechanism design.

---

**Keywords:** Blockchain, Token Economics, Proof-of-Action, Minting Policy, Cryptoeconomics, Sybil Resistance, Mechanism Design, Smart Contracts, Provenance, Utility-Backed Issuance

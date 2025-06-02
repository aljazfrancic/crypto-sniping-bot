# Crypto-Forecasting Build Guide

## 1. On-chain analytics
1. **Cluster wallets** – group addresses that act as one entity.  
2. **Model token flow** – treat the transaction graph as a flow network and compute flux.  
3. **Rank key actors** – use betweenness / eigenvector centrality.  
4. **Find trading communities** – run Louvain or Leiden algorithms.

## 2. Liquidity intelligence
1. Model **bid–ask-spread dynamics** from full order-book depth.  
2. Track **liquidity-provider (LP) migrations** between pools.  
3. Compute **impermanent-loss curves** for multiple price paths.  
4. Derive **slippage functions** mapping trade size → price impact.

## 3. Network-effect metrics
1. Estimate value with **Metcalfe’s law**:  
   \[
   \text{value} = k \times (\text{active addresses})^2
   \]  
2. Calculate **clustering coefficients** of the transaction graph.  
3. Fit **power-law degree distributions** and flag outliers.  
4. Measure **average wallet path length** to confirm small-world behaviour.

## 4. Time-series modelling
### Frequency-domain tools
* FFT, power-spectral density, wavelet and Hilbert transforms.

### Statistical models
* ARIMA (trend), GARCH (volatility), VAR (multi-asset links), cointegration tests.

### Chaos & fractals
* Lyapunov exponents, fractal dimension, Hurst exponent, recurrence plots.

## 5. Market microstructure
1. Implement **Kyle** and **Glosten–Milgrom** price-formation models.  
2. Track **VWAP/TWAP** execution quality.  
3. Monitor **Amihud illiquidity**, bid-ask components, square-root market impact, and resilience.  
4. Scan for **triangular, cross-DEX & cross-chain arbitrage** plus MEV; quantify latency edge.

## 6. Graph-neural-network pipeline
1. Build **token-relationship graphs** (edge weight = shared-liquidity volume).  
2. Train **GCN, GAT or GraphSAGE**; extend to **temporal GNNs**.  
3. Separate layers per DEX; add **bridge-flow data** for cross-chain views.

## 7. Advanced machine learning
* **Reinforcement learning** for trade execution (MDP).  
* **Gaussian processes** & **Kalman filters** for uncertainty-aware forecasts.  
* **Hidden Markov Models** (regime detection).  
* **Portfolio optimisation**: mean-variance, convex & multi-objective.

## 8. Signal-processing utilities
* Digital & adaptive filters.  
* **ICA** for latent factors, **PCA** for dimensionality reduction.

## 9. Ensemble strategy
1. Combine models via **weighted averaging, stacking, Bayesian averaging, dynamic weighting**.  
2. Validate with **walk-forward, purged CV and Monte-Carlo** time-series splits.

---

## Implementation roadmap

| Phase | Key deliverables |
|-------|------------------|
| **1 – Foundation** | FFT & wavelets; basic GCN on top-N tokens; ARIMA/GARCH baselines; simple arbitrage scanner |
| **2 – Advanced**   | Multi-scale wavelets; attention-based temporal GNNs; cross-chain flow analytics; advanced portfolio optimiser |
| **3 – Integration**| Unified ensemble; real-time inference pipelines; embedded risk management; performance-attribution dashboard |

> **Rule of thumb:** Complete each phase only when accuracy, latency and robustness targets are met.

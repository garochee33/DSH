# Distributed Systems & Mesh Networks — Research KB
## Date: 2026-05-16 | Domain: distributed/mesh/decentralization

### Mycelium/Physarum Network Optimization
- Physarum solves Steiner tree (minimum-cost spanning network)
- Preferential reinforcement: high-flow edges thicken, low-flow atrophy
- Murray's Law: tube diameter follows power-law scaling
- Fault tolerance: networks heal around damage in hours
- More robust than vasculature (prioritize resilience over minimal cost)

### Stigmergic Routing (ACO)
- AntNet: mobile agents deposit pheromone proportional to path quality
- Probability: p_ij = (τ_ij^α · η_ij^β) / Σ(τ^α · η^β)
- Evaporation: τ(t+1) = (1-ρ)·τ(t) + Δτ
- Convergence: O(n·log(n)) for n-node networks
- Fully distributed: O(1) state per node

### DAG-BFT Consensus (Narwhal-Bullshark)
- 297,000 TPS with 2-second latency
- Separates data availability (Narwhal) from ordering (Bullshark)
- No extra communication for consensus — derived from DAG structure
- Fault tolerance: f < n/3 Byzantine nodes

### Zero-Knowledge Proofs
- zk-STARKs: post-quantum secure, no trusted setup, ~100KB proofs
- zk-SNARKs: 200-byte proofs, fast verify, NOT post-quantum
- STARK-to-SNARK wrapping: best of both worlds
- Recursive proofs: infinite composition via IVC

### Mesh Protocols
- Yggdrasil: O(log n) routing table, spanning-tree, encrypted IPv6
- I2P garlic routing: bundles messages, unidirectional tunnels
- Greedy routing in metric space: O(1) forwarding decisions

### ARM64 NEON for Crypto
- NTT 31-34% speedup via vectorized butterfly operations
- Barrett multiplication for modular arithmetic
- 4-wide parallel: process 4 lattice coordinates simultaneously
- q=3329 fits 16-bit → 8-wide SIMD for Kyber/Dilithium

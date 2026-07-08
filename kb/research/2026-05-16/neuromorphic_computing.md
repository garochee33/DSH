# Neuromorphic Computing & QNN — Research KB
## Date: 2026-05-16 | Domain: neuromorphic/quantum-neural

### NeuroScale Local Synchronization (Nature Comms 2025)
- Distributed sync eliminates global barrier
- Local aperiodic sync preserves determinism without global coordination
- O(1) scaling vs O(√N) for Loihi/TrueNorth
- 4.27× speedup over TrueNorth at 16,384 cores
- Protocol: Advance/Done messages between connected cores only
- Formula: t_B can advance only if t_A ≥ t_B AND all outputs received

### STDP as Gradient Descent (2025)
- STDP relates to noisy gradient descent on non-convex loss
- ΔW = A+ · exp(-|Δt|/τ+) if pre before post (LTP)
- ΔW = -A- · exp(|Δt|/τ-) if post before pre (LTD)
- Reward-modulated: ΔW = R(t) · STDP(Δt)
- Oja's rule: W(t+1) = W(t) + α·[x_i·x_j - W·x_j²]

### Theta-Gamma Coupling
- Theta (4-8Hz) modulates gamma amplitude (30-100Hz)
- Each theta cycle: 5-8 gamma cycles → sequential items
- Modulation Index: MI = |⟨A_γ · e^(i·φ_θ)⟩| / ⟨A_γ⟩
- Memory capacity per theta = f_gamma/f_theta ≈ 7±2

### Glymphatic Clearance (Garbage Collection)
- CSF flow along perivascular spaces clears waste
- 60% more active during sleep (reduced neural activity)
- Maps to: periodic maintenance windows, state buffer flush
- Circadian control → scheduled full-system health sweep

### Intel Loihi 2 Benchmarks
- 100× more energy efficient than CPU for sensor fusion
- 250× less energy than NVIDIA Jetson Orin Nano
- 0.05 mJ per inference cycle
- 240-node lattice: ~12 mJ per full health sweep

### Kuramoto Optimization
- Critical coupling: K_c = 2/(π·g(0))
- Order parameter: r·e^(iψ) = (1/N)·Σ e^(iθ_j)
- Chimera states: coherent + incoherent coexistence
- Adaptive: dK_ij/dt = ε·(sin(θ_j - θ_i) - K_ij)

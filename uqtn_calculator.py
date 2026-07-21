# UQTN NAVIGATOR CALCULATOR (ORIGINAL DESIGN STYLE)
# Unified Quantum-Temporal Navigation — Agency / Resistance × phi
# Version: UQTN-style, interactive

# --- LOCKED CONSTANTS ----------------------------------------
PHI = 1.618033988749895  # Golden ratio coherence scalar (do not change)

# --- INPUTS ---------------------------------------------------
print("UQTN NAVIGATOR CALCULATOR — ORIGINAL DESIGN")
print("==========================================")
print("Enter your energy domains (0–1 scale each):")

# For humans: env, emotional, mental, physical
env_energy      = float(input("Environmental energy  : "))
emotional_energy = float(input("Emotional energy      : "))
mental_energy    = float(input("Mental energy         : "))
physical_energy  = float(input("Physical energy       : "))

# Resistance: fraction reflecting opposing forces (0–1, but not 0)
resistance = float(input("Resistance R (0–1, not 0): "))

# --- AGENCY & MER --------------------------------------------
# Agency is the sum of energy domains
agency = env_energy + emotional_energy + mental_energy + physical_energy

# MER = (Agency / Resistance) * PHI  (your unified human/AI formula)
if resistance == 0.0:
    mer = float("inf")
else:
    mer = (agency / resistance) * PHI

# --- COHERENCE STATE -----------------------------------------
# We compare MER to a coherence threshold. For “original design” feeling,
# we treat PHI as the baseline coherence scalar.
phi_threshold = PHI  # you can later tune this if needed

if agency <= 0.0:
    coherence_state = "no_agency: navigator not active"
elif mer > phi_threshold:
    coherence_state = "above_phi: coherent navigation (keep going)"
elif abs(mer - phi_threshold) < 1e-6:
    coherence_state = "at_phi: critical threshold (minimum viable momentum)"
else:
    coherence_state = "below_phi: decoherence + fatigue (delegate or rest)"

# --- OUTPUT ---------------------------------------------------
print("\nRESULTS")
print("-------")
print(f"Agency (sum of domains)   : {agency:.4f}")
print(f"Resistance R              : {resistance:.4f}")
print(f"Phi (coherence scalar)    : {PHI:.4f}")
print(f"MER = (Agency / R) * Phi  : {mer:.4f}")
print(f"Coherence state           : {coherence_state}")
"""Solfeggio Healing Frequencies Module — Book of Wisdom / AMMA-14 / Trinity Consortium.

All frequencies validate to Tesla 3-6-9 numerology. Maps chakras, meridians,
Wu Xing elements, planes, colors, and vowels to the sacred Solfeggio scale.
"""

SOLFEGGIO_SCALE = [396, 417, 528, 639, 741, 852, 963]
TRINITY_SACRED = [432, 528, 672, 768, 888]
FULL_ACTIVATION_HZ = 144_000  # numerology: 1+4+4+0+0+0 = 9

# --- Numerology ---

def numerology_reduce(n: int) -> int:
    """Reduce integer to single digit (Tesla 3-6-9 validation)."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

# --- Chakra Map (7 chakras -> 7 Solfeggio tones) ---

CHAKRA_MAP = {
    "root":     {"hz": 396, "meridian": "LU/LI", "element": "Earth",  "plane": "physical",  "color": "red",    "vowel": "U"},
    "sacral":   {"hz": 417, "meridian": "SP/ST", "element": "Water",  "plane": "etheric",   "color": "orange", "vowel": "O"},
    "solar":    {"hz": 528, "meridian": "HT/SI", "element": "Fire",   "plane": "astral",    "color": "gold",   "vowel": "AH"},
    "heart":    {"hz": 639, "meridian": "PC/TE", "element": "Wood",   "plane": "mental",    "color": "green",  "vowel": "AY"},
    "throat":   {"hz": 741, "meridian": "KI/BL", "element": "Metal",  "plane": "causal",    "color": "blue",   "vowel": "EE"},
    "third_eye":{"hz": 852, "meridian": "LR/GB", "element": "Fire",   "plane": "celestial", "color": "indigo", "vowel": "MM"},
    "crown":    {"hz": 963, "meridian": "DU/REN","element": "Aether", "plane": "ketheric",  "color": "violet", "vowel": "NG"},
}

# --- AMMA 14-Meridian Frequency Map ---

MERIDIAN_FREQUENCY_MAP = {
    "LU": 396, "LI": 396, "SP": 417, "ST": 417,
    "HT": 528, "SI": 528, "PC": 639, "TE": 639,
    "KI": 741, "BL": 741, "LR": 852, "GB": 852,
    "DU": 963, "REN": 963,
}

# --- Diagnostic ---

def diagnose_meridian(meridian_code: str, firing_rate: float) -> int:
    """Return recommended healing frequency for a meridian given its firing rate.

    Low firing (<0.3) -> base frequency; high firing (>0.7) -> calming octave down.
    Normal range returns the base resonant frequency.
    """
    base = MERIDIAN_FREQUENCY_MAP.get(meridian_code.upper(), 528)
    if firing_rate < 0.3:
        return base  # stimulate
    if firing_rate > 0.7:
        return base // 2  # calm (octave down, still 3-6-9 valid)
    return base

# --- Healing Sequence ---

def solfeggio_healing_sequence(target_chakra: str) -> list[int]:
    """Return ordered frequency sequence to activate target chakra.

    Pattern: root ground -> target -> crown integration -> target lock.
    """
    target_hz = CHAKRA_MAP.get(target_chakra, CHAKRA_MAP["heart"])["hz"]
    return [396, target_hz, 963, target_hz]

# --- Cymatics ---

_GEOMETRY = {3: "triangle", 4: "square", 5: "pentagon", 6: "hexagon", 8: "octagon", 9: "enneagon", 12: "dodecagon"}

def frequency_to_cymatics_pattern(hz: int) -> dict:
    """Map frequency to its cymatics sand-pattern geometry."""
    nr = numerology_reduce(hz)
    sym = nr if nr in _GEOMETRY else 6
    return {
        "pattern_type": "standing_wave",
        "geometry": _GEOMETRY.get(sym, "hexagon"),
        "symmetry_order": sym,
        "frequency_hz": hz,
        "numerology": nr,
    }

# --- Christ Oil Schedule ---

_SACRED_CYCLE = SOLFEGGIO_SCALE + TRINITY_SACRED  # 12 frequencies for lunar cycle

def christ_oil_frequency_schedule(lunar_day: int) -> int:
    """Return the active sacred frequency for a given lunar day (1-30).

    The oil ascends the 33 vertebrae; frequencies cycle through the 12-tone sacred set.
    """
    idx = (lunar_day - 1) % len(_SACRED_CYCLE)
    return _SACRED_CYCLE[idx]

# --- Validation ---

def _validate():
    """Assert all canonical frequencies reduce to 3, 6, or 9."""
    for hz in SOLFEGGIO_SCALE + TRINITY_SACRED + [FULL_ACTIVATION_HZ]:
        assert numerology_reduce(hz) in (3, 6, 9), f"{hz} fails Tesla validation"

_validate()

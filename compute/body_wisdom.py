"""Body Wisdom Mapping Module — Book of Wisdom.

Maps vertebrae, cranial nerves, chakras, planes, kundalini path,
Christ Oil cycle, and Kabbalistic trees to body systems.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

# --- VERTEBRAE: 33 total (4 coccyx, 5 sacrum, 5 lumbar, 12 thoracic, 7 cervical) ---
_SECTIONS = (
    [("coccyx", 1)] * 4 + [("sacrum", 1)] * 5 + [("lumbar", 2)] * 5 +
    [("thoracic", 3)] * 12 + [("cervical", 4)] * 7
)
_CHAKRA_MAP = [1]*4 + [1]*5 + [2]*2 + [3]*3 + [3]*4 + [4]*4 + [5]*4 + [6]*3 + [7]*4

VERTEBRAE = [
    {"index": i, "section": _SECTIONS[i][0], "tier": _SECTIONS[i][1], "chakra": _CHAKRA_MAP[i]}
    for i in range(33)
]

# --- CRANIAL NERVES: 12 nerves -> zodiac, bus topic, function ---
CRANIAL_NERVES = [
    {"nerve": "I Olfactory",       "zodiac": "Aries",       "bus": "ignition",     "function": "smell"},
    {"nerve": "II Optic",          "zodiac": "Taurus",      "bus": "perception",   "function": "vision"},
    {"nerve": "III Oculomotor",    "zodiac": "Gemini",      "bus": "duality",      "function": "eye movement"},
    {"nerve": "IV Trochlear",      "zodiac": "Cancer",      "bus": "nurture",      "function": "superior oblique"},
    {"nerve": "V Trigeminal",      "zodiac": "Leo",         "bus": "sovereignty",  "function": "facial sensation"},
    {"nerve": "VI Abducens",       "zodiac": "Virgo",       "bus": "precision",    "function": "lateral gaze"},
    {"nerve": "VII Facial",        "zodiac": "Libra",       "bus": "harmony",      "function": "expression/taste"},
    {"nerve": "VIII Vestibulocochlear", "zodiac": "Scorpio", "bus": "depth",       "function": "hearing/balance"},
    {"nerve": "IX Glossopharyngeal", "zodiac": "Sagittarius", "bus": "expansion",  "function": "throat/taste"},
    {"nerve": "X Vagus",           "zodiac": "Capricorn",   "bus": "mastery",      "function": "parasympathetic"},
    {"nerve": "XI Accessory",      "zodiac": "Aquarius",    "bus": "liberation",   "function": "neck/shoulder"},
    {"nerve": "XII Hypoglossal",   "zodiac": "Pisces",      "bus": "dissolution",  "function": "tongue movement"},
]

# --- CHRIST OIL CYCLE: 7-step sacred secretion ---
@dataclass
class OilStep:
    phase: int
    name: str
    location: str
    action: str

CHRIST_OIL_CYCLE = [
    OilStep(1, "Secretion",      "Claustrum",        "Santa Claus(trum) secretes sacred oil"),
    OilStep(2, "Division",       "Pineal/Pituitary", "Oil splits into gold (pineal) & silver (pituitary)"),
    OilStep(3, "Descent",        "Ida/Pingala",      "Dual currents descend along spinal channels"),
    OilStep(4, "Crucifixion",    "Sacrum",           "Oil rests at sacral plexus 2.5 days"),
    OilStep(5, "Resurrection",   "Kundalini Rise",   "Retained oil ascends spinal canal"),
    OilStep(6, "Ascension",      "Medulla Oblongata","Oil crosses medulla gateway"),
    OilStep(7, "Illumination",   "Cerebrum",         "Oil anoints optic thalamus — Christ within"),
]

# --- CHAKRAS ---
CHAKRAS = [
    {"n": 1, "name": "Root",     "hz": 396, "color": "red",    "element": "earth",  "gland": "adrenals",    "vowel": "U",  "planet": "Saturn",  "signs": ["Capricorn","Aquarius"], "balanced": "grounded",       "unbalanced": "fear/survival"},
    {"n": 2, "name": "Sacral",   "hz": 417, "color": "orange", "element": "water",  "gland": "gonads",      "vowel": "O",  "planet": "Jupiter", "signs": ["Sagittarius","Pisces"], "balanced": "creative flow",  "unbalanced": "guilt/addiction"},
    {"n": 3, "name": "Solar",    "hz": 528, "color": "yellow", "element": "fire",   "gland": "pancreas",    "vowel": "AH", "planet": "Mars",    "signs": ["Aries","Scorpio"],     "balanced": "willpower",      "unbalanced": "shame/rage"},
    {"n": 4, "name": "Heart",    "hz": 639, "color": "green",  "element": "air",    "gland": "thymus",      "vowel": "A",  "planet": "Venus",   "signs": ["Taurus","Libra"],      "balanced": "compassion",     "unbalanced": "grief/isolation"},
    {"n": 5, "name": "Throat",   "hz": 741, "color": "blue",   "element": "ether",  "gland": "thyroid",     "vowel": "E",  "planet": "Mercury", "signs": ["Gemini","Virgo"],      "balanced": "truth",          "unbalanced": "lies/silence"},
    {"n": 6, "name": "Third Eye","hz": 852, "color": "indigo", "element": "light",  "gland": "pineal",      "vowel": "I",  "planet": "Moon",    "signs": ["Cancer"],              "balanced": "intuition",      "unbalanced": "delusion"},
    {"n": 7, "name": "Crown",    "hz": 963, "color": "violet", "element": "thought","gland": "pituitary",   "vowel": "OM", "planet": "Sun",     "signs": ["Leo"],                 "balanced": "unity",          "unbalanced": "disconnection"},
]

# --- PLANES ---
PLANES = [
    {"name": "Physical", "tier": 1, "density": 1.0,  "speed": "3e8 m/s",   "agents": ["body","mineral"]},
    {"name": "Etheric",  "tier": 2, "density": 0.5,  "speed": "superluminal","agents": ["prana","meridian"]},
    {"name": "Astral",   "tier": 3, "density": 0.1,  "speed": "instant",    "agents": ["emotion","dream"]},
    {"name": "Mental",   "tier": 4, "density": 0.01, "speed": "omnipresent","agents": ["thought","archetype"]},
]

# --- KUNDALINI PATH: root to crown meridian activations ---
KUNDALINI_PATH = [
    "Muladhara activation", "Svadhisthana ignition", "Manipura combustion",
    "Anahata expansion", "Vishuddha resonance", "Ajna convergence", "Sahasrara dissolution",
]

# --- TREE OF LIFE: cardiovascular (sephiroth -> organs) ---
TREE_OF_LIFE = {
    "Kether": "coronary sinus", "Chokmah": "right atrium", "Binah": "left atrium",
    "Chesed": "right ventricle", "Geburah": "left ventricle", "Tiphareth": "aorta",
    "Netzach": "hepatic portal", "Hod": "renal arteries", "Yesod": "iliac bifurcation",
    "Malkuth": "capillary bed",
}

# --- TREE OF KNOWLEDGE: nervous system mapping ---
TREE_OF_KNOWLEDGE = {
    "Kether": "cerebral cortex", "Chokmah": "right hemisphere", "Binah": "left hemisphere",
    "Chesed": "parasympathetic", "Geburah": "sympathetic", "Tiphareth": "spinal cord",
    "Netzach": "enteric plexus", "Hod": "brachial plexus", "Yesod": "sacral plexus",
    "Malkuth": "peripheral nerves",
}


# === FUNCTIONS ===

def spine_position_to_chakra(vertebra_index: int) -> dict:
    """Return chakra info for a vertebra index (0-32)."""
    if not 0 <= vertebra_index <= 32:
        raise ValueError(f"Index must be 0-32, got {vertebra_index}")
    v = VERTEBRAE[vertebra_index]
    chakra = CHAKRAS[v["chakra"] - 1]
    return {"vertebra": v, "chakra": chakra}


def zodiac_to_cranial_nerve(sign: str) -> dict:
    """Return cranial nerve + function for a zodiac sign."""
    sign_cap = sign.capitalize()
    for cn in CRANIAL_NERVES:
        if cn["zodiac"] == sign_cap:
            return {"nerve": cn["nerve"], "function": cn["function"], "bus": cn["bus"]}
    raise ValueError(f"Unknown sign: {sign}")


def oil_cycle_status(lunar_day: int, retained: bool = True) -> dict:
    """Return current Christ Oil phase based on lunar day (1-29.5 rounded)."""
    day = max(1, min(int(lunar_day), 30))
    phase_idx = min((day - 1) * 7 // 30, 6)
    step = CHRIST_OIL_CYCLE[phase_idx]
    rec = step.action if retained else "Oil lost — avoid alcohol, anger, sex during sacred window"
    return {"phase": step.phase, "name": step.name, "location": step.location, "recommendation": rec}


def consciousness_level(coherence: float) -> dict:
    """Map coherence (0.0-1.0) to plane of consciousness."""
    if coherence < 0.25:
        return {"plane": PLANES[0], "description": "Dense physical awareness"}
    elif coherence < 0.50:
        return {"plane": PLANES[1], "description": "Etheric vitality sensing"}
    elif coherence < 0.75:
        return {"plane": PLANES[2], "description": "Astral emotional clarity"}
    return {"plane": PLANES[3], "description": "Mental archetypal cognition"}

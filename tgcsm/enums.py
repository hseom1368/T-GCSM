# ==============================================================================
# T-GCSM v2.0: Taiwan Ground Combat Simulation Model
# enums.py - Enum 정의
# ==============================================================================

"""
Enumeration definitions for T-GCSM v2.0
Provides type safety and clarity for various game states and properties.
"""

from enum import Enum


class Faction(Enum):
    """Represents the two main factions in the simulation."""
    PLA = "PLA"  # People's Liberation Army (China)
    ROC = "ROC"  # Republic of China (Taiwan)


class UnitType(Enum):
    """Different types of military units in the simulation."""
    Armor = "Armor"
    Mechanized = "Mechanized"
    Infantry = "Infantry"
    Artillery = "Artillery"
    Engineer = "Engineer"
    AttackHelo = "AttackHelo"


class SupplyStatus(Enum):
    """Supply status of units."""
    In_Supply = "In_Supply"
    Out_Of_Supply = "Out_Of_Supply"


class PortStatus(Enum):
    """Operational status of ports."""
    Operational = "Operational"
    Damaged = "Damaged"
    Destroyed = "Destroyed"


class AirfieldStatus(Enum):
    """Operational status of airfields."""
    Operational = "Operational"
    Damaged = "Damaged"
    Destroyed = "Destroyed"


class Phase(Enum):
    """Different phases in each turn of the simulation."""
    AIR_SEA_EFFECTS = "Air & Sea Effects Phase"
    SUPPLY_STATUS = "Supply Status Determination Phase"
    PLAYER_ACTION = "Player Action Phase"
    COMBAT_RESOLUTION = "Combat Resolution Phase"
    LOGISTICS_REINFORCEMENT = "Logistics & Reinforcement Phase"
    END_OF_TURN = "End of Turn & Victory Check Phase"


class ActionType(Enum):
    """Types of actions that units can perform."""
    MOVE = "MOVE"
    ATTACK = "ATTACK"
    FORTIFY = "FORTIFY"
    ARTILLERY_SUPPORT = "ARTILLERY_SUPPORT"
    PASS = "PASS"


class TerrainType(Enum):
    """Different terrain types affecting movement and combat."""
    Plains = "Plains"
    Hills = "Hills"
    Mountain = "Mountain"
    Urban = "Urban"
    Forest = "Forest"
    River_Crossing = "River_Crossing"
    Coastal = "Coastal"
    Ocean = "Ocean"
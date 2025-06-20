# ==============================================================================
# T-GCSM v2.0: Taiwan Ground Combat Simulation Model
# __init__.py - 패키지 초기화
# ==============================================================================

"""
T-GCSM v2.0: Taiwan Ground Combat Simulation Model

A turn-based hexagonal wargame simulation of ground combat in Taiwan,
based on the CSIS report "The First Battle of the Next War: Wargaming a Chinese Invasion of Taiwan"
"""

from .config import __version__, __author__
from .enums import *
from .data_loader import load_data
from .models import Hex, Unit
from .agents import Agent, HumanAgent, ScriptedAgent
from .engine import SimulationEngine
from .analysis import print_final_summary, export_game_data

__all__ = [
    # Version info
    '__version__',
    '__author__',
    
    # Core functions
    'load_data',
    
    # Enums
    'Faction',
    'UnitType',
    'SupplyStatus',
    'PortStatus',
    'AirfieldStatus',
    'Phase',
    'ActionType',
    'TerrainType',
    
    # Models
    'Hex',
    'Unit',
    
    # Agents
    'Agent',
    'HumanAgent',
    'ScriptedAgent',
    
    # Engine
    'SimulationEngine',
    
    # Analysis
    'print_final_summary',
    'export_game_data',
]
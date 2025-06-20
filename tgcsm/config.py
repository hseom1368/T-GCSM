# ==============================================================================
# T-GCSM v2.0: Taiwan Ground Combat Simulation Model
# config.py - 환경 설정 및 라이브러리 임포트
# ==============================================================================

"""
Configuration module for T-GCSM v2.0
Contains all necessary imports and global configuration settings.
"""

# Standard library imports
import pandas as pd
import numpy as np
import random
import copy
from abc import ABC, abstractmethod
import io
from enum import Enum
import re
import collections

# Version information
__version__ = "2.0.0"
__author__ = "T-GCSM Development Team"

# Simulation constants
MAX_TURNS = 10  # Maximum number of turns (35 days)
TURN_DURATION = 3.5  # Days per turn

# Map constants
HEX_SIZE = 30  # km per hex
MAX_SUPPLY_DISTANCE = 10  # Maximum hex distance for supply lines

# Combat constants
D20_SIDES = 20  # Dice sides for combat resolution

# PLA initial values
PLA_INITIAL_AMPHIBIOUS_CAPACITY = 300
PLA_LIFT_CAPACITY_DECAY_RATE = 0.25
PLA_INTERDICTION_SUCCESS_RATE = 0.6

# Artillery range
ARTILLERY_RANGE = 2  # hexes

# Debug settings
DEBUG_MODE = False
VERBOSE_COMBAT = True

# Random seed for reproducibility (set to None for random behavior)
RANDOM_SEED = None

if RANDOM_SEED is not None:
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
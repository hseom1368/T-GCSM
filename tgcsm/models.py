# ==============================================================================
# T-GCSM v2.0: Taiwan Ground Combat Simulation Model
# models.py - 핵심 데이터 모델 클래스
# ==============================================================================

"""
Core data model classes for T-GCSM v2.0
Includes Hex and Unit classes representing the game board and military units.
"""

from .enums import Faction, UnitType, SupplyStatus, PortStatus, AirfieldStatus


class Hex:
    """
    Represents an individual hex on the Taiwan hex map.
    
    Attributes:
        hex_id (str): Unique identifier (e.g., "A10")
        name (str): Name of the location
        terrain_type (str): Type of terrain affecting movement and combat
        is_port (bool): Whether this hex contains a port
        port_name (str): Name of the port if present
        is_airfield (bool): Whether this hex contains an airfield
        airfield_name (str): Name of the airfield if present
        is_victory_point (bool): Whether this is a victory point location
        owner (Faction): Current controlling faction
        port_status (PortStatus): Operational status of port
        airfield_status (AirfieldStatus): Operational status of airfield
        units (list): List of Unit objects currently in this hex
    """
    
    def __init__(self, hex_data):
        """Initialize a Hex from a data row."""
        self.hex_id = hex_data['hex_id']
        self.name = hex_data['name']
        self.terrain_type = hex_data['terrain_type']
        self.is_port = bool(hex_data['is_port'])
        self.port_name = hex_data['port_name']
        self.is_airfield = bool(hex_data['is_airfield'])
        self.airfield_name = hex_data['airfield_name']
        self.is_victory_point = bool(hex_data['is_victory_point'])
        self.owner = Faction(hex_data['initial_owner'])
        self.port_status = PortStatus.Operational if self.is_port else None
        self.airfield_status = AirfieldStatus.Operational if self.is_airfield else None
        self.units = []  # List of Unit objects in this hex

    def __repr__(self):
        return f"Hex({self.hex_id}: {self.name}, {self.terrain_type}, Owner: {self.owner.value})"

    def get_defense_modifier(self, terrain_modifiers_df):
        """Get the defense multiplier for this hex's terrain type."""
        terrain_row = terrain_modifiers_df[terrain_modifiers_df['terrain_type'] == self.terrain_type]
        if not terrain_row.empty:
            return terrain_row['defense_multiplier'].iloc[0]
        return 1.0

    def get_movement_cost(self, terrain_modifiers_df):
        """Get the movement cost factor for this hex's terrain type."""
        terrain_row = terrain_modifiers_df[terrain_modifiers_df['terrain_type'] == self.terrain_type]
        if not terrain_row.empty:
            return terrain_row['movement_cost_factor'].iloc[0]
        return 1.0


class Unit:
    """
    Represents a military battalion unit in the simulation.
    
    Attributes:
        unit_id (str): Unique identifier
        faction (Faction): PLA or ROC
        unit_type (UnitType): Type of unit (Armor, Infantry, etc.)
        is_reserve (bool): Whether this is a reserve unit
        location_hex_id (str): Current hex location
        strength (int): Current strength (0-100)
        initial_strength (int): Starting strength
        supply_status (SupplyStatus): Current supply status
        turns_out_of_supply (int): Number of turns without supply
        base_attack (int): Base attack value
        base_defense (int): Base defense value
        movement_points (int): Movement points per turn
        lift_cost (int): Cost to transport this unit
        has_moved (bool): Whether unit has moved this turn
        has_attacked (bool): Whether unit has attacked this turn
        is_fortified (bool): Whether unit is fortified
        is_supporting_arty (bool): Whether artillery is providing support
    """
    
    def __init__(self, unit_id, unit_data, battalion_templates, equipment_catalog):
        """Initialize a Unit from data rows."""
        self.unit_id = unit_id
        self.faction = Faction(unit_data['brigade'].split()[0] if 'PLA' in unit_id else 'ROC')
        
        # Get template data
        template_id = unit_data['template_id']
        template_rows = battalion_templates[battalion_templates['template_id'] == template_id]
        
        if not template_rows.empty:
            template = template_rows.iloc[0]
            self.unit_type = UnitType(template['unit_type'])
        else:
            # Default for units without templates
            self.unit_type = UnitType.Infantry
        
        self.is_reserve = bool(unit_data['is_reserve'])
        self.location_hex_id = unit_data['location_hex_id'] if unit_data['location_hex_id'] else None
        self.strength = int(unit_data['initial_strength'])
        self.initial_strength = self.strength
        self.supply_status = SupplyStatus.In_Supply
        self.turns_out_of_supply = 0
        
        # Calculate combat values based on unit type and equipment
        self._calculate_combat_values(template_rows, equipment_catalog)
        
        # Set movement points based on unit type
        self._set_movement_points()
        
        # Lift cost for PLA units
        self.lift_cost = int(unit_data['lift_cost']) if 'lift_cost' in unit_data else 0
        
        # Turn status flags
        self.has_moved = False
        self.has_attacked = False
        self.is_fortified = False
        self.is_supporting_arty = False

    def _calculate_combat_values(self, template_rows, equipment_catalog):
        """Calculate attack and defense values based on equipment."""
        if template_rows.empty or equipment_catalog.empty:
            # Default values by unit type
            default_values = {
                UnitType.Armor: (15, 12),
                UnitType.Mechanized: (10, 10),
                UnitType.Infantry: (8, 12),
                UnitType.Artillery: (4, 4),
                UnitType.Engineer: (4, 6),
                UnitType.AttackHelo: (12, 2)
            }
            self.base_attack, self.base_defense = default_values.get(self.unit_type, (8, 8))
            return
        
        total_attack = 0
        total_defense = 0
        total_equipment = 0
        
        for _, row in template_rows.iterrows():
            equipment_id = row['equipment_id']
            quantity = row['quantity'] if 'quantity' in row and row['quantity'] > 0 else 0
            
            if equipment_id and quantity > 0:
                equipment_rows = equipment_catalog[equipment_catalog['equipment_id'] == equipment_id]
                if not equipment_rows.empty:
                    equipment = equipment_rows.iloc[0]
                    # Simplified combat value calculation
                    attack_value = self._calculate_equipment_attack(equipment)
                    defense_value = self._calculate_equipment_defense(equipment)
                    total_attack += attack_value * quantity
                    total_defense += defense_value * quantity
                    total_equipment += quantity
        
        if total_equipment > 0:
            # Normalize by equipment count and apply unit type modifiers
            self.base_attack = int(total_attack / total_equipment)
            self.base_defense = int(total_defense / total_equipment)
        else:
            # Use default values for unit type
            default_values = {
                UnitType.Armor: (15, 12),
                UnitType.Mechanized: (10, 10),
                UnitType.Infantry: (8, 12),
                UnitType.Artillery: (4, 4),
                UnitType.Engineer: (4, 6),
                UnitType.AttackHelo: (12, 2)
            }
            self.base_attack, self.base_defense = default_values.get(self.unit_type, (8, 8))

    def _calculate_equipment_attack(self, equipment):
        """Calculate attack value from equipment stats."""
        base_value = 0
        if 'main_gun_mm' in equipment and equipment['main_gun_mm'] > 0:
            base_value += equipment['main_gun_mm'] / 10
        if 'has_atgm' in equipment and equipment['has_atgm']:
            base_value += 3
        if 'engine_hp' in equipment:
            base_value += equipment['engine_hp'] / 200
        return min(20, max(1, int(base_value)))

    def _calculate_equipment_defense(self, equipment):
        """Calculate defense value from equipment stats."""
        base_value = 0
        if 'armor_rating' in equipment:
            base_value += equipment['armor_rating'] * 1.5
        if 'weight_tonnes' in equipment:
            base_value += equipment['weight_tonnes'] / 10
        return min(20, max(1, int(base_value)))

    def _set_movement_points(self):
        """Set movement points based on unit type."""
        movement_by_type = {
            UnitType.Armor: 6,
            UnitType.Mechanized: 8,
            UnitType.Infantry: 4,
            UnitType.Artillery: 4,
            UnitType.Engineer: 4,
            UnitType.AttackHelo: 12
        }
        self.movement_points = movement_by_type.get(self.unit_type, 4)

    def get_current_attack(self):
        """Get current attack value adjusted for strength."""
        return self.base_attack * (self.strength / 100)

    def get_current_defense(self):
        """Get current defense value adjusted for strength."""
        return self.base_defense * (self.strength / 100)

    def take_damage(self, percentage):
        """Apply damage as a percentage of current strength."""
        damage = int(round(self.strength * (percentage / 100)))
        self.strength -= damage
        if self.strength < 0:
            self.strength = 0
        print(f"  - {self.unit_id} takes {percentage}% damage. New strength: {self.strength}")

    def is_destroyed(self):
        """Check if unit is destroyed."""
        return self.strength <= 0

    def can_move(self):
        """Check if unit can move this turn."""
        return not self.has_moved and not self.has_attacked and self.strength > 0

    def can_attack(self):
        """Check if unit can attack this turn."""
        return not self.has_attacked and self.strength > 0

    def __repr__(self):
        return (f"Unit({self.unit_id}, {self.faction.value}, {self.unit_type.value}, "
                f"Str: {self.strength}, Loc: {self.location_hex_id})")
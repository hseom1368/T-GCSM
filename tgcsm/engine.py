# ==============================================================================
# T-GCSM v2.0: Taiwan Ground Combat Simulation Model
# engine.py - 시뮬레이션 엔진
# ==============================================================================

"""
Main simulation engine for T-GCSM v2.0
Manages game state, enforces rules, and runs the simulation loop.
"""

import random
import copy
import collections
import re
from .config import *
from .enums import *
from .models import Hex, Unit


class SimulationEngine:
    """
    Main engine that manages the game state and runs the simulation.
    
    Attributes:
        data: Dictionary of all game data (maps, units, etc.)
        pla_agent: Agent controlling PLA forces
        roc_agent: Agent controlling ROC forces
        turn_number: Current turn number
        max_turns: Maximum number of turns
        game_over: Whether the game has ended
        winner: Winning faction if game is over
        hexes: Dictionary of all hex objects
        units: Dictionary of all unit objects
        pla_reinforcement_pool: List of PLA units available for reinforcement
    """
    
    def __init__(self, data_files, pla_agent_class, roc_agent_class):
        """Initialize the simulation engine."""
        print("Initializing Simulation Engine...")
        self.data = data_files
        
        # Instantiate agents with reference to engine
        self.pla_agent = pla_agent_class(Faction.PLA, self)
        self.roc_agent = roc_agent_class(Faction.ROC, self)
        
        # Game state variables
        self.turn_number = 1
        self.max_turns = MAX_TURNS
        self.current_phase = None
        self.game_over = False
        self.winner = None
        self.pending_combats = []
        
        # Air/sea effects variables
        self.is_roc_interdicted = False
        self.pla_cas_available = True
        self.roc_cas_available = False
        self.pla_amphibious_lift_capacity = PLA_INITIAL_AMPHIBIOUS_CAPACITY
        self.pla_lift_capacity_decay_rate = PLA_LIFT_CAPACITY_DECAY_RATE
        
        # Initialize map and units
        self._initialize_map()
        self._setup_hex_grid()
        self._initialize_units()
        print("Initialization Complete.")
    
    def _initialize_map(self):
        """Initialize Hex objects from map data."""
        self.hexes = {
            row['hex_id']: Hex(row)
            for _, row in self.data['hex_map'].iterrows()
        }
    
    def _initialize_units(self):
        """Initialize Unit objects and place them on the map."""
        self.units = {}
        self.pla_reinforcement_pool = []
        
        # Initialize ROC units
        for _, row in self.data['oob_roc_initial_setup'].iterrows():
            unit = Unit(
                row['unit_id'], 
                row, 
                self.data['battalion_templates'], 
                self.data['equipment_catalog']
            )
            self.units[unit.unit_id] = unit
            if unit.location_hex_id and unit.location_hex_id in self.hexes:
                self.hexes[unit.location_hex_id].units.append(unit)
        
        # Create PLA reinforcement pool
        for _, row in self.data['oob_pla_reinforcements'].iterrows():
            unit = Unit(
                row['unit_id'], 
                row, 
                self.data['battalion_templates'], 
                self.data['equipment_catalog']
            )
            self.pla_reinforcement_pool.append(unit)
    
    def _setup_hex_grid(self):
        """Set up hex coordinate system and neighbor relationships."""
        self.hex_coords = {}
        
        # Convert offset coordinates to axial coordinates
        for hex_id in self.hexes:
            col_char = hex_id[0]
            row_num = int(hex_id[1:])
            # "odd-q" vertical layout conversion
            q = ord(col_char) - ord('A')
            r = row_num - (q - (q & 1)) // 2
            self.hex_coords[hex_id] = (q, r)
        
        # Create reverse mapping for fast lookup
        self.coords_to_hex = {v: k for k, v in self.hex_coords.items()}
        
        # Calculate neighbors for each hex
        self.hex_neighbors = {hex_id: [] for hex_id in self.hexes}
        axial_directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        
        for hex_id, (q, r) in self.hex_coords.items():
            for dq, dr in axial_directions:
                neighbor_coords = (q + dq, r + dr)
                if neighbor_coords in self.coords_to_hex:
                    self.hex_neighbors[hex_id].append(self.coords_to_hex[neighbor_coords])
    
    def _get_neighbors(self, hex_id):
        """Get all neighboring hex IDs for a given hex."""
        return self.hex_neighbors.get(hex_id, [])
    
    def get_hex_distance(self, hex1_id, hex2_id):
        """Calculate distance between two hexes using axial coordinates."""
        if hex1_id not in self.hex_coords or hex2_id not in self.hex_coords:
            return float('inf')
        q1, r1 = self.hex_coords[hex1_id]
        q2, r2 = self.hex_coords[hex2_id]
        return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) / 2
    
    def run_simulation(self):
        """Main game loop."""
        print("\n===== T-GCSM v2.0 SIMULATION START =====")
        
        while self.turn_number <= self.max_turns and not self.game_over:
            print(f"\n{'='*20} TURN {self.turn_number} {'='*20}")
            
            # Reset unit action flags at start of turn
            for unit in self.units.values():
                unit.has_moved = False
                unit.has_attacked = False
                unit.is_fortified = False
                unit.is_supporting_arty = False
            
            # Execute phases
            self._run_air_sea_phase()
            self._run_supply_phase()
            self._run_player_action_phase(Faction.PLA)
            self._run_player_action_phase(Faction.ROC)
            self._run_combat_resolution_phase()
            self._run_logistics_reinforcement_phase()
            self._run_end_of_turn_phase()
            
            if not self.game_over:
                self.turn_number += 1
        
        print("\n===== SIMULATION END =====")
        if self.winner:
            print(f"Winner: {self.winner.value}")
        elif self.game_over:
            print("Game Over: Stalemate or Max Turns Reached.")
        else:
            print(f"Max turns ({self.max_turns}) reached. Result: STALEMATE")
            self.game_over = True
            self.winner = Faction.ROC  # ROC wins by survival
            print(f"Winner: {self.winner.value} (Survival)")
    
    def _run_air_sea_phase(self):
        """Phase 1: Air & Sea Effects"""
        self.current_phase = Phase.AIR_SEA_EFFECTS
        print(f"\n--- {self.current_phase.value} ---")
        
        # Rule 2.3.1: ROC interdiction
        if random.random() < PLA_INTERDICTION_SUCCESS_RATE:
            self.is_roc_interdicted = True
            print("  - PLA air interdiction successful. ROC movement penalized this turn.")
        else:
            self.is_roc_interdicted = False
            print("  - PLA air interdiction failed.")
        
        # Rule 2.3.3: PLA amphibious capacity decay
        if self.turn_number <= 4:
            decay = self.pla_amphibious_lift_capacity * self.pla_lift_capacity_decay_rate
            self.pla_amphibious_lift_capacity -= decay
            print(f"  - PLA amphibious lift capacity reduced by {decay:.0f}. "
                  f"New capacity: {self.pla_amphibious_lift_capacity:.0f}")
        else:
            print(f"  - PLA amphibious lift capacity stable at {self.pla_amphibious_lift_capacity:.0f}")
    
    def _run_supply_phase(self):
        """Phase 2: Supply Status Determination"""
        self.current_phase = Phase.SUPPLY_STATUS
        print(f"\n--- {self.current_phase.value} ---")
        
        for unit in self.units.values():
            if unit.location_hex_id:
                is_in_supply = self._is_unit_in_supply(unit)
                if is_in_supply:
                    unit.supply_status = SupplyStatus.In_Supply
                    unit.turns_out_of_supply = 0
                else:
                    unit.supply_status = SupplyStatus.Out_Of_Supply
                    unit.turns_out_of_supply += 1
                    print(f"  - Unit {unit.unit_id} is Out of Supply for "
                          f"{unit.turns_out_of_supply} turn(s).")
    
    def _is_unit_in_supply(self, unit):
        """Check if a unit is connected to a supply source."""
        if not unit.location_hex_id:
            return False
    
    def _run_player_action_phase(self, faction: Faction):
        """Phase 3: Player Action"""
        self.current_phase = Phase.PLAYER_ACTION
        print(f"\n--- {self.current_phase.value} ({faction.value}) ---")
        
        agent = self.pla_agent if faction == Faction.PLA else self.roc_agent
        game_state = self._get_game_state(faction)
        possible_actions = self._get_possible_actions(faction)
        
        if not possible_actions or (len(possible_actions) == 1 and 
                                   possible_actions[0]['action'] == ActionType.PASS.value):
            print(f"  - No possible actions for {faction.value}. Passing turn.")
            return
        
        chosen_actions = agent.choose_actions(
            copy.deepcopy(game_state), 
            copy.deepcopy(possible_actions)
        )
        
        if not chosen_actions or (len(chosen_actions) == 1 and 
                                 chosen_actions[0]['action'] == ActionType.PASS.value):
            print(f"  - {faction.value} chose to PASS.")
            return
        
        # Execute chosen actions
        for action in chosen_actions:
            print(f"  - {faction.value} executes: {action}")
            if action['action'] == ActionType.MOVE.value:
                self._execute_move(action)
            elif action['action'] == ActionType.ATTACK.value:
                self._declare_attack(action)
            elif action['action'] == ActionType.FORTIFY.value:
                self._execute_fortify(action)
            elif action['action'] == ActionType.ARTILLERY_SUPPORT.value:
                self._declare_artillery_support(action)
    
    def _get_game_state(self, faction: Faction):
        """Create game state dictionary for AI agents."""
        unit_data = []
        for unit in self.units.values():
            if unit.strength > 0:
                unit_data.append({
                    'unit_id': unit.unit_id,
                    'faction': unit.faction.value,
                    'unit_type': unit.unit_type.value,
                    'strength': unit.strength,
                    'location_hex_id': unit.location_hex_id,
                    'supply_status': unit.supply_status.value,
                    'turns_out_of_supply': unit.turns_out_of_supply,
                    'is_reserve': unit.is_reserve,
                    'base_attack': unit.base_attack,
                    'base_defense': unit.base_defense,
                    'movement_points': unit.movement_points,
                    'has_moved': unit.has_moved,
                    'has_attacked': unit.has_attacked,
                })
        
        map_data = {
            hex_id: {
                'name': h.name,
                'terrain_type': h.terrain_type,
                'owner': h.owner.value,
                'is_victory_point': h.is_victory_point,
                'port_status': h.port_status.value if h.port_status else None,
                'airfield_status': h.airfield_status.value if h.airfield_status else None,
                'unit_ids': [u.unit_id for u in h.units]
            } for hex_id, h in self.hexes.items()
        }
        
        player_specific_data = {
            'PLA': {
                'amphibious_lift_capacity': self.pla_amphibious_lift_capacity,
                'reinforcement_pool_count': len(self.pla_reinforcement_pool)
            },
            'ROC': {}
        }
        
        return {
            'turn_number': self.turn_number,
            'current_phase': self.current_phase.value,
            'current_player_faction': faction.value,
            'map_data': map_data,
            'unit_data': unit_data,
            'player_specific_data': player_specific_data
        }
    
    def _get_possible_actions(self, faction: Faction):
        """Generate all valid actions for a faction."""
        actions = []
        my_units = [u for u in self.units.values() 
                   if u.faction == faction and u.strength > 0 and 
                   not u.has_moved and not u.has_attacked]
        
        declared_attack_targets = set()
        
        for unit in my_units:
            if not unit.location_hex_id:
                continue
            
            # Generate movement actions
            q = collections.deque([
                (unit.location_hex_id, [unit.location_hex_id], unit.movement_points)
            ])
            visited_paths = {unit.location_hex_id}
            
            while q:
                current_hex, path, remaining_mp = q.popleft()
                
                # Add movement action if not starting hex
                if path[-1] != unit.location_hex_id:
                    actions.append({
                        'action': ActionType.MOVE.value,
                        'unit_id': unit.unit_id,
                        'path': path
                    })
                
                # Stop if entering enemy ZoC
                if len(path) > 1 and self._is_in_enemy_zoc(current_hex, faction):
                    continue
                
                # Explore neighbors
                for neighbor in self._get_neighbors(current_hex):
                    if neighbor not in visited_paths:
                        terrain = self.hexes[neighbor].terrain_type
                        terrain_mod = self.data['terrain_modifiers']
                        cost_row = terrain_mod.loc[terrain_mod['terrain_type'] == terrain]
                        cost_factor = cost_row['movement_cost_factor'].iloc[0] if not cost_row.empty else 1.0
                        
                        move_cost = 1.0 * cost_factor
                        
                        if remaining_mp >= move_cost:
                            visited_paths.add(neighbor)
                            q.append((neighbor, path + [neighbor], remaining_mp - move_cost))
            
            # Generate attack actions
            if unit.unit_type not in [UnitType.Artillery, UnitType.Engineer]:
                for neighbor_id in self._get_neighbors(unit.location_hex_id):
                    if neighbor_id in declared_attack_targets:
                        continue
                    neighbor_hex = self.hexes[neighbor_id]
                    if any(u.faction != faction for u in neighbor_hex.units):
                        attacking_units = [
                            u.unit_id for u in self.hexes[unit.location_hex_id].units 
                            if u.faction == faction and not u.has_attacked
                        ]
                        if attacking_units:
                            attack_action = {
                                'action': ActionType.ATTACK.value,
                                'attacking_units': attacking_units,
                                'target_hex': neighbor_id
                            }
                            actions.append(attack_action)
                            declared_attack_targets.add(neighbor_id)
            
            # Generate artillery support actions
            if unit.unit_type == UnitType.Artillery:
                for target_hex_id in self.hexes:
                    if any(u.faction != faction for u in self.hexes[target_hex_id].units):
                        if self.get_hex_distance(unit.location_hex_id, target_hex_id) <= ARTILLERY_RANGE:
                            actions.append({
                                'action': ActionType.ARTILLERY_SUPPORT.value,
                                'unit_id': unit.unit_id,
                                'target_hex': target_hex_id
                            })
            
            # Generate fortify action
            actions.append({
                'action': ActionType.FORTIFY.value,
                'unit_id': unit.unit_id
            })
        
        # Always include pass option
        actions.append({'action': ActionType.PASS.value})
        return actions
    
    def _execute_move(self, action):
        """Execute a unit movement action."""
        unit = self.units.get(action['unit_id'])
        if not unit or unit.has_moved or unit.has_attacked:
            return
        
        path = action['path']
        start_hex_id = path[0]
        end_hex_id = path[-1]
        
        # Ensure unit is in the start hex
        if unit in self.hexes[start_hex_id].units:
            self.hexes[start_hex_id].units.remove(unit)
            self.hexes[end_hex_id].units.append(unit)
            unit.location_hex_id = end_hex_id
            unit.has_moved = True
            print(f"  - Unit {unit.unit_id} moved from {start_hex_id} to {end_hex_id}.")
        else:
            print(f"  - ERROR: Unit {unit.unit_id} not found in start hex {start_hex_id}.")
    
    def _execute_fortify(self, action):
        """Execute a fortify action."""
        unit = self.units.get(action['unit_id'])
        if not unit or unit.has_moved or unit.has_attacked:
            return
        unit.is_fortified = True
        unit.has_moved = True
        unit.has_attacked = True
    
    def _declare_attack(self, action):
        """Declare an attack for later resolution."""
        self.pending_combats.append(action)
        for unit_id in action['attacking_units']:
            unit = self.units.get(unit_id)
            if unit:
                unit.has_attacked = True
                unit.has_moved = True
    
    def _declare_artillery_support(self, action):
        """Declare artillery support."""
        unit = self.units.get(action['unit_id'])
        if not unit or unit.has_moved or unit.has_attacked:
            return
        unit.is_supporting_arty = True
        unit.has_moved = True
        unit.has_attacked = True
    
    def _run_combat_resolution_phase(self):
        """Phase 4: Combat Resolution"""
        self.current_phase = Phase.COMBAT_RESOLUTION
        print(f"\n--- {self.current_phase.value} ---")
        
        if not self.pending_combats:
            print("  - No combats to resolve.")
            return
        
        for combat in self.pending_combats:
            self._resolve_combat(combat)
        
        self.pending_combats = []
    
    def _resolve_combat(self, combat_declaration):
        """Resolve a single combat."""
        attackers = [self.units[uid] for uid in combat_declaration['attacking_units'] 
                    if uid in self.units]
        if not attackers:
            return
        
        target_hex = self.hexes[combat_declaration['target_hex']]
        defenders = [u for u in target_hex.units if u.faction != attackers[0].faction]
        
        if not defenders:
            print(f"  - Combat at {target_hex.hex_id} cancelled: No defenders.")
            # Capture hex
            target_hex.owner = attackers[0].faction
            print(f"  - Hex {target_hex.hex_id} captured by {target_hex.owner.value}.")
            return
        
        print(f"\n  Combat at {target_hex.hex_id}: "
              f"{[u.unit_id for u in attackers]} vs {[u.unit_id for u in defenders]}")
        
        # 1. Calculate modified combat power
        total_attack_power = sum(u.get_current_attack() for u in attackers)
        total_defense_power = sum(u.get_current_defense() for u in defenders)
        
        # 2. Apply modifiers
        # Terrain modifier
        terrain_mod = target_hex.get_defense_modifier(self.data['terrain_modifiers'])
        total_defense_power *= terrain_mod
        print(f"    Terrain modifier: x{terrain_mod}")
        
        # Fortification bonus
        fortified_defenders = [d for d in defenders if d.is_fortified]
        if fortified_defenders:
            total_defense_power *= 1.5
            print(f"    Fortification bonus applied")
        
        # CAS bonus
        if attackers[0].faction == Faction.PLA and self.pla_cas_available:
            total_attack_power *= 1.2
            print(f"    PLA CAS bonus applied")
        
        # Out of supply penalty
        oos_attackers = [a for a in attackers if a.supply_status == SupplyStatus.Out_Of_Supply]
        if oos_attackers:
            total_attack_power *= 0.5
            print(f"    Attackers out of supply penalty")
        
        oos_defenders = [d for d in defenders if d.supply_status == SupplyStatus.Out_Of_Supply]
        if oos_defenders:
            total_defense_power *= 0.5
            print(f"    Defenders out of supply penalty")
        
        # 3. Calculate odds ratio
        if total_defense_power > 0:
            odds_ratio = total_attack_power / total_defense_power
        else:
            odds_ratio = 99.0
        
        print(f"    Final odds: {odds_ratio:.2f}:1 ({total_attack_power:.1f} vs {total_defense_power:.1f})")
        
        # 4. Map to CRT column
        if odds_ratio < 0.75:
            crt_column = '1:2'
        elif odds_ratio < 1.5:
            crt_column = '1:1'
        elif odds_ratio < 2.5:
            crt_column = '2:1'
        elif odds_ratio < 3.5:
            crt_column = '3:1'
        else:
            crt_column = '4:1+'
        
        # 5. Roll d20
        d20_roll = random.randint(1, D20_SIDES)
        print(f"    CRT Column: {crt_column}, d20 roll: {d20_roll}")
        
        # 6. Look up result in CRT
        crt = self.data['combat_results_table']
        result_row = None
        if d20_roll <= 5:
            result_row = crt[crt['d20_Roll'] == '1-5']
        elif d20_roll <= 10:
            result_row = crt[crt['d20_Roll'] == '6-10']
        elif d20_roll <= 15:
            result_row = crt[crt['d20_Roll'] == '11-15']
        elif d20_roll <= 19:
            result_row = crt[crt['d20_Roll'] == '16-19']
        else:
            result_row = crt[crt['d20_Roll'] == '20']
        
        if result_row.empty:
            print("    ERROR: CRT lookup failed")
            return
        
        result = result_row[crt_column].iloc[0]
        print(f"    Result: {result}")
        
        # 7. Apply results
        self._apply_combat_result(result, attackers, defenders, target_hex)
    
    def _apply_combat_result(self, result, attackers, defenders, target_hex):
        """Apply combat result from CRT."""
        # Parse result string
        match = re.match(r'A-(\d+)/D-(\d+)(?:_(\w+))?', result)
        if not match:
            print(f"    ERROR: Invalid result format: {result}")
            return
        
        attacker_loss = int(match.group(1))
        defender_loss = int(match.group(2))
        special = match.group(3) if match.group(3) else None
        
        # Apply losses
        if attacker_loss > 0:
            print(f"    Attackers take {attacker_loss}% losses")
            for unit in attackers:
                unit.take_damage(attacker_loss)
        
        if defender_loss > 0:
            print(f"    Defenders take {defender_loss}% losses")
            for unit in defenders:
                unit.take_damage(defender_loss)
        
        # Handle special results
        units_to_retreat = []
        if special == 'DR':  # Defender retreat
            print("    Defenders must retreat!")
            units_to_retreat = [d for d in defenders if d.strength > 0]
            self._retreat_units(units_to_retreat, target_hex, defenders[0].faction)
        elif special == 'AR':  # Attacker retreat
            print("    Attackers must retreat!")
            # Attackers retreat to their starting hex
            for attacker in attackers:
                if attacker.strength > 0:
                    print(f"      {attacker.unit_id} retreats (stays in place)")
        elif special == 'DX':  # Defender eliminated
            print("    Defenders eliminated!")
            for unit in defenders:
                unit.strength = 0
        elif special == 'AX':  # Attacker eliminated
            print("    Attackers eliminated!")
            for unit in attackers:
                unit.strength = 0
        
        # Check for hex capture
        surviving_defenders = [d for d in defenders if d.strength > 0 and d not in units_to_retreat]
        if not surviving_defenders and target_hex.owner != attackers[0].faction:
            target_hex.owner = attackers[0].faction
            print(f"    Hex {target_hex.hex_id} captured by {target_hex.owner.value}!")
    
    def _retreat_units(self, units, from_hex, faction):
        """Handle unit retreat."""
        # Find valid retreat hexes
        valid_retreats = []
        for neighbor_id in self._get_neighbors(from_hex.hex_id):
            neighbor = self.hexes[neighbor_id]
            # Can't retreat into enemy units or enemy ZoC
            if not any(u.faction != faction for u in neighbor.units):
                if not self._is_in_enemy_zoc(neighbor_id, faction):
                    valid_retreats.append(neighbor)
        
        if valid_retreats:
            # Retreat to random valid hex
            retreat_hex = random.choice(valid_retreats)
            for unit in units:
                from_hex.units.remove(unit)
                retreat_hex.units.append(unit)
                unit.location_hex_id = retreat_hex.hex_id
                print(f"      {unit.unit_id} retreats to {retreat_hex.hex_id}")
        else:
            # No valid retreat - units take additional damage
            print("      No valid retreat path! Units take additional damage.")
            for unit in units:
                unit.take_damage(10)
    
    def _run_logistics_reinforcement_phase(self):
        """Phase 5: Logistics & Reinforcement (PLA only)"""
        self.current_phase = Phase.LOGISTICS_REINFORCEMENT
        print(f"\n--- {self.current_phase.value} ---")
        
        lift_for_reinforce = self.pla_amphibious_lift_capacity
        
        # Find available landing zones
        landing_zones = [h for h in self.hexes.values() 
                        if h.terrain_type == 'Coastal' and h.owner == Faction.PLA]
        
        if not landing_zones:
            print("  - No available landing zones for PLA reinforcements.")
            return
        
        # Copy reinforcement pool to avoid modification during iteration
        reinforcement_pool_copy = list(self.pla_reinforcement_pool)
        
        for unit_to_land in reinforcement_pool_copy:
            if unit_to_land.lift_cost <= lift_for_reinforce:
                lift_for_reinforce -= unit_to_land.lift_cost
                
                # Remove from pool
                self.pla_reinforcement_pool.remove(unit_to_land)
                
                # Land at zone with fewest units
                landing_zone = min(landing_zones, key=lambda h: len(h.units))
                unit_to_land.location_hex_id = landing_zone.hex_id
                self.units[unit_to_land.unit_id] = unit_to_land
                landing_zone.units.append(unit_to_land)
                
                print(f"  - PLA reinforces with {unit_to_land.unit_id} at {landing_zone.hex_id}. "
                      f"Remaining lift: {lift_for_reinforce}")
            else:
                # Can't fit this unit
                continue
    
    def _run_end_of_turn_phase(self):
        """Phase 6: End of Turn & Victory Check"""
        self.current_phase = Phase.END_OF_TURN
        print(f"\n--- {self.current_phase.value} ---")
        
        # Remove destroyed units
        destroyed_units = [uid for uid, u in self.units.items() if u.strength <= 0]
        for uid in destroyed_units:
            unit = self.units[uid]
            if unit.location_hex_id and unit in self.hexes[unit.location_hex_id].units:
                self.hexes[unit.location_hex_id].units.remove(unit)
            del self.units[uid]
            print(f"  - Unit {uid} (strength 0) removed from game.")
        
        # Victory condition check
        taipei_hex = self.hexes['A10']
        if taipei_hex.owner == Faction.PLA:
            self.game_over = True
            self.winner = Faction.PLA
            print("  - VICTORY CHECK: PLA has captured Taipei!")
        
        # Check if PLA has any units left
        pla_units = [u for u in self.units.values() if u.faction == Faction.PLA]
        if not pla_units and not self.pla_reinforcement_pool:
            self.game_over = True
            self.winner = Faction.ROC
            print("  - VICTORY CHECK: All PLA forces eliminated!")
        
        # BFS to find supply path
        q = collections.deque([(unit.location_hex_id, [unit.location_hex_id])])
        visited = {unit.location_hex_id}
        
        while q:
            current_hex_id, path = q.popleft()
            
            # Check if this is a supply source
            if self._is_supply_source(current_hex_id, unit.faction):
                return True
            
            # Path length limit
            if len(path) > MAX_SUPPLY_DISTANCE:
                continue
            
            # Explore neighbors
            for neighbor_id in self._get_neighbors(current_hex_id):
                if neighbor_id not in visited:
                    # Check if path is blocked by enemy ZoC
                    if not self._is_in_enemy_zoc(neighbor_id, unit.faction):
                        visited.add(neighbor_id)
                        q.append((neighbor_id, path + [neighbor_id]))
        
        return False
    
    def _is_supply_source(self, hex_id, faction):
        """Check if a hex is a supply source for a faction."""
        hex_obj = self.hexes[hex_id]
        
        if faction == Faction.ROC:
            # Eastern edge of map (column J)
            q, _ = self.hex_coords[hex_id]
            return q >= 9
        
        elif faction == Faction.PLA:
            # PLA-controlled operational ports/airfields
            if hex_obj.owner == Faction.PLA:
                if hex_obj.is_port and hex_obj.port_status == PortStatus.Operational:
                    return True
                if hex_obj.is_airfield and hex_obj.airfield_status == AirfieldStatus.Operational:
                    return True
            
            # Coastal beachhead in first 3 turns
            if (self.turn_number <= 3 and 
                hex_obj.terrain_type == 'Coastal' and 
                hex_obj.owner == Faction.PLA):
                return True
        
        return False
    
    def _is_in_enemy_zoc(self, hex_id, friendly_faction):
        """Check if a hex is in enemy Zone of Control."""
        enemy_faction = Faction.ROC if friendly_faction == Faction.PLA else Faction.PLA
        
        for neighbor_id in self._get_neighbors(hex_id):
            neighbor_hex = self.hexes.get(neighbor_id)
            if neighbor_hex:
                for unit in neighbor_hex.units:
                    # Only certain unit types project ZoC
                    if (unit.faction == enemy_faction and 
                        unit.strength > 0 and 
                        unit.unit_type in [UnitType.Armor, UnitType.Mechanized, UnitType.Infantry]):
                        return True
        
        return False
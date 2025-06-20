# ==============================================================================
# T-GCSM v2.0: Taiwan Ground Combat Simulation Model
# agents.py - AI 에이전트 구현
# ==============================================================================

"""
Agent implementations for T-GCSM v2.0
Includes abstract base class and concrete implementations for human and AI players.
"""

from abc import ABC, abstractmethod
from .enums import Faction, ActionType
from .config import ARTILLERY_RANGE


class Agent(ABC):
    """
    Abstract base class for all player agents (human, scripted AI, LLM).
    
    Attributes:
        faction (Faction): The faction this agent controls (PLA or ROC)
        engine: Reference to the simulation engine for helper functions
    """
    
    def __init__(self, faction: Faction, engine):
        """
        Initialize the agent.
        
        Args:
            faction: The faction this agent controls
            engine: Reference to the simulation engine
        """
        self.faction = faction
        self.engine = engine  # Reference for distance calculations etc.

    @abstractmethod
    def choose_actions(self, game_state: dict, possible_actions: list) -> list:
        """
        Choose actions for this turn given the current game state.
        
        Args:
            game_state: Dictionary containing complete game state
            possible_actions: List of all valid actions
            
        Returns:
            List of chosen actions to execute
        """
        pass


class HumanAgent(Agent):
    """
    Human player agent that accepts input through console prompts.
    """
    
    def choose_actions(self, game_state: dict, possible_actions: list) -> list:
        """
        Interactively prompt the human player to choose actions.
        """
        print(f"\n--- {self.faction.value} Player's Turn ---")
        print(f"Turn {game_state['turn_number']}")
        
        # Show unit status
        my_units = [u for u in game_state['unit_data'] 
                   if u['faction'] == self.faction.value and u['strength'] > 0]
        print(f"\nYour units ({len(my_units)} total):")
        for unit in my_units:
            print(f"  {unit['unit_id']}: {unit['unit_type']} at {unit['location_hex_id']} "
                  f"(Str: {unit['strength']}, Moved: {unit['has_moved']}, "
                  f"Attacked: {unit['has_attacked']})")
        
        # Group actions by type
        move_actions = [a for a in possible_actions if a['action'] == ActionType.MOVE.value]
        attack_actions = [a for a in possible_actions if a['action'] == ActionType.ATTACK.value]
        fortify_actions = [a for a in possible_actions if a['action'] == ActionType.FORTIFY.value]
        arty_actions = [a for a in possible_actions if a['action'] == ActionType.ARTILLERY_SUPPORT.value]
        
        chosen_actions = []
        
        while True:
            print("\nAvailable action types:")
            print("1. Move units")
            print("2. Attack")
            print("3. Fortify")
            print("4. Artillery support")
            print("5. Pass turn")
            
            choice = input("Choose action type (1-5): ").strip()
            
            if choice == '1' and move_actions:
                # Show available moves
                print("\nAvailable moves:")
                for i, action in enumerate(move_actions[:10]):  # Limit display
                    print(f"{i}: Move {action['unit_id']} to {action['path'][-1]}")
                
                idx = input("Select move index (or 'back'): ").strip()
                if idx.isdigit() and 0 <= int(idx) < len(move_actions):
                    chosen_actions.append(move_actions[int(idx)])
                    # Remove this unit's actions from future options
                    unit_id = move_actions[int(idx)]['unit_id']
                    move_actions = [a for a in move_actions if a['unit_id'] != unit_id]
                    
            elif choice == '2' and attack_actions:
                # Show available attacks
                print("\nAvailable attacks:")
                for i, action in enumerate(attack_actions[:10]):
                    print(f"{i}: Attack {action['target_hex']} with {action['attacking_units']}")
                
                idx = input("Select attack index (or 'back'): ").strip()
                if idx.isdigit() and 0 <= int(idx) < len(attack_actions):
                    chosen_actions.append(attack_actions[int(idx)])
                    
            elif choice == '3' and fortify_actions:
                # Show units that can fortify
                print("\nUnits that can fortify:")
                for i, action in enumerate(fortify_actions[:10]):
                    print(f"{i}: Fortify {action['unit_id']}")
                
                idx = input("Select fortify index (or 'back'): ").strip()
                if idx.isdigit() and 0 <= int(idx) < len(fortify_actions):
                    chosen_actions.append(fortify_actions[int(idx)])
                    
            elif choice == '4' and arty_actions:
                # Show artillery support options
                print("\nArtillery support options:")
                for i, action in enumerate(arty_actions[:10]):
                    print(f"{i}: {action['unit_id']} support attack on {action['target_hex']}")
                
                idx = input("Select artillery index (or 'back'): ").strip()
                if idx.isdigit() and 0 <= int(idx) < len(arty_actions):
                    chosen_actions.append(arty_actions[int(idx)])
                    
            elif choice == '5':
                # Pass turn
                if not chosen_actions:
                    return [{'action': ActionType.PASS.value}]
                else:
                    confirm = input("End turn with current actions? (y/n): ").strip().lower()
                    if confirm == 'y':
                        return chosen_actions
            
            # Show chosen actions so far
            if chosen_actions:
                print(f"\nChosen actions so far: {len(chosen_actions)}")


class ScriptedAgent(Agent):
    """
    Simple rule-based AI agent for testing and baseline behavior.
    
    Strategy:
    - PLA: Move towards Taipei, then Kaohsiung
    - ROC: Intercept nearest enemy units
    """
    
    def choose_actions(self, game_state: dict, possible_actions: list) -> list:
        """
        Choose actions based on simple heuristic rules.
        """
        if not possible_actions:
            return [{'action': ActionType.PASS.value}]
        
        actions_to_take = []
        units_acted = set()
        
        # Get my units
        my_units = [u for u in game_state['unit_data'] 
                   if u['faction'] == self.faction.value and u['strength'] > 0]
        
        if self.faction == Faction.PLA:
            # PLA strategy: Capture victory points
            primary_target = 'A10'  # Taipei
            secondary_target = 'G2'  # Kaohsiung
            
            # Check if Taipei is already captured
            taipei_owner = game_state['map_data']['A10']['owner']
            if taipei_owner == 'PLA':
                primary_target = secondary_target
            
            # 1. Execute attacks first
            for action in possible_actions:
                if action['action'] == ActionType.ATTACK.value:
                    # Check if any attacking unit hasn't acted yet
                    can_act = any(uid not in units_acted for uid in action['attacking_units'])
                    if can_act:
                        actions_to_take.append(action)
                        for uid in action['attacking_units']:
                            units_acted.add(uid)
            
            # 2. Move units towards objectives
            available_units = [u for u in my_units if u['unit_id'] not in units_acted]
            for unit in available_units:
                if not unit['location_hex_id']:
                    continue
                
                best_move = None
                min_dist = self.engine.get_hex_distance(unit['location_hex_id'], primary_target)
                
                for action in possible_actions:
                    if (action['action'] == ActionType.MOVE.value and 
                        action['unit_id'] == unit['unit_id']):
                        end_hex = action['path'][-1]
                        dist_primary = self.engine.get_hex_distance(end_hex, primary_target)
                        
                        if dist_primary < min_dist:
                            min_dist = dist_primary
                            best_move = action
                
                if best_move:
                    actions_to_take.append(best_move)
                    units_acted.add(unit['unit_id'])
        
        elif self.faction == Faction.ROC:
            # ROC strategy: Defend and intercept
            pla_units = [u for u in game_state['unit_data'] 
                        if u['faction'] == 'PLA' and u['location_hex_id']]
            
            if not pla_units:
                return [{'action': ActionType.PASS.value}]
            
            # 1. Execute attacks on adjacent enemies
            for action in possible_actions:
                if action['action'] == ActionType.ATTACK.value:
                    can_act = any(uid not in units_acted for uid in action['attacking_units'])
                    if can_act:
                        actions_to_take.append(action)
                        for uid in action['attacking_units']:
                            units_acted.add(uid)
            
            # 2. Move towards nearest enemy
            available_units = [u for u in my_units if u['unit_id'] not in units_acted]
            for unit in available_units:
                if not unit['location_hex_id']:
                    continue
                
                # Find closest enemy
                closest_enemy = min(pla_units, 
                                  key=lambda e: self.engine.get_hex_distance(
                                      unit['location_hex_id'], e['location_hex_id']))
                
                best_move = None
                min_dist = self.engine.get_hex_distance(
                    unit['location_hex_id'], closest_enemy['location_hex_id'])
                
                for action in possible_actions:
                    if (action['action'] == ActionType.MOVE.value and 
                        action['unit_id'] == unit['unit_id']):
                        end_hex = action['path'][-1]
                        dist = self.engine.get_hex_distance(
                            end_hex, closest_enemy['location_hex_id'])
                        if dist < min_dist:
                            min_dist = dist
                            best_move = action
                
                if best_move:
                    actions_to_take.append(best_move)
                    units_acted.add(unit['unit_id'])
            
            # 3. Fortify units in victory points
            for unit in my_units:
                if (unit['unit_id'] not in units_acted and 
                    unit['location_hex_id'] and
                    game_state['map_data'][unit['location_hex_id']]['is_victory_point']):
                    fortify_actions = [a for a in possible_actions 
                                     if a['action'] == ActionType.FORTIFY.value and 
                                     a['unit_id'] == unit['unit_id']]
                    if fortify_actions:
                        actions_to_take.append(fortify_actions[0])
                        units_acted.add(unit['unit_id'])
        
        # Return chosen actions or PASS if none
        if not actions_to_take:
            return [{'action': ActionType.PASS.value}]
        
        return actions_to_take
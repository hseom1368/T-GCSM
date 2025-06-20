# ==============================================================================
# T-GCSM v2.0: Taiwan Ground Combat Simulation Model
# analysis.py - 게임 후 분석 함수
# ==============================================================================

"""
Post-game analysis functions for T-GCSM v2.0
Provides summary statistics and visualization capabilities.
"""

from .enums import Faction, UnitType


def print_final_summary(engine):
    """
    Print comprehensive final game summary.
    
    Args:
        engine: The SimulationEngine instance after game completion
    """
    print("\n" + "="*60)
    print("FINAL GAME SUMMARY")
    print("="*60)
    
    # Basic info
    print(f"\nGame Duration: {engine.turn_number} turns ({engine.turn_number * 3.5:.1f} days)")
    
    if engine.winner:
        print(f"Winner: {engine.winner.value}")
        if engine.winner == Faction.PLA:
            print("Victory Type: Conquest (Taipei captured)")
        else:
            print("Victory Type: Survival (Taiwan maintains autonomy)")
    else:
        print("Result: Stalemate")
    
    # Force summary
    print("\n" + "-"*40)
    print("FINAL FORCE STATUS")
    print("-"*40)
    
    # Get final state
    final_state = engine._get_game_state(Faction.PLA)
    
    # PLA summary
    print("\nPLA Forces:")
    pla_units = [u for u in final_state['unit_data'] if u['faction'] == 'PLA']
    print_force_summary(pla_units, "PLA")
    
    # ROC summary
    print("\nROC Forces:")
    roc_units = [u for u in final_state['unit_data'] if u['faction'] == 'ROC']
    print_force_summary(roc_units, "ROC")
    
    # Territory control
    print("\n" + "-"*40)
    print("TERRITORY CONTROL")
    print("-"*40)
    
    pla_hexes = 0
    roc_hexes = 0
    key_locations = []
    
    for hex_id, hex_data in final_state['map_data'].items():
        if hex_data['owner'] == 'PLA':
            pla_hexes += 1
        else:
            roc_hexes += 1
        
        # Track key locations
        if hex_data['is_victory_point'] or hex_data['port_status'] or hex_data['airfield_status']:
            key_locations.append((hex_id, hex_data))
    
    total_hexes = pla_hexes + roc_hexes
    print(f"\nPLA controls: {pla_hexes} hexes ({pla_hexes/total_hexes*100:.1f}%)")
    print(f"ROC controls: {roc_hexes} hexes ({roc_hexes/total_hexes*100:.1f}%)")
    
    print("\nKey Locations:")
    for hex_id, hex_data in sorted(key_locations, key=lambda x: x[0]):
        status_parts = []
        if hex_data['is_victory_point']:
            status_parts.append("VP")
        if hex_data['port_status']:
            status_parts.append(f"Port-{hex_data['port_status']}")
        if hex_data['airfield_status']:
            status_parts.append(f"Airfield-{hex_data['airfield_status']}")
        
        status = ", ".join(status_parts)
        print(f"  - {hex_data['name']} ({hex_id}): {hex_data['owner']} [{status}]")
    
    # Casualties
    print("\n" + "-"*40)
    print("CASUALTIES")
    print("-"*40)
    
    # Calculate casualties
    pla_casualties = calculate_casualties(engine, Faction.PLA)
    roc_casualties = calculate_casualties(engine, Faction.ROC)
    
    print(f"\nPLA Casualties: {pla_casualties['total_strength_lost']} strength points")
    print(f"  - Units destroyed: {pla_casualties['units_destroyed']}")
    print(f"  - Units damaged: {pla_casualties['units_damaged']}")
    
    print(f"\nROC Casualties: {roc_casualties['total_strength_lost']} strength points")
    print(f"  - Units destroyed: {roc_casualties['units_destroyed']}")
    print(f"  - Units damaged: {roc_casualties['units_damaged']}")
    
    # Strategic assessment
    print("\n" + "-"*40)
    print("STRATEGIC ASSESSMENT")
    print("-"*40)
    
    if engine.winner == Faction.PLA:
        print("\nPLA achieved strategic objectives:")
        print("- Successfully established beachhead")
        print("- Captured key victory points")
        print("- Overcame ROC defensive positions")
    else:
        print("\nROC achieved strategic objectives:")
        print("- Prevented PLA conquest")
        print("- Maintained control of key areas")
        print("- Inflicted sufficient attrition on invasion force")
    
    # Remaining reinforcements
    if engine.pla_reinforcement_pool:
        print(f"\nUncommitted PLA reserves: {len(engine.pla_reinforcement_pool)} battalions")


def print_force_summary(units, faction_name):
    """Print summary of a faction's forces."""
    if not units:
        print(f"  - No {faction_name} units remaining")
        return
    
    # Count by type
    unit_counts = {}
    total_strength = 0
    
    for unit in units:
        unit_type = unit['unit_type']
        if unit_type not in unit_counts:
            unit_counts[unit_type] = {'count': 0, 'strength': 0}
        unit_counts[unit_type]['count'] += 1
        unit_counts[unit_type]['strength'] += unit['strength']
        total_strength += unit['strength']
    
    print(f"  - Total units: {len(units)}")
    print(f"  - Total strength: {total_strength}")
    print("  - By type:")
    
    for unit_type, data in sorted(unit_counts.items()):
        avg_strength = data['strength'] / data['count']
        print(f"    * {unit_type}: {data['count']} units (avg strength: {avg_strength:.1f})")


def calculate_casualties(engine, faction):
    """Calculate casualties for a faction."""
    casualties = {
        'units_destroyed': 0,
        'units_damaged': 0,
        'total_strength_lost': 0
    }
    
    # Check initial setup
    if faction == Faction.ROC:
        initial_data = engine.data['oob_roc_initial_setup']
        for _, row in initial_data.iterrows():
            unit_id = row['unit_id']
            initial_strength = row['initial_strength']
            
            # Check if unit still exists
            if unit_id in engine.units:
                current_unit = engine.units[unit_id]
                if current_unit.strength < initial_strength:
                    casualties['units_damaged'] += 1
                    casualties['total_strength_lost'] += initial_strength - current_unit.strength
            else:
                casualties['units_destroyed'] += 1
                casualties['total_strength_lost'] += initial_strength
    
    elif faction == Faction.PLA:
        # For PLA, check all reinforcements that were deployed
        initial_pool_size = len(engine.data['oob_pla_reinforcements'])
        current_pool_size = len(engine.pla_reinforcement_pool)
        deployed_units = initial_pool_size - current_pool_size
        
        # Count PLA units in play
        pla_units_in_play = [u for u in engine.units.values() if u.faction == Faction.PLA]
        
        for unit in pla_units_in_play:
            if unit.strength < unit.initial_strength:
                casualties['units_damaged'] += 1
                casualties['total_strength_lost'] += unit.initial_strength - unit.strength
        
        # Destroyed units = deployed - still in play
        casualties['units_destroyed'] = deployed_units - len(pla_units_in_play)
        casualties['total_strength_lost'] += casualties['units_destroyed'] * 100
    
    return casualties


def generate_turn_summary(engine, turn_number):
    """Generate summary for a specific turn."""
    summary = {
        'turn': turn_number,
        'pla_units': 0,
        'roc_units': 0,
        'pla_strength': 0,
        'roc_strength': 0,
        'combats': 0,
        'hexes_captured': 0
    }
    
    # This would require turn-by-turn logging in the engine
    # For now, return placeholder
    return summary


def export_game_data(engine, filename):
    """Export game data to CSV for external analysis."""
    import pandas as pd
    
    # Get final state
    final_state = engine._get_game_state(Faction.PLA)
    
    # Export unit data
    unit_df = pd.DataFrame(final_state['unit_data'])
    unit_df.to_csv(f"{filename}_units.csv", index=False)
    
    # Export map control
    map_data = []
    for hex_id, hex_info in final_state['map_data'].items():
        map_data.append({
            'hex_id': hex_id,
            'name': hex_info['name'],
            'owner': hex_info['owner'],
            'terrain': hex_info['terrain_type'],
            'is_vp': hex_info['is_victory_point'],
            'units': len(hex_info['unit_ids'])
        })
    
    map_df = pd.DataFrame(map_data)
    map_df.to_csv(f"{filename}_map.csv", index=False)
    
    print(f"Game data exported to {filename}_units.csv and {filename}_map.csv")
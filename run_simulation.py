#!/usr/bin/env python3
# ==============================================================================
# T-GCSM v2.0: Taiwan Ground Combat Simulation Model
# run_simulation.py - 메인 실행 스크립트
# ==============================================================================

"""
Main script to run the T-GCSM v2.0 simulation.
Can be run directly or imported for use in notebooks.
"""

import argparse
import sys
from tgcsm import (
    load_data, 
    SimulationEngine, 
    HumanAgent, 
    ScriptedAgent,
    print_final_summary,
    export_game_data
)


def setup_simulation(pla_agent_type='ai', roc_agent_type='ai'):
    """
    Set up the simulation with specified agent types.
    
    Args:
        pla_agent_type: 'human' or 'ai' for PLA agent
        roc_agent_type: 'human' or 'ai' for ROC agent
        
    Returns:
        SimulationEngine instance ready to run
    """
    print("Setting up T-GCSM v2.0...")
    print("Loading data...")
    all_data = load_data()
    
    print("Setting up agents...")
    # Select agent classes based on type
    agent_map = {
        'human': HumanAgent,
        'ai': ScriptedAgent
    }
    
    pla_agent_class = agent_map.get(pla_agent_type.lower(), ScriptedAgent)
    roc_agent_class = agent_map.get(roc_agent_type.lower(), ScriptedAgent)
    
    print(f"  PLA Agent: {pla_agent_class.__name__}")
    print(f"  ROC Agent: {roc_agent_class.__name__}")
    
    # Create engine
    simulation_engine = SimulationEngine(all_data, pla_agent_class, roc_agent_class)
    
    return simulation_engine


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Run the Taiwan Ground Combat Simulation Model (T-GCSM) v2.0'
    )
    
    parser.add_argument(
        '--pla-agent',
        choices=['human', 'ai'],
        default='ai',
        help='Agent type for PLA forces (default: ai)'
    )
    
    parser.add_argument(
        '--roc-agent',
        choices=['human', 'ai'],
        default='ai',
        help='Agent type for ROC forces (default: ai)'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        help='Export game data to CSV files with given prefix'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress detailed turn output'
    )
    
    args = parser.parse_args()
    
    # Set up and run simulation
    try:
        engine = setup_simulation(args.pla_agent, args.roc_agent)
        
        # Run the simulation
        print("\nStarting simulation...")
        print("="*60)
        engine.run_simulation()
        
        # Print final summary
        print_final_summary(engine)
        
        # Export data if requested
        if args.export:
            print(f"\nExporting game data...")
            export_game_data(engine, args.export)
        
        # Return exit code based on winner
        if engine.winner:
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
        return 2
    except Exception as e:
        print(f"\nError during simulation: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())
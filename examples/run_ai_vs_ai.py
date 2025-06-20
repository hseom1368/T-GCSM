#!/usr/bin/env python3
"""
Example: AI vs AI Simulation
Runs a fully automated game between two AI agents.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tgcsm import (
    load_data,
    SimulationEngine,
    ScriptedAgent,
    print_final_summary,
    export_game_data
)


def run_ai_battle():
    """Run an automated AI vs AI battle."""
    print("="*60)
    print("T-GCSM v2.0: AI vs AI Battle")
    print("="*60)
    print("\nBoth sides will be controlled by scripted AI agents.")
    print("PLA will attempt to capture Taipei.")
    print("ROC will defend and intercept PLA forces.\n")
    
    # Load data
    print("Loading game data...")
    data = load_data()
    
    # Create simulation with AI agents
    print("Initializing simulation...")
    engine = SimulationEngine(data, ScriptedAgent, ScriptedAgent)
    
    # Run simulation
    print("\nStarting battle...\n")
    engine.run_simulation()
    
    # Show results
    print_final_summary(engine)
    
    # Ask if user wants to export data
    export_choice = input("\nExport game data to CSV? (y/n): ").strip().lower()
    if export_choice == 'y':
        filename = input("Enter filename prefix (default: ai_vs_ai): ").strip()
        if not filename:
            filename = "ai_vs_ai"
        export_game_data(engine, filename)
    
    return engine


if __name__ == "__main__":
    try:
        engine = run_ai_battle()
        print("\nSimulation complete!")
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
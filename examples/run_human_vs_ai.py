#!/usr/bin/env python3
"""
Example: Human vs AI Simulation
Allows a human player to command one side against an AI opponent.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tgcsm import (
    load_data,
    SimulationEngine,
    HumanAgent,
    ScriptedAgent,
    print_final_summary,
    Faction
)


def choose_faction():
    """Let the player choose which faction to command."""
    print("\nWhich faction would you like to command?")
    print("1. PLA (People's Liberation Army) - Invading force")
    print("2. ROC (Republic of China/Taiwan) - Defending force")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == '1':
            return 'PLA'
        elif choice == '2':
            return 'ROC'
        else:
            print("Invalid choice. Please enter 1 or 2.")


def print_game_intro(player_faction):
    """Print game introduction and objectives."""
    print("\n" + "="*60)
    print("GAME INTRODUCTION")
    print("="*60)
    
    if player_faction == 'PLA':
        print("\nYou are commanding the PLA invasion force.")
        print("\nYour objectives:")
        print("- Establish and maintain beachheads on Taiwan's coast")
        print("- Advance inland and capture key objectives")
        print("- Most importantly: Capture Taipei (hex A10) to win")
        print("\nChallenges:")
        print("- Your amphibious lift capacity decreases each turn")
        print("- You must maintain supply lines to your units")
        print("- ROC forces will defend key positions")
    else:
        print("\nYou are commanding the ROC defense forces.")
        print("\nYour objectives:")
        print("- Prevent PLA from capturing Taipei")
        print("- Destroy or attrit PLA invasion forces")
        print("- Hold out for 10 turns (35 days) to win")
        print("\nAdvantages:")
        print("- You start with units already deployed")
        print("- Interior lines and defensive terrain")
        print("- PLA must come to you")
    
    print("\nGame mechanics:")
    print("- Each turn represents 3.5 days")
    print("- Units can move OR attack each turn")
    print("- Combat uses terrain modifiers and dice rolls")
    print("- Keep units in supply for full effectiveness")
    
    input("\nPress Enter to start the game...")


def run_human_vs_ai():
    """Run a game with human player vs AI."""
    print("="*60)
    print("T-GCSM v2.0: Human vs AI Battle")
    print("="*60)
    
    # Choose faction
    player_faction = choose_faction()
    ai_faction = 'ROC' if player_faction == 'PLA' else 'PLA'
    
    print(f"\nYou will play as: {player_faction}")
    print(f"AI will play as: {ai_faction}")
    
    # Show introduction
    print_game_intro(player_faction)
    
    # Load data
    print("\nLoading game data...")
    data = load_data()
    
    # Create simulation with appropriate agents
    print("Initializing simulation...")
    if player_faction == 'PLA':
        engine = SimulationEngine(data, HumanAgent, ScriptedAgent)
    else:
        engine = SimulationEngine(data, ScriptedAgent, HumanAgent)
    
    # Run simulation
    print("\nStarting battle...\n")
    engine.run_simulation()
    
    # Show results
    print_final_summary(engine)
    
    # Check victory
    if engine.winner:
        if engine.winner.value == player_faction:
            print("\n*** CONGRATULATIONS! You have achieved victory! ***")
        else:
            print("\n*** DEFEAT! The AI has won this battle. ***")
    else:
        print("\n*** STALEMATE! Neither side achieved their objectives. ***")
    
    return engine


def main():
    """Main function with replay option."""
    while True:
        try:
            engine = run_human_vs_ai()
            
            # Ask for replay
            replay = input("\nWould you like to play again? (y/n): ").strip().lower()
            if replay != 'y':
                print("\nThank you for playing T-GCSM v2.0!")
                break
                
        except KeyboardInterrupt:
            print("\n\nGame interrupted by user.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()
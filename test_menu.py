#!/usr/bin/env python3
"""
Interactive test menu for RSI Trading Bot
"""
import sys
import subprocess
from pathlib import Path


def print_header():
    """Print menu header"""
    print("\n" + "="*70)
    print("🧪 RSI TRADING BOT - MENU DE TEST INTERACTIF")
    print("="*70)


def print_menu():
    """Print main menu"""
    print("\n📋 Choisissez un test:\n")
    print("  1. 🔬 Test des Indicateurs Techniques (rapide)")
    print("  2. 🤖 Demo Bot - Rapide (20 itérations)")
    print("  3. 🤖 Demo Bot - Standard (50 itérations)")
    print("  4. 🤖 Demo Bot - Complet (100 itérations)")
    print("  5. 🧪 Tests Unitaires (pytest)")
    print("  6. 📊 Suite Complète (tous les tests)")
    print("  7. 🚀 Lancer le Bot (Mode Simulation)")
    print("  8. 🌐 Lancer Bot + Dashboard (2 terminaux)")
    print("  9. 📊 Dashboard Seul (bot doit tourner)")
    print("  0. ❌ Quitter")
    print()


def run_command(cmd: list, description: str):
    """Run a command and handle errors"""
    print(f"\n{'='*70}")
    print(f"▶️  {description}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            cmd,
            check=False,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print(f"\n✅ {description} - SUCCÈS")
        else:
            print(f"\n⚠️  {description} - Terminé avec code {result.returncode}")
        
        return result.returncode
        
    except KeyboardInterrupt:
        print(f"\n⚠️  {description} - Interrompu par l'utilisateur")
        return 1
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return 1


def test_indicators():
    """Test technical indicators"""
    return run_command(
        ["python", "test_indicators.py"],
        "Test des Indicateurs Techniques"
    )


def demo_bot_quick():
    """Run quick demo"""
    return run_command(
        ["python", "test_demo.py", "--iterations", "20", "--speed", "0.1"],
        "Demo Bot - Rapide"
    )


def demo_bot_standard():
    """Run standard demo"""
    return run_command(
        ["python", "test_demo.py", "--iterations", "50", "--speed", "0.3"],
        "Demo Bot - Standard"
    )


def demo_bot_full():
    """Run full demo"""
    return run_command(
        ["python", "test_demo.py", "--iterations", "100", "--speed", "0.5"],
        "Demo Bot - Complet"
    )


def unit_tests():
    """Run unit tests"""
    return run_command(
        ["pytest", "tests/", "-v", "--color=yes"],
        "Tests Unitaires"
    )


def full_test_suite():
    """Run full test suite"""
    return run_command(
        ["bash", "scripts/run_tests.sh"],
        "Suite de Tests Complète"
    )


def run_bot_simulation():
    """Run bot in simulation mode"""
    print(f"\n{'='*70}")
    print("🚀 Lancement du Bot en Mode Simulation")
    print(f"{'='*70}\n")
    print("⚠️  Assurez-vous d'avoir configuré vos clés API dans .env")
    print("    Appuyez sur Ctrl+C pour arrêter le bot\n")
    print("💡 Pour voir le dashboard:")
    print("    → Ouvrez un AUTRE terminal")
    print("    → Lancez: python run_dashboard.py")
    print("    → Ou utilisez l'option 8 du menu\n")
    
    input("Appuyez sur Entrée pour continuer...")
    
    return run_command(
        ["python", "main.py", "--interactive"],
        "Bot en Mode Simulation"
    )


def launch_bot_and_dashboard():
    """Launch bot and dashboard in separate terminals"""
    print(f"\n{'='*70}")
    print("🚀 Lancement Bot + Dashboard")
    print(f"{'='*70}\n")
    print("Cette option lance:")
    print("  1. Le bot dans CE terminal")
    print("  2. Le dashboard dans un NOUVEAU terminal")
    print("")
    print("⚠️  Assurez-vous d'avoir configuré vos clés API dans .env")
    print("")
    
    input("Appuyez sur Entrée pour continuer...")
    
    return run_command(
        ["bash", "launch_all.sh"],
        "Bot + Dashboard"
    )


def open_dashboard():
    """Open dashboard"""
    print(f"\n{'='*70}")
    print("🌐 Dashboard")
    print(f"{'='*70}\n")
    print("⚠️  IMPORTANT: Le bot doit être lancé AVANT le dashboard!")
    print("")
    print("Si le bot n'est pas lancé:")
    print("  1. Ouvrez un autre terminal")
    print("  2. Lancez: python main.py --interactive")
    print("  3. Revenez ici et relancez le dashboard")
    print("")
    print("Le dashboard sera accessible à:")
    print("  👉 http://localhost:5000")
    print("")
    
    input("Appuyez sur Entrée pour lancer le dashboard...")
    
    return run_command(
        ["python", "run_dashboard.py"],
        "Dashboard"
    )


def main():
    """Main interactive menu"""
    while True:
        print_header()
        print_menu()
        
        try:
            choice = input("Votre choix (0-9): ").strip()
            
            if choice == "0":
                print("\n👋 Au revoir!")
                sys.exit(0)
            
            elif choice == "1":
                test_indicators()
            
            elif choice == "2":
                demo_bot_quick()
            
            elif choice == "3":
                demo_bot_standard()
            
            elif choice == "4":
                demo_bot_full()
            
            elif choice == "5":
                unit_tests()
            
            elif choice == "6":
                full_test_suite()
            
            elif choice == "7":
                run_bot_simulation()
            
            elif choice == "8":
                launch_bot_and_dashboard()
            
            elif choice == "9":
                open_dashboard()
            
            else:
                print("\n❌ Choix invalide. Veuillez choisir entre 0 et 9.")
            
            input("\nAppuyez sur Entrée pour revenir au menu...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            sys.exit(0)
        except EOFError:
            print("\n\n👋 Au revoir!")
            sys.exit(0)


if __name__ == "__main__":
    main()

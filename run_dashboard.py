#!/usr/bin/env python3
"""
Launch the dashboard separately from the bot
"""
import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

print("\n" + "="*70)
print("📊 RSI Trading Bot - Dashboard Server")
print("="*70)
print("\n⚠️  Assurez-vous que le bot est déjà lancé dans un autre terminal!")
print("   → python main.py --interactive\n")

try:
    from dashboard.backend.api import app, socketio
    from config.settings import AppConfig
    
    config = AppConfig()
    config.initialize()
    
    port = config.dashboard.BACKEND_PORT
    host = config.dashboard.BACKEND_HOST
    
    print(f"🌐 Dashboard accessible sur: http://{host}:{port}")
    print(f"📂 Interface web: dashboard/frontend/index.html")
    print("\n💡 Appuyez sur Ctrl+C pour arrêter le dashboard")
    print("="*70 + "\n")
    
    # Run dashboard
    socketio.run(
        app,
        host=host,
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
    
except KeyboardInterrupt:
    print("\n\n👋 Dashboard arrêté")
except ImportError as e:
    print(f"\n❌ Erreur d'import: {e}")
    print("\n💡 Installez les dépendances:")
    print("   pip install flask flask-cors flask-socketio")
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

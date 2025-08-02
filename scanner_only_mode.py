"""
Scanner-Only Mode - Failover for Critical Operations
Run this if the AI module causes issues but scanning must continue
"""
import json
import sys

# Temporarily disable AI in config
def disable_ai_mode():
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Store original AI state
    original_ai_state = config.get('ai', {}).get('enabled', True)
    
    # Disable AI
    if 'ai' in config:
        config['ai']['enabled'] = False
    else:
        config['ai'] = {'enabled': False}
    
    # Save updated config
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    return original_ai_state

def restore_ai_mode(original_state):
    """Restore AI configuration"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    config['ai']['enabled'] = original_state
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

if __name__ == "__main__":
    print("="*60)
    print("SCANNER-ONLY MODE (FAILOVER)")
    print("="*60)
    print("This mode disables AI features for critical scanning operations")
    print("Use this if AI module causes issues but scanning must continue")
    print("="*60)
    
    # Check if we should use the simple version instead
    response = input("\nUse simple webhook (recommended for stability)? (y/n): ")
    
    if response.lower() == 'y':
        # Use the simple, proven webhook
        print("\nStarting simple webhook service...")
        import subprocess
        subprocess.run([sys.executable, "webhook_simple_print.py"])
    else:
        # Disable AI and run main app
        original_ai = disable_ai_mode()
        print("\nAI module disabled. Starting scanner-only mode...")
        
        try:
            import main_app
            main_app.main()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            # Restore original AI state
            restore_ai_mode(original_ai)
            print("AI configuration restored.") 
"""
Greenfield Metal Sales - Integrated Scanner & AI System
Main application entry point
"""
import threading
import time
import signal
import sys
from flask import Flask, jsonify

from modules.shared.config_manager import get_config
from modules.shared.event_bus import get_event_bus, EventTypes
from modules.scanner.webhook_service import WebhookService
from modules.ai.inventory_analyzer import InventoryAnalyzer

class IntegratedSystem:
    """Main system that runs both scanner and AI modules"""
    
    def __init__(self):
        self.config = get_config()
        self.event_bus = get_event_bus()
        self.running = False
        
        # Ensure all directories exist
        self.config.ensure_directories()
        
        # Initialize modules
        print("Initializing Scanner Module...")
        self.scanner_service = WebhookService()
        
        print("Initializing AI Module...")
        self.ai_analyzer = InventoryAnalyzer()
        
        # Setup system monitoring
        self._setup_monitoring()
        
        # Handle shutdown gracefully
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_monitoring(self):
        """Setup system monitoring endpoints"""
        # Add monitoring routes to scanner service
        app = self.scanner_service.app
        
        @app.route('/system/status')
        def system_status():
            """Overall system status"""
            return jsonify({
                "status": "operational",
                "modules": {
                    "scanner": "active",
                    "ai": "active" if self.config.ai['enabled'] else "disabled"
                },
                "ai_report": self.ai_analyzer.get_inventory_report() if self.config.ai['enabled'] else None
            })
        
        @app.route('/system/ai/report')
        def ai_report():
            """Get AI inventory report"""
            if not self.config.ai['enabled']:
                return jsonify({"error": "AI module disabled"}), 503
            
            return jsonify(self.ai_analyzer.get_inventory_report())
        
        @app.route('/system/events')
        def recent_events():
            """Get recent system events (would need event history implementation)"""
            return jsonify({
                "message": "Event history not yet implemented",
                "tip": "Check logs for event details"
            })
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutdown signal received...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the integrated system"""
        print("="*60)
        print("GREENFIELD METAL SALES - INTEGRATED SYSTEM")
        print("="*60)
        print(f"Scanner Module: ENABLED")
        print(f"AI Module: {'ENABLED' if self.config.ai['enabled'] else 'DISABLED'}")
        print(f"Webhook Port: {self.config.webhook['port']}")
        print("="*60)
        print("\nSystem Endpoints:")
        print(f"  Webhook: http://localhost:{self.config.webhook['port']}/paradigm-webhook")
        print(f"  Health: http://localhost:{self.config.webhook['port']}/health")
        print(f"  System Status: http://localhost:{self.config.webhook['port']}/system/status")
        print(f"  AI Report: http://localhost:{self.config.webhook['port']}/system/ai/report")
        print(f"  Test Print: http://localhost:{self.config.webhook['port']}/test-print")
        print("="*60)
        
        self.running = True
        
        # Publish system startup event
        self.event_bus.publish_event(
            EventTypes.SYSTEM_STARTUP,
            {"ai_enabled": self.config.ai['enabled']},
            "main_app"
        )
        
        # Start the webhook service (this blocks)
        self.scanner_service.run(debug=False)
    
    def stop(self):
        """Stop the integrated system"""
        if self.running:
            print("Stopping integrated system...")
            
            # Publish shutdown event
            self.event_bus.publish_event(
                EventTypes.SYSTEM_SHUTDOWN,
                {},
                "main_app"
            )
            
            # Stop event bus
            self.event_bus.stop()
            
            self.running = False
            print("System stopped.")

def main():
    """Main entry point"""
    system = IntegratedSystem()
    
    try:
        system.start()
    except Exception as e:
        print(f"Error: {e}")
        system.stop()

if __name__ == "__main__":
    main() 
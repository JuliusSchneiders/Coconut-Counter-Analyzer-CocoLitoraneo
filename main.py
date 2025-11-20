"""
Application Entry Point.
Orchestrates the initialization and execution of the Coconut Analysis System.
"""
import sys
from src.system import MegaCoconutSystem

def main() -> None:
    """
    Bootstraps the application components and starts the main processing loop.
    """
    try:
        ## === [ SYSTEM INITIALIZATION ] ===
        # Instantiates the main controller which loads models and configs
        Counter = MegaCoconutSystem()
        
        ## === [ EXECUTION ] ===
        # Starts the video processing loop
        Counter.run()

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully in the terminal
        print("\n[INFO] Processo interrompido pelo usuário (Ctrl+C).")
        sys.exit(0)
        
    except Exception as e:
        # Catch-all for unexpected crashes to log the error
        print(f"\n[ERRO CRÍTICO] Ocorreu uma exceção inesperada: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
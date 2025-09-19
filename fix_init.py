import asyncio, sys

# Force Windows to use compatible event loop
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import AFTER setting event loop
from skyvern.cli.commands import cli_app

if __name__ == "__main__":
    cli_app()

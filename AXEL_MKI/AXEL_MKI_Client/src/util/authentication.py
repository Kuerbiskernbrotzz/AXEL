import asyncio
import threading
from util.config import SERVER_ADDRESS, PORT, PASSWORD
from .logger import log

log.info("Authentication initialized.")
def authenticate_with_server():
    """Authenticates with the server."""
    def run_auth():
        async def send_auth():
            print()
            reader, writer = await asyncio.open_connection(SERVER_ADDRESS, PORT)
            writer.write(f"AUTH {PASSWORD}\n".encode())
            await writer.drain()
            response = await reader.readline()
            writer.close()
            await writer.wait_closed()
            return response.decode().strip()
        result = asyncio.run(send_auth())
        # Hier wird das Emoji durch Text ersetzt
        log.info(f"Authentication answer: [SUCCESS] {result.replace('✅', '')}")
    threading.Thread(target=run_auth, daemon=True).start()
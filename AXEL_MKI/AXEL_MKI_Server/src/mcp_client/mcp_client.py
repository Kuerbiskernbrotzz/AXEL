import asyncio
import os
import sys
import json
from contextlib import AsyncExitStack
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import socket

# MCP Client Imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_google_genai import ChatGoogleGenerativeAI

# Agent and LLM Imports
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from logger.logger import log


log.info("MCP-client initialized.")

def check_internet() -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def load_config():
    # Von src/mcp_client auf AXEL_X_MKIV wechseln -> drei Ebenen nach oben:
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Error loading the config: {e}")
        raise

config = load_config()
env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(env_path)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

LLMO = ChatOllama(model=config["LLM"], temperature=0)

if GEMINI_API_KEY:
    try:
        LLMG = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)
    except Exception as e:
        log.error(e)
        LLMG = None



# ---------------------------
# Custom JSON Encoder
# ---------------------------
class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "content"):
            type_mapping = {
                "AIMessage": "assistant",
                "HumanMessage": "user",
                "ToolMessage": "tool"
            }
            message_type = type_mapping.get(o.__class__.__name__, o.__class__.__name__)
            return {"type": message_type, "content": o.content}


# ---------------------------
# Function: extract_latest_ai_message
# ---------------------------
def extract_latest_ai_message(response: str) -> Optional[str]:
    try:
        response_data = json.loads(response)
        for message in reversed(response_data.get("messages", [])):
            if message.get("type") == "assistant":
                return message.get("content")
    except Exception as e:
        log.error(f"Error extracting assistant message: {e}")
    return None


# ---------------------------
# Class: MCPClientManager
# ---------------------------
class MCPClientManager:
    def __init__(self, config_path: str = "mcp_config.json"):
        self.config_path = config_path
        self.tools: List[Any] = []
        self.llmo = LLMO
        self.llmg = LLMG
        self.exit_stack = AsyncExitStack()

    async def initialize(self):
        """Initialize the MCP client by loading servers and tools."""
        if not os.path.exists(self.config_path):
            log.error(f"Configuration file '{self.config_path}' not found.")
            log.info("Starting with LLM only.")
            config = {}
        else:
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
                    log.info(f"Successfully loaded configuration from {self.config_path}")
            except Exception as e:
                log.error(f"Error reading configuration file: {e}")
                sys.exit(1)

        mcp_servers = config.get("mcpServers", {})
        for server_name, server_info in mcp_servers.items():
            try:
                server_params = StdioServerParameters(
                    command=server_info["command"],
                    args=server_info["args"],
                    env=None
                )
                read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                server_tools = await load_mcp_tools(session)
                self.tools.extend(server_tools)
                log.info(f"\n🛠️ {len(server_tools)} tools loaded from {server_name}.\n")
            except asyncio.TimeoutError:
                log.error(f"\n❌ Connection to {server_name} timed out.\n")
            except Exception as e:
                log.error(f"\n❌ Error connecting to {server_name}: {e}\n")

        

    async def process_query(self, query: dict) -> dict:
        """Process a query using the initialized agent."""
        ic = check_internet()
        if self.llmg and self.llmg != None and ic == True:
            try:
                log.info("Using Gemini as LLM")
                google_agent = create_react_agent(self.llmg, self.tools) if self.tools else create_react_agent(self.llmg, [])
                response = await google_agent.ainvoke(query)
                formatted_raw = json.dumps(response, indent=2, cls=CustomEncoder)
                latest_ai_message = extract_latest_ai_message(formatted_raw)
                return {"raw": formatted_raw, "latest_ai_message": latest_ai_message}
            except Exception as e:
                log.error(f"Gemini LLM Fehler: {e}")
        else:
            try:
                log.info("Using Ollama as LLM")
                ollama_agent = create_react_agent(self.llmo, self.tools) if self.tools else create_react_agent(self.llmo, [])
                response = await ollama_agent.ainvoke(query)
                formatted_raw = json.dumps(response, indent=2, cls=CustomEncoder)
                latest_ai_message = extract_latest_ai_message(formatted_raw)
                return {"raw": formatted_raw, "latest_ai_message": latest_ai_message}
            except Exception as e:
                log.error(f"Ollama Fehler: {e}")
                return {"raw": "{}", "latest_ai_message": None}

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()


# ---------------------------
# Function: interactive_mode (for testing)
# ---------------------------
async def interactive_mode(client_manager: MCPClientManager):
    print("\n🚀 Ready! Type 'quit' to exit.")
    while True:
        user_input = input("\nQuery: ").strip()
        if user_input.lower() == "quit":
            break

        query = {"messages": [{"role": "user", "content": user_input}]}
        try:
            formatted = await client_manager.process_query(query)
            print("\n====== Raw Response ======")
            print(formatted["raw"])
            print("\n====== Latest assistant message ======")
            print(formatted["latest_ai_message"])
        except Exception as e:
            log.error(f"\nError processing query: {e}\n")


# ---------------------------
# Main Entry Point
# ---------------------------
async def main():
    client_manager = MCPClientManager()
    try:
        await client_manager.initialize()
        await interactive_mode(client_manager)
    finally:
        await client_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())



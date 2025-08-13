import asyncio
import logging
import tempfile
import shutil
import json
from pathlib import Path

import os


from mcp_client.mcp_client import MCPClientManager
from tts.TextToSpeech import text_to_speech
from stt.SpeechToText import transcribe_audio
from logger.logger import log
from resource import resource_path

def load_config():
    config_path = Path(__file__).parent / "config" / "config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        log.error(f"Error loading the config: {e}")
        raise
config = load_config()


PASSWORD = config["PASSWORD"]
MCW =  config["MESSAGE_CONTEXT_WINDOW"]
PORT = config["SERVER_PORT"]
clients = {}
messages = []
system_prompt = {"role": "system", "content": config["SYSTEM_MESSAGE"]}

client_manager = MCPClientManager(config_path="mcp_config/mcp_config.json")

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    global messages   # <-- globale Variable "messages" deklarieren
    peername = writer.get_extra_info("peername")
    log.info(f"New connection: {peername}")
    clients[peername] = False
    
    # Erstelle ein client-spezifisches temporäres Verzeichnis
    temp_dir = tempfile.mkdtemp(prefix=f"client_{peername[1]}_")
    log.info(f"Temporary file path created: {peername}: {temp_dir}")

    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            message = data.decode().strip()
            if not message:
                continue

            if " " not in message:
                writer.write("Wrong format:\n".encode())
                await writer.drain()
                continue
            typ, payload = message.split(" ", 1)
            typ = typ.upper()

            if typ == "AUTH":
                if payload == PASSWORD:
                    clients[peername] = True
                    await client_manager.initialize()
                    writer.write("✅ Authenticated\n".encode())
                else:
                    writer.write("❌ Wrong password\n".encode())
            elif typ == "TEXT":
                if not clients.get(peername, False):
                    writer.write("❌ Please authenticate first (AUTH)\n".encode())
                else:
                    messages.append({"role": "user", "content": payload})
                    query = {"messages": [system_prompt] + messages[-MCW:]}
                    response = await client_manager.process_query(query)
                    messages.append({"role": "assistant", "content": response["latest_ai_message"]})
                    antwort = response["latest_ai_message"] + "\n<END>\n"
                    writer.write(antwort.encode())
            elif typ == "AUDIO":
                if not clients.get(peername, False):
                    writer.write("❌ Please authenticate first (AUTH)\n".encode())
                else:
                    # Bestimme den Pfad der zu speichernden Audiodatei
                    audio_file_path = os.path.join(temp_dir, "recieved_audio.wav")
                    writer.write("ACK AUDIO recieve\n".encode())
                    await writer.drain()

                    # Empfange Audio in chunks bis "<END>" gefunden wird
                    audio_bytes = b""
                    while True:
                        chunk = await reader.read(1024)
                        if b"<END>" in chunk:
                            index = chunk.find(b"<END>")
                            audio_bytes += chunk[:index]
                            break
                        audio_bytes += chunk
                    with open(audio_file_path, "wb") as f:
                        f.write(audio_bytes)
                    log.info(f"Audio file recieved and saved: {audio_file_path}")

                    # Transkribiere die Audiodatei
                    transcript = transcribe_audio(audio_file_path)
                    log.info(f"Transcribed Text: {transcript}")

                    # Sende zuerst die transkribierte Benutzeranfrage separat
                    transcript_send = transcript + "\n<TRANSCRIPT_END>\n"
                    writer.write(transcript_send.encode())
                    await writer.drain()

                    # Verarbeite den transkribierten Text als Anfrage
                    messages.append({"role": "user", "content": transcript})
                    query = {"messages": [system_prompt] + messages[-MCW:]}
                    response = await client_manager.process_query(query)
                    messages.append({"role": "assistant", "content": response["latest_ai_message"]})

                    # Sende nun die AI-Antwort separat
                    ai_answer_send = response["latest_ai_message"] + "\n<AI_END>\n"
                    writer.write(ai_answer_send.encode())
                    await writer.drain()

                    # Konvertiere den Antworttext in Sprache und speichere diese als "response_audio.wav"
                    response_audio_path = os.path.join(temp_dir, "response_audio.wav")
                    await text_to_speech(response["latest_ai_message"], response_audio_path)
                    log.info(f"Audio answer generated: {response_audio_path}")

                    # Sende die generierte Audio-Datei an den Client
                    with open(response_audio_path, "rb") as f:
                        audio_response = f.read()
                        writer.write(audio_response)
                        writer.write(b"<END>")
                        await writer.drain()

                    # Leere den Inhalt des temporären Verzeichnisses
                    for filename in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, filename)
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            log.error(f"Error deleting the file {file_path}: {e}")
            elif typ == "COMMAND":
                if not clients.get(peername, False):
                    writer.write("❌ Please authenticate first (AUTH)\n".encode())
                else:
                    if payload == "/clear_context":
                        messages.clear()  # Leert die globale messages Liste
                        writer.write("✅ Context deleted\n".encode())
                        log.info(f"Context for client {peername} got deleted")
                    else:
                        antwort = "❌ Unknown COMMAND"
                        writer.write(antwort.encode())
            else:
                writer.write("❌ Unknown message type\n".encode())

            await writer.drain()

    except Exception as e:
        log.error(f"Error at {peername}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        await client_manager.cleanup()
        clients.pop(peername, None)
        # Lösche das client-spezifische temporäre Verzeichnis
        shutil.rmtree(temp_dir, ignore_errors=True)
        log.info(f"Temporary path {temp_dir} for {peername} deleted.")

async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", PORT)
    addr = server.sockets[0].getsockname()
    log.info(f"Server started on {addr}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
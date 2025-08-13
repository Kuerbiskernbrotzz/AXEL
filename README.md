# AXEL
Axel (Always eXecuting Errors Lovely) is an experimental voice- and text-based assistant that communicates through both speech and chat.  
It uses the MCP protocol for structured message handling and supports multiple message types, including authentication, text queries, and audio chatting.
Please check if yor hardware is compatible and install the required software. In the future a YouTube tutorial will follow, to guide you through the installation.
---
### YouTube tutorial:
  -comming soon

## 📥 Download Links
**Client (Windows 💻)**  
[Download](https://filecente.com/bLagvvhyd1bTwo7/file)

**Client (Linux 🐧)**  
[Download]() (comming soon)

**Server (Windows 🔗)**  
[Download](https://filecente.com/Sz3oyxiKINf1kuV/file)

**Server (Linux 🔗)**  
[Download]() (comming soon)

---
Natürlich, Johann! Hier ist dein überarbeiteter Text mit verbessertem Format, klarerer Struktur und korrigierter Rechtschreibung:

Absolutely! Here's the improved and polished English version of your instructions:

---

## Setup

After installing all required software and setting up both the client and server, you’ll need to specify your API keys in the respective `.env` files.

### 🔑 Location of `.env` Files

**Windows:**
```plaintext
C:\Program Files\AXEL-Server-MK.I\_internal\.env
C:\Program Files\AXEL-Client-MK.I\_internal\.env
```

**Linux:**
```plaintext
~/path/to/dir
```



### 🎤 Client: Picovoice API Key

The client requires a Picovoice API key. You can get one here:  
👉 [Picovoice Console](https://console.picovoice.ai)

🔧 Add the key to the `.env` file located in the client directory.



### 🤖 Server: Gemini API Key (Optional)

If you prefer something faster than Ollama, you can use a Gemini API key.  
👉 [Gemini API Console](https://aistudio.google.com/apikey)

🔧 Add the key to the `.env` file located in the server directory.

---

## Usage 🚀

### Start the programms. First the Server, wait a couple of seconds and start the client.
**Features**
  - You can Use the Voice featur by Saying "hi, Axel".
  - The Chat you can mute the mic / speaker.
  - You can chat just by writing something and sending it.
  - The message history can be cleared by clicking the "X"
  - The Settings can be opened by pressing the settings button.
  - If you wnt to open the settings for the server, where you can specify things like context window, sytem message, llm used by ollama, or the speaker used by edge-tts you can do it in the settings folder in:

```plaintext
C:\Program Files\AXEL-Server-MK.I\_internal\config\config.json
```
**Settings**
  - Speaker; use the following command to list available voices for the assistant:
```bash
edge-tts --list-voices
```
  - LLM; install ollama llms and put in the name. You can get models from [ollama](https://ollama.com/search)
    - install them with:
    
```bash
ollama pull your_model_name 
```

   - list installed models with:
    
```bash
ollama list
```

  - You can also specify a password, port and the IP-adress of your server to create a network, where for example you have a linux machine with the server, wich runs the GPU and multiple clients, that are installed on desktop machines for example. (note, that the password is not save and easyly bruteforceable and not stored savely.

  - You can install mcp servers and specify them in the mcp_config.json ([documentation](https://modelcontextprotocol.io/docs/getting-started/intro)):

```plaintext
C:\Program Files\AXEL_server_MK.I\_internal\mcp_config\mcp_config.json
```

  - Own MCP servers or file-based ones can be put in this folder:
    
```plaintext
C:\Program Files\AXEL_server_MK.I\_internal\mcp_client\servers\
```

---

## 🖥️ System Requirements

### Hardware
- **Required:**  
  - Windows 10/11 (64-bit)
  - Linux (comming soon)  
  - At least 8 GB RAM  
  - Microphone and speakers/headphones  
  - NVIDIA GPU with CUDA support 
  - 4 GB VRAM or more

### Software
- **Required:**  
  - Latest NVIDIA GPU drivers 
  - CUDA Toolkit 13.0 [Installation Guide](https://github.com/Kuerbiskernbrotzz/AXEL/blob/main/Tutorials/Cuda-Installation.md)
  - Ollama Installed:
    - Windows:
    
      1: [Download](https://ollama.com/download/OllamaSetup.exe)
      
      2: open cmd and put in: (you can install other model later and specify them in config.json in the programm dir)
      
      ```bash
      ollama pull qwen2.5:3b
      ```
      
    - Linux:
      
      1: Open Terminal and insert:
      
      ```bash
      curl -fsSL https://ollama.com/install.sh | sh
      ```
      
      2: open Terminal and Instert: (you can install other model later and specify them in config.json in the programm dir)
      
      ```bash
      ollama pull qwen2.5:3b
      ```

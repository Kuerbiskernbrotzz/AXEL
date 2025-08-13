# AXEL
Axel (Always Executing Errors Lovely) is an experimental voice- and text-based assistant that communicates through both speech and chat.  
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

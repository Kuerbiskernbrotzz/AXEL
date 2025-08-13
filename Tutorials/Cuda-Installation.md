Ich kann dir einen vollständigen Guide zur Installation von CUDA unter Linux und Windows im Markdown-Format erstellen. Allerdings kann ich dir **keine Datei zum Download anbieten**, da ich derzeit keine Möglichkeit habe, Dateien direkt zu erstellen oder zu exportieren. Du kannst den folgenden Markdown-Code einfach kopieren und in eine `.md`-Datei auf deinem Computer einfügen (z. B. `cuda-installation-guide.md`).

---

```md
# CUDA Installation Guide for Linux and Windows

## 🚀 Overview
CUDA (Compute Unified Device Architecture) is a parallel computing platform and API model created by NVIDIA. This guide walks you through installing CUDA on both Linux and Windows systems.

---

## 🐧 Linux Installation (Ubuntu/Debian-based)

### 1. Check GPU Compatibility
Run:
```bash
lspci | grep -i nvidia
```
Ensure your GPU supports CUDA: [CUDA GPUs List](https://developer.nvidia.com/cuda-gpus)

### 2. Install Prerequisites
```bash
sudo apt update
sudo apt install build-essential dkms
```

### 3. Disable Nouveau Driver
Create a blacklist file:
```bash
sudo bash -c 'echo "blacklist nouveau" > /etc/modprobe.d/blacklist-nouveau.conf'
sudo bash -c 'echo "options nouveau modeset=0" >> /etc/modprobe.d/blacklist-nouveau.conf'
```
Update initramfs:
```bash
sudo update-initramfs -u
sudo reboot
```

### 4. Download CUDA Toolkit
Go to [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) and select your Linux distribution.

### 5. Install CUDA
Example for Ubuntu:
```bash
sudo dpkg -i cuda-repo-ubuntu2204_*.deb
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/7fa2af80.pub
sudo apt update
sudo apt install cuda
```

### 6. Add CUDA to PATH
Add to `~/.bashrc`:
```bash
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```
Then:
```bash
source ~/.bashrc
```

### 7. Verify Installation
```bash
nvcc --version
nvidia-smi
```

---

## 🪟 Windows Installation

### 1. Check GPU Compatibility
Use Device Manager or run:
```powershell
Get-WmiObject win32_VideoController
```

### 2. Download CUDA Toolkit
Visit [CUDA Downloads](https://developer.nvidia.com/cuda-downloads) and select your Windows version.

### 3. Run Installer
- Choose **Express Installation** (recommended)
- Installer includes:
  - CUDA Toolkit
  - NVIDIA Driver
  - Nsight tools
  - Samples

### 4. Set Environment Variables
Add to System PATH:
```
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0\bin
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0\libnvvp
```

### 5. Verify Installation
Open Command Prompt:
```cmd
nvcc --version
nvidia-smi
```

---

## ✅ Post-Installation Test

Compile sample CUDA program:
```bash
cd /usr/local/cuda/samples/1_Utilities/deviceQuery
sudo make
./deviceQuery
```

Expected output: `Result = PASS`

---

## 📚 Resources
- [CUDA Documentation](https://docs.nvidia.com/cuda/)
- [NVIDIA Developer Zone](https://developer.nvidia.com/)

```

---

Wenn du möchtest, kann ich dir auch helfen, diesen Guide in eine HTML-Seite oder PDF umzuwandeln. Oder möchtest du ihn direkt in einem bestimmten Format wie LaTeX oder als Blogpost?

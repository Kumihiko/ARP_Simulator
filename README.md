# 🛰️ ARP Simulator with Spoofing GUI

This project is a simple ARP (Address Resolution Protocol) simulation written in Python, including support for ARP spoofing. It features a Tkinter-based graphical interface that allows you to select a target host, send ARP requests, and enable/disable spoofing.
✅ Requires Python 3.6+ (tested on Python 3.9)
## 🔧 Features

- Simulates ARP request/response between virtual hosts
- Supports timeout for unanswered ARP requests (Timeout is set to h2 / 192.168.1.20)
- ARP table with automatic aging and cleanup
- Optional ARP spoofing functionality (Spoofer is set to h3 / 192.168.1.30)
- GUI built with Tkinter:
  - Target host selection
  - Send ARP request button
  - Enable/disable spoofing toggle
  - Clear console button
  - Output console (redirected `print()`)

## ⚙️ How It Works
The main sender host is hardcoded as h1 (192.168.1.10)

The GUI allows you to choose a target IP to send an ARP request

If spoofing is enabled (via h3), fake ARP replies are sent to poison ARP tables

If a host is offline (e.g., 192.168.1.20), the system will show a timeout error

## 🖥️ Preview


![image](https://github.com/user-attachments/assets/e882fbcd-d74e-495e-a8a2-039ddd46b806)



## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ARP_Simulator.git
   cd ARP_Simulator
   python arp_gui.py

Made by Kumihiko

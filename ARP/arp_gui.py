import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from io import StringIO
import sys

class Host:    
    def __init__(self, ip, mac):
        self.ip = ip
        self.mac = mac
        self.arp_table = {}
        self.pending_arp_requests = {}
        self.enable_spoofing = False
        self.spoof_target_ip = None  
        self.spoof_victim_ip = None  

    def send_arp_request(self, target_ip, network, timeout=5):
        print(f"[{self.ip}] Sending ARP request: who has {target_ip}???")
        network.broadcast_arp_request(self, target_ip)

        self.pending_arp_requests[target_ip] = time.time()

        start_time = time.time()
        while time.time() - start_time < timeout:
            if target_ip in self.arp_table:
                break
            time.sleep(0.1) 

        if target_ip not in self.arp_table:
            print(f"[{self.ip}] ERROR: No ARP reply from {target_ip} after {timeout} seconds!")

    def receive_arp_request(self, sender_ip, sender_mac, target_ip, network):
        if self.ip == target_ip:
            print(f"[{self.ip}] Recieved ARP request, sending answer back to {sender_ip}")
            network.send_arp_reply(self, sender_ip, sender_mac)

    def receive_arp_reply(self, sender_ip, sender_mac):
        print(f"[{self.ip}] Recieved ARP reply: {sender_ip} on MAC {sender_mac}")
        self.arp_table[sender_ip] = (sender_mac, time.time())
        if sender_ip in self.pending_arp_requests:
            del self.pending_arp_requests[sender_ip]

    def try_spoofing(self, target_ip, victim_ip, network):
        if not self.enable_spoofing:
            print(f"[{self.ip}] Spoofing is disabled.")
            return

        print(f"[{self.ip}] SPOOFING: Attempting to send fake ARP to {victim_ip} - {target_ip} is at {self.mac}")

        for host in network.hosts:
            if host.ip == victim_ip:
                host.receive_arp_reply(target_ip, self.mac)

        network.send_arp_reply(self, target_ip, self.mac)

        self.arp_table[target_ip] = (self.mac, time.time())

    def check_pending_requests(self, timeout=5):
        now = time.time()
        timed_out = []
        for target_ip, timestamp in list(self.pending_arp_requests.items()):
            if now - timestamp > timeout:
                print(f"[{self.ip}] ERROR: No ARP reply from {target_ip} after {timeout} seconds!")
                timed_out.append(target_ip)
        for ip in timed_out:
            del self.pending_arp_requests[ip]

    def clean_arp_table(self, timeout=10):
        now = time.time()
        self.arp_table = {
            ip: (mac, timestamp)
            for ip, (mac, timestamp) in self.arp_table.items()
            if now - timestamp < timeout
        }

    def show_arp_table(self):
        self.clean_arp_table()
        print(f"ARP host table {self.ip}:")
        for ip, (mac, timestamp) in self.arp_table.items():
            print(f"  {ip} => {mac} (added {int(time.time() - timestamp)} sec. ago)")

class Network:
    def __init__(self):
        self.hosts = []

    def add_host(self, host):
        self.hosts.append(host)
        # print(f"[DEBUG] Host {host.ip} added to network")

    def broadcast_arp_request(self, sender_host, target_ip):
        for host in self.hosts:
            if host != sender_host:
                host.receive_arp_request(sender_host.ip, sender_host.mac, target_ip, self)

    def send_arp_reply(self, replying_host, target_ip, target_mac):
        for host in self.hosts:
            if host.ip == target_ip:
                host.receive_arp_reply(replying_host.ip, replying_host.mac)
                break

    def trigger_spoofing_if_enabled(self, target_ip, victim_ip):
        for host in self.hosts:
            if host.enable_spoofing:
                host.try_spoofing(target_ip, victim_ip, self)

class RedirectedOutput:
    def __init__(self, console_widget):
        self.console = console_widget

    def write(self, message):
        self.console.configure(state='normal')
        self.console.insert(tk.END, message)
        self.console.see(tk.END)
        self.console.configure(state='disabled')

    def flush(self):
        pass

class ARPSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ARP Simulation GUI")

        # Setup network and hosts
        self.network = Network()
        self.h1 = Host("192.168.1.10", "AA:BB:CC:DD:EE:01")  # Fixed sender
        self.h3 = Host("192.168.1.30", "AA:BB:CC:DD:EE:03")  # Potential spoofer
        self.h4 = Host("192.168.1.40", "AA:BB:CC:DD:EE:04")
        self.h5 = Host("192.168.1.50", "AA:BB:CC:DD:EE:05")
        self.h6 = Host("192.168.1.60", "AA:BB:CC:DD:EE:06")

        self.network.add_host(self.h1)
        self.network.add_host(self.h3)
        self.network.add_host(self.h4)
        self.network.add_host(self.h5)
        self.network.add_host(self.h6)

        # h2 is simulated as offline
        self.victim_ip = self.h1.ip

        self.available_hosts = {
            "192.168.1.30": self.h3,
            "192.168.1.40": self.h4,
            "192.168.1.50": self.h5,
            "192.168.1.60": self.h6,
            "192.168.1.20 (Offline)": "offline"
        }

        self.create_widgets()

        # Redirect stdout
        sys.stdout = RedirectedOutput(self.console)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(main_frame, text="Select target host IP:").grid(row=0, column=0, sticky="w")
        self.target_ip_var = tk.StringVar(value="192.168.1.30")
        ip_dropdown = ttk.Combobox(main_frame, textvariable=self.target_ip_var, state="readonly", width=25)
        ip_dropdown["values"] = list(self.available_hosts.keys())
        ip_dropdown.grid(row=0, column=1, padx=10, pady=5)

        ttk.Button(main_frame, text="Send ARP Request", command=self.send_arp_request).grid(row=1, column=0, pady=5, sticky="ew")
        ttk.Button(main_frame, text="Clear Console", command=self.clear_console).grid(row=1, column=1, pady=5, sticky="ew")

        self.spoof_button = ttk.Button(main_frame, text="Spoofing OFF", command=self.toggle_spoofing)
        self.spoof_button.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        self.console = scrolledtext.ScrolledText(self.root, height=20, state='disabled', wrap=tk.WORD)
        self.console.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def send_arp_request(self):
        target_ip = self.target_ip_var.get().split()[0]  # remove (Offline) label if present

        def arp_logic():
            self.h1.send_arp_request(target_ip, self.network)
            self.network.trigger_spoofing_if_enabled(target_ip, self.victim_ip)
            time.sleep(1)
            self.h1.check_pending_requests()
            self.h1.show_arp_table()

        threading.Thread(target=arp_logic).start()

    def clear_console(self):
        self.console.configure(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.configure(state='disabled')

    def toggle_spoofing(self):
        self.h3.enable_spoofing = not self.h3.enable_spoofing
        state = "ON" if self.h3.enable_spoofing else "OFF"
        self.spoof_button.config(text=f"Spoofing {state}")
        print(f"[{self.h3.ip}] Spoofing {'enabled' if self.h3.enable_spoofing else 'disabled'}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ARPSimulatorGUI(root)
    root.mainloop()

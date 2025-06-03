import tkinter as tk
from tkinter import ttk
from ARP import Host, Network  # zakładam, że masz to w pliku ARP.py
import time
import threading

class ARPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ARP Spoofing Simulator")

        self.net = Network()
        self.hosts = []

        self.setup_network()
        self.create_widgets()

    def setup_network(self):
        # Tworzenie hostów i dodanie do sieci
        self.h1 = Host("192.168.1.10", "AA:BB:CC:DD:EE:01")
        self.h2 = Host("192.168.1.20", "AA:BB:CC:DD:EE:02")
        self.h3 = Host("192.168.1.30", "AA:BB:CC:DD:EE:03")  # spoofer

        self.net.add_host(self.h1)
        self.net.add_host(self.h2)
        self.net.add_host(self.h3)

        self.h3.enable_spoofing = True
        self.hosts = [self.h1, self.h2, self.h3]

    def create_widgets(self):
        frame = ttk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        ttk.Label(frame, text="Wybierz hosta:").grid(row=0, column=0)
        self.host_combo = ttk.Combobox(frame, values=[h.ip for h in self.hosts])
        self.host_combo.grid(row=0, column=1)
        self.host_combo.current(0)

        ttk.Label(frame, text="IP docelowe:").grid(row=1, column=0)
        self.target_entry = ttk.Entry(frame)
        self.target_entry.grid(row=1, column=1)
        self.target_entry.insert(0, "192.168.1.20")

        send_button = ttk.Button(frame, text="Wyślij ARP Request", command=self.send_arp_request)
        send_button.grid(row=2, column=0, columnspan=2, pady=5)

        refresh_button = ttk.Button(frame, text="Odśwież ARP Tabelę", command=self.refresh_arp_table)
        refresh_button.grid(row=3, column=0, columnspan=2)

        self.arp_output = tk.Text(frame, height=10, width=50)
        self.arp_output.grid(row=4, column=0, columnspan=2, pady=5)

    def send_arp_request(self):
        sender_ip = self.host_combo.get()
        target_ip = self.target_entry.get()

        sender = next((h for h in self.hosts if h.ip == sender_ip), None)
        if sender:
            threading.Thread(target=lambda: sender.send_arp_request(target_ip, self.net)).start()

    def refresh_arp_table(self):
        sender_ip = self.host_combo.get()
        sender = next((h for h in self.hosts if h.ip == sender_ip), None)
        if sender:
            sender.clean_arp_table()
            self.arp_output.delete("1.0", tk.END)
            for ip, (mac, timestamp) in sender.arp_table.items():
                age = int(time.time() - timestamp)
                self.arp_output.insert(tk.END, f"{ip} => {mac} (added {age}s ago)\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = ARPGUI(root)
    root.mainloop()

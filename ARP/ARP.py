import time

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


if __name__ == "__main__":
    net = Network()

    h1 = Host("192.168.1.10", "AA:BB:CC:DD:EE:01")
    # h2 = Host("192.168.1.20", "AA:BB:CC:DD:EE:02")
    h3 = Host("192.168.1.30", "AA:BB:CC:DD:EE:03")
    h4 = Host("192.168.1.40", "AA:BB:CC:DD:EE:04")
    h5 = Host("192.168.1.50", "AA:BB:CC:DD:EE:05")
    h6 = Host("192.168.1.60", "AA:BB:CC:DD:EE:06")

    net.add_host(h1)
    # net.add_host(h2)
    net.add_host(h3)
    net.add_host(h4)
    net.add_host(h5)
    net.add_host(h6)
    
    target_ip = "192.168.1.40"# set the target IP to the host you want to send the ARP request to
                              # if set to h2 should return an error / can be combined with spoofing 
    victim_ip = "192.168.1.10"
    

    h3.enable_spoofing = False #set for true or false to enable or disable spoofing

    h1.send_arp_request(target_ip, net) 

    net.trigger_spoofing_if_enabled(target_ip, victim_ip)

    time.sleep(1)

    h1.check_pending_requests()
    h1.show_arp_table()
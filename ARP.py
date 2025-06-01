import time

class Host:
    def __init__(self, ip, mac):
        self.ip = ip
        self.mac = mac
        self.arp_table = {}

    def send_arp_request(self, target_ip, network):
        print(f"[{self.ip}] Sending ARP request: who has {target_ip}???")
        network.broadcast_arp_request(self, target_ip)

    def receive_arp_request(self, sender_ip, sender_mac, target_ip, network):
        if self.ip == target_ip:
            print(f"[{self.ip}] Recieved ARP request, sending answer back to {sender_ip}")
            network.send_arp_reply(self, sender_ip, sender_mac)

    def receive_arp_reply(self, sender_ip, sender_mac):
        print(f"[{self.ip}] Recieved ARP reply: {sender_ip} on MAC {sender_mac}")
        self.arp_table[sender_ip] = (sender_mac, time.time())
        
                      
    def clean_arp_table(self, timeout=10):
        now = time.time()
        self.arp_table = {
        ip: (mac, timestamp)
        for ip, (mac, timestamp) in self.arp_table.items() 
        if now - timestamp < 10}
        

    def show_arp_table(self):
        self.clean_arp_table()
        print(f"ARP host table {self.ip}:")
        for ip, (mac,timestamp) in self.arp_table.items():
            print(f"  {ip} => {mac} (added {int(time.time() - timestamp)} sec. ago)") 
                  



class Network:
    def __init__(self):
        self.hosts = []

    def add_host(self, host):
        self.hosts.append(host)

    def broadcast_arp_request(self, sender_host, target_ip):
        for host in self.hosts:
            if host != sender_host:
                host.receive_arp_request(sender_host.ip, sender_host.mac, target_ip, self)

    def send_arp_reply(self, replying_host, target_ip, target_mac):
        for host in self.hosts:
            if host.ip == target_ip:
                host.receive_arp_reply(replying_host.ip, replying_host.mac)
                break


if __name__ == "__main__":
    net = Network()

    h1 = Host("192.168.1.10", "AA:BB:CC:DD:EE:01")
    h2 = Host("192.168.1.20", "AA:BB:CC:DD:EE:02")
    h3 = Host("192.168.1.30", "AA:BB:CC:DD:EE:03")

    net.add_host(h1)
    net.add_host(h2)
    net.add_host(h3)

    h1.send_arp_request("192.168.1.20", net)
    time.sleep(1)  # Simulate some delay for the ARP
    h1.show_arp_table()

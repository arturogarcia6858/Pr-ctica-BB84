import socket
import json
import random
import time

IP_BOB = '192.168.118.137'
PUERTO_CUANTICO = 5000

NUM_BITS = 100

print(f'Generando bits aleatorios')

bits_de_alice = [random.randint(0, 1) for _ in range(NUM_BITS)]
bases_de_alice =[random.choice(['x', '+']) for _ in range(NUM_BITS)]

fotones_polarizados= []

for i in range(NUM_BITS):
    if bases_de_alice[i] == '+':
        fotones_polarizados.append(0 if bits_de_alice[i] == 0 else 90)
    else:
        fotones_polarizados.append(45 if bits_de_alice[i] == 0 else 135)

print(F'Enviando fotones por puerto {PUERTO_CUANTICO}')
print(f'Fotones enviados: {fotones_polarizados}')

try:
    with socket.socket() as mi_socket:
        mi_socket.connect((IP_BOB, PUERTO_CUANTICO))
        payload = json.dumps(fotones_polarizados)
        mi_socket.sendall(payload.encode('utf-8'))
    print("Transmisión de fotones correcta")
except Exception as e:
    print(f'No se pudo conectar con Bob {e}')

PUERTO_CLASICO = 5001

print("\nConectando al canal para verificación de clave")

time.sleep(5)

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as canal_clasico:
        canal_clasico.connect((IP_BOB, PUERTO_CLASICO))

        payload_bases = json.dumps(bases_de_alice)
        canal_clasico.sendall(payload_bases.encode('utf-8'))
        print("Bases enviadas. Esperando respuesta")
        
        
        datos_indices = canal_clasico.recv(4096)
        indices_correctos = json.loads(datos_indices.decode('utf-8'))
        
        
        clave_secreta_alice = [bits_de_alice[i] for i in indices_correctos]

    print(f"Clave de Alice [{len(clave_secreta_alice)}]:")
    print(clave_secreta_alice)

except Exception as e:
    print(f"Error en el canal: {e}")
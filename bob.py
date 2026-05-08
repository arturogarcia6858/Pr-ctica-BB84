import socket
import json
import random

IP_LOCAL = "0.0.0.0"
PUERTO_CUANTICO = 5000
PUERTO_CLASICO = 5001

def ejecutar_bob():
    fotones_recibidos = []

    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP_LOCAL, PUERTO_CUANTICO))
        s.listen(1)
        print(f"Esperando fototes en el puerto {PUERTO_CUANTICO}")
        
        conn, addr = s.accept()
        with conn:
            print(f"Conexión desde la IP {addr}")

            datos_recibidos = conn.recv(8192).decode('utf-8', errors='ignore').strip()

            try:
                if '[' in datos_recibidos and ']' in datos_recibidos:
                    datos_limpios = datos_recibidos[datos_recibidos.find('['):datos_recibidos.rfind(']')+1]
                    fotones_recibidos = json.loads(datos_limpios)
                    print(f"Fotones decodificados: {len(fotones_recibidos)}")
                else:
                    print(f"Datos con errores")
                    return
            except Exception as e:
                print(f"Error: {e}")
                return

    n = len(fotones_recibidos)

    bases_bob = [random.choice(["+", "x"]) for _ in range(n)]
    bits_medidos = []

    for i in range(n):
        angulo = fotones_recibidos[i]
        base = bases_bob[i]
        if base == "+":
           if angulo == 0:
              bits_medidos.append(0)
           elif angulo == 90:
              bits_medidos.append(1)
           else:
              bits_medidos.append(random.randint(0, 1))
        else:
           if angulo == 45:
              bits_medidos.append(0)
           elif angulo == 135:
              bits_medidos.append(1)
           else:
              bits_medidos.append(random.randint(0, 1))

    print(f"Esperando bases")
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((IP_LOCAL, PUERTO_CLASICO))
        s.listen(1)

        conn, addr = s.accept()
        with conn:
            datos_bases = conn.recv(8192).decode('utf-8', errors='ignore').strip()
            bases_limpias = datos_bases[datos_bases.find('['):datos_bases.rfind(']')+1]
            bases_alice = json.loads(bases_limpias)

            indices_validos = [i for i in range(n) if bases_alice[i] == bases_bob[i]]
            conn.sendall(json.dumps(indices_validos).encode())

    clave = [bits_medidos[i] for i in indices_validos]
    print(f"\nClave de Bob [{len(clave)}]: {clave}")

if __name__ == "__main__":
    ejecutar_bob()
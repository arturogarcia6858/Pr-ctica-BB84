import base64
import numpy as np

from braket.circuits import noises, Circuit, Observable
from braket.devices import LocalSimulator

from utils.golay_code import GolayCode
from utils.secret_utils import convert_to_octets
import os


def inicializar_protocolo(numero_de_qubits):
    base_codificacion = np.random.randint(2, size=numero_de_qubits)
    estados_alice = np.random.randint(2, size=numero_de_qubits)
    base_medicion = np.random.randint(2, size=numero_de_qubits)
    return base_codificacion, estados_alice, base_medicion


def codificar_qubits(estados_alice, base_codificacion):
    circuito = Circuit()
    for indice in range(len(base_codificacion)):
        if estados_alice[indice] == 1:
            circuito.x(indice)
        else:
            circuito.i(indice)
        if base_codificacion[indice] == 1:
            circuito.h(indice)
    return circuito


def medir_qubits(circuito, base_medicion):
    for i in range(len(base_medicion)):
        if base_medicion[i] == 1:
            circuito.h(i)
    return circuito


def filtrar_qubits(bits_medidos, base_alice, base_bob):
    rango_maximo = min(len(base_bob), len(base_alice))
    mantener = np.array([int(bits_medidos[i]) for i in range(rango_maximo) if base_bob[i] == base_alice[i]])
    return mantener


def arreglo_a_cadena(arreglo):
    resultado = np.array2string(
        arreglo,
        separator="",
        max_line_width=(len(arreglo) + 3))
    return resultado.strip('[').strip(']')


def obtener_tamano_circuito(nombre_archivo, buffer_seguridad=16):
    tamano_circuito = os.path.getsize(nombre_archivo) + buffer_seguridad
    cadena_tamano_circuito = str(tamano_circuito).zfill(8)
    return cadena_tamano_circuito


PROBABILIDAD_FLIP_BIT = 0.1
NUMERO_DE_QUBITS = 12
TAMANO_BLOQUE_CORRECCION_ERRORES = 12

clave_cruda_alice = np.array([])
clave_cruda_bob = np.array([])

while len(clave_cruda_alice) < TAMANO_BLOQUE_CORRECCION_ERRORES:
    base_codificacion_A, estados_A, _ = inicializar_protocolo(NUMERO_DE_QUBITS)
    bits_enviados = arreglo_a_cadena(estados_A)
    _, _, base_medicion_B = inicializar_protocolo(NUMERO_DE_QUBITS)
    qubits_codificados_A = codificar_qubits(estados_A, base_codificacion_A)
    ruido = noises.BitFlip(probability=PROBABILIDAD_FLIP_BIT)
    qubits_codificados_A.apply_gate_noise(ruido)
    circuito_medido = medir_qubits(qubits_codificados_A, base_medicion_B)
    dispositivo = LocalSimulator("braket_dm")
    resultado = dispositivo.run(circuito_medido, shots=1).result()
    bits_medidos = list(resultado.measurements[0])
    clave_cruda_alice = np.concatenate(
        (clave_cruda_alice, filtrar_qubits(bits_enviados, base_codificacion_A, base_medicion_B))
    )
    clave_cruda_bob = np.concatenate(
        (clave_cruda_bob, filtrar_qubits(bits_medidos, base_codificacion_A, base_medicion_B))
    )

clave_cruda_alice = clave_cruda_alice[:12]
clave_cruda_alice

clave_cruda_bob = clave_cruda_bob[:12]
clave_cruda_bob

codigo_correccion_errores = GolayCode()

matriz_generadora = codigo_correccion_errores.get_generator_matrix()
verificacion_paridad = codigo_correccion_errores.get_parity_check_matrix()
matriz_b = codigo_correccion_errores.get_b_matrix()

clave_codificada_A = np.matmul(matriz_generadora, clave_cruda_alice) % 2
print(f'Clave de Alice después de codificación: {clave_codificada_A}')

sindrome_A = np.matmul(clave_codificada_A, verificacion_paridad) % 2
print(f'Síndrome de Alice (debe ser todo cero): {sindrome_A}')

bits_paridad = clave_codificada_A[12:]
print(f'Información enviada a Bob: {bits_paridad}')

clave_codificada_B = np.concatenate((clave_cruda_bob, bits_paridad))
print(clave_codificada_B)

sindrome_B = np.matmul(clave_codificada_B, verificacion_paridad) % 2
print(sindrome_B)

sindrome_BB = np.matmul(sindrome_B, matriz_b) % 2
sindrome_BB

if sindrome_BB.sum() < 4:
    mascara_correccion = np.concatenate((sindrome_BB, np.zeros(12,)))
    print(mascara_correccion)
else:
    print("La decodificación falló - más de 3 errores")

clave_corregida = np.mod(clave_cruda_bob + mascara_correccion[:12], 2).astype(int)
clave_corregida

clave_corregida == clave_cruda_alice

clave_ascii = base64.b64encode(
    convert_to_octets(arreglo_a_cadena(clave_corregida))
).decode('ascii')

print(clave_ascii)

print(circuito_medido)
from braket.visualization import circuit_visualizer
circuit_visualizer.ascii_draw(circuito_medido)
import os
import platform
import psutil
import socket
import subprocess
import re

def obtener_procesador():
    try:
        resultado = subprocess.check_output("wmic cpu get name", shell=True).decode()
        lineas = resultado.strip().split('\n')
        if len(lineas) >= 2:
            return lineas[1].strip()
        else:
            return platform.processor()
    except Exception as e:
        return f"Error: {e}"

def obtener_info_sistema():
    
    info = {}
    info["Nombre del dispositivo"] = socket.gethostname()
    info["Sistema"] = platform.system()
    info["Versi�n de Windows"] = platform.version()
    info["Procesador"] = obtener_procesador()
    info["Arquitectura"] = platform.architecture()[0]
    info["N�mero de n�cleos"] = psutil.cpu_count(logical=False)
    info["RAM total (GB)"] = round(psutil.virtual_memory().total / (1024**3), 2)
    info["Disco total (GB)"] = round(psutil.disk_usage('/').total / (1024**3), 2)

    try:
        battery = psutil.sensors_battery()
        if battery:
            info["Bater�a actual (%)"] = f"{battery.percent} %"
        else:
            info["Bater�a actual (%)"] = "No disponible"
    except Exception as e:
        info["Bater�a actual (%)"] = "Error: " + str(e)

    return info

def generar_reporte_bateria():
    try:
        resultado = subprocess.run(["powercfg", "/batteryreport"], capture_output=True, text=True, shell=True)
        if resultado.returncode == 0:
            print("Salida de powercfg:\n", resultado.stdout)
            ruta_generada = re.search(r'saved to (.+battery-report\.html)', resultado.stdout, re.IGNORECASE)
            if ruta_generada:
                ruta = ruta_generada.group(1).strip()
                return ruta
            else:
                return os.path.expanduser("~\\battery-report.html")
        else:
            return f"Error ejecutando powercfg: {resultado.stderr}"
    except Exception as e:
        return f"Excepci�n al generar el reporte: {e}"

def extraer_capacidades_bateria(ruta_html):
    try:
        with open(ruta_html, 'r', encoding='utf-8', errors='ignore') as f:
            contenido = f.read()

        design_match = re.search(r"DESIGN CAPACITY\s+([\d,]+) mWh", contenido, re.IGNORECASE)
        full_match = re.search(r"FULL CHARGE CAPACITY\s+([\d,]+) mWh", contenido, re.IGNORECASE)

        design_val = design_match.group(1).replace(',', '') if design_match else "No encontrado"
        full_val = full_match.group(1).replace(',', '') if full_match else "No encontrado"

        return {
            "Capacidad de dise�o (mWh)": design_val,
            "Capacidad actual de carga completa (mWh)": full_val
        }

    except Exception as e:
        return {
            "Capacidad de dise�o (mWh)": f"Error: {e}",
            "Capacidad actual de carga completa (mWh)": f"Error: {e}"
        }

def main():
    print("Informaci�n del sistema:\n")
    info = obtener_info_sistema()
    for clave, valor in info.items():
        print(f"{clave}: {valor}")

    print("\nGenerando reporte de bater�a...\n")
    ruta_reporte = generar_reporte_bateria()

    if isinstance(ruta_reporte, str) and ruta_reporte.endswith(".html") and os.path.exists(ruta_reporte):
        resultados = extraer_capacidades_bateria(ruta_reporte)
        print("\nResumen del estado de la bater�a:\n")
        for clave, valor in resultados.items():
            print(f"{clave}: {valor}")
    else:
        print("El reporte se logro generar en html")

    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()

# NOTA
# Este comando fue el comando utilizado en la terminal para proceder a empaquetar:
# pyinstaller --onefile  --icon=Bateria.ico Reporte_de_sistema2.0.py


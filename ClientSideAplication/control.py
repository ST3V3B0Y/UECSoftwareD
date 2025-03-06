# Importación de bibliotecas necesarias
import socket  # Para establecer la conexión con el servidor a través de sockets
import json  # Para codificar y decodificar datos en formato JSON
import psutil  # Para obtener información sobre los procesos en ejecución del sistema
import ctypes  # Para interactuar con las API del sistema operativo (aunque no se está utilizando en el código actual)

# Configuración de la dirección del servidor
SERVER_HOST = '10.33.0.93'  # Dirección IP del servidor al que se conecta el cliente
SERVER_PORT = 5040  # Puerto en el que el servidor escucha las conexiones

# Importación de bibliotecas de Tkinter para la interfaz gráfica
import tkinter as tk  # Para crear ventanas de la interfaz gráfica
from PIL import Image, ImageTk  # Pillow para manejar imágenes dentro de la GUI
from pynput import mouse, keyboard  # Para bloquear el mouse y teclado
import threading  # Para crear y manejar hilos (threads)

# Función para bloquear el movimiento del mouse
def bloquear_mouse():
    # Se usa un listener que escucha el movimiento y clics del mouse. Aquí, simplemente los desactiva.
    with mouse.Listener(on_move=lambda x, y: False, on_click=lambda x, y, button, pressed: False) as listener:
        listener.join()  # El listener se mantiene activo hasta que se cierre

# Función para bloquear el teclado
def bloquear_teclado():
    # Se usa un listener que escucha las teclas presionadas y simplemente las bloquea.
    with keyboard.Listener(on_press=lambda key: False) as listener:
        listener.join()  # El listener se mantiene activo hasta que se cierre

# Función para mostrar el protector de pantalla
def mostrar_protector():
    ventana = tk.Tk()  # Crear una nueva ventana de Tkinter
    ventana.attributes('-fullscreen', True)  # Poner la ventana en modo pantalla completa

    # Cargar la imagen para usar como protector de pantalla
    """imagen = Image.open("src/images/tu_imagen.jpg")"""  # Esta línea es un comentario, reemplazable con el nombre de la imagen
    imagen = Image.open("C:\UECSoftware\UEC-Flask\ClientSideAplication\src\images\AIO Salones 1920 x 1080.jpg")
    imagen = imagen.resize((ventana.winfo_screenwidth(), ventana.winfo_screenheight()), Image.ANTIALIAS)  # Ajusta la imagen al tamaño de la pantalla
    imagen_fondo = ImageTk.PhotoImage(imagen)  # Convierte la imagen a un formato que Tkinter puede mostrar

    # Crear un label que contendrá la imagen y cubrirá toda la ventana
    label_fondo = tk.Label(ventana, image=imagen_fondo)
    label_fondo.place(x=0, y=0, relwidth=1, relheight=1)  # Coloca la imagen para que ocupe toda la pantalla

    # Evitar que la ventana se cierre con Alt+F4
    ventana.protocol("WM_DELETE_WINDOW", lambda: None)

    ventana.mainloop()  # Ejecuta el loop principal de Tkinter para mostrar la ventana

# Función para desbloquear el mouse y el teclado
def desbloquear():
    global listener
    listener.stop()  # Detiene el listener que bloquea el mouse y el teclado

# Función para ejecutar el bloqueo del mouse y teclado en hilos separados
def ejecutar_bloqueo():
    # Se crean y ejecutan los hilos para bloquear el mouse y el teclado
    mouse_hilo = threading.Thread(target=bloquear_mouse)
    teclado_hilo = threading.Thread(target=bloquear_teclado)

    mouse_hilo.start()  # Inicia el hilo para bloquear el mouse
    teclado_hilo.start()  # Inicia el hilo para bloquear el teclado

    # Muestra el protector de pantalla
    mostrar_protector()

# Función para obtener los procesos en ejecución
def get_processes():
    processes = []
    # Utiliza psutil para iterar sobre los procesos en ejecución y almacenar su información
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        processes.append(proc.info)  # Añade la información de cada proceso a la lista
    return processes

# Función para conectar al servidor y manejar la comunicación
def connect_to_server():
    client = None  # Variable que representará la conexión del cliente
    try:
        # Crear un socket TCP/IP
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER_HOST, SERVER_PORT))  # Conectar al servidor en la IP y puerto configurados
        print("Client Side Application")

        while True:
            try:
                # Recibe los datos del servidor (hasta 1024 bytes)
                data = client.recv(1024).decode()
                if not data:
                    break  # Si no se recibe nada, sale del bucle
                ejecutar_bloqueo()  # Bloquea el mouse y el teclado

                # Intenta decodificar el mensaje recibido como un JSON
                command = json.loads(data)
                if command['action'] == 'unlock':  # Si la acción es desbloquear
                    desbloqueo = desbloquear()  # Desbloquea el sistema
                    response = json.dumps({'action': 'unlock', 'data': desbloqueo})  # Prepara la respuesta

                elif command['action'] == 'lock':  # Si la acción es bloquear
                    ejecutar_bloqueo()  # Bloquea nuevamente el sistema

                # Obtiene los procesos en ejecución y los envía al servidor
                processes = get_processes()
                response = json.dumps({'action': 'processes', 'data': processes})
                client.send(response.encode())  # Envía la respuesta con la lista de procesos

            except json.JSONDecodeError:
                print("Error al decodificar JSON")
            except Exception as e:
                print(f"Error: {e}")  # Imprime cualquier otro error
                break

    except socket.error as e:
        print(f"Error al crear o conectar el socket: {e}")  # Maneja cualquier error de conexión
    finally:
        if client is not None:  # Verifica si el socket fue creado
            client.close()  # Cierra la conexión del socket

# Punto de entrada principal del programa
if __name__ == "__main__":
    connect_to_server()  # Llama a la función para iniciar la conexión con el servidor

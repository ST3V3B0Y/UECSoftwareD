import socket  # Importa el módulo socket para la comunicación en red

def main():
    # Crear un socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Se especifica el tipo de socket: AF_INET para direcciones IPv4 y SOCK_STREAM para una conexión TCP.

    # Conectar al servidor en la dirección IP y puerto especificados
    server_address = ('127.0.0.1', 5000)  # Dirección IP del servidor y puerto. '127.0.0.1' es localhost, el mismo equipo
    client_socket.connect(server_address)  # Establece la conexión con el servidor

    try:
        # Enviar un mensaje al servidor
        message = "¡Hola, servidor!"  # El mensaje que se enviará al servidor
        client_socket.sendall(message.encode())  # Envía el mensaje codificado en formato byte

        # Recibir la respuesta del servidor
        data = client_socket.recv(1024)  # Recibe hasta 1024 bytes de datos desde el servidor
        print(f"Respuesta del servidor: {data.decode()}")  # Decodifica y muestra la respuesta del servidor

    finally:
        client_socket.close()  # Cierra la conexión del socket una vez que se termina la comunicación

# Si este script se ejecuta directamente, llama a la función main
if __name__ == '__main__':
    main()

# INTENTAR CONECTAR OTRO EQUIPO Y ESPERAR EL MENSAJE DE RESPUESTA A CONEXIÓN 

import socket

def main():
    # Crear un socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Conectar al servidor en la dirección IP y puerto especificados
    server_address = ('127.0.0.1', 5000)  # Reemplaza con la IP del servidor
    client_socket.connect(server_address)

    try:
        # Enviar un mensaje al servidor
        message = "¡Hola, servidor!"
        client_socket.sendall(message.encode())

        # Recibir la respuesta del servidor
        data = client_socket.recv(1024)
        print(f"Respuesta del servidor: {data.decode()}")
    finally:
        client_socket.close()

if __name__ == '__main__':
    main()
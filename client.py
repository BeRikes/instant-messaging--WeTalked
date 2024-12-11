import socket


def start_client(host='127.0.0.1', port=65432):
    """客户端socket程序"""
    # 创建一个socket对象
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 连接到服务器
        s.connect((host, port))
        while True:
            # 获取用户输入
            message = input("Enter message to send: ")
            if message.lower() == 'exit':
                break
            # 发送消息到服务器
            s.sendall(message.encode())
            # 接收响应
            data = s.recv(1024)
            print(f"Received from server: {data.decode()}")


if __name__ == "__main__":
    server_ip_addr = ''
    port = 65432
    start_client(server_ip_addr, port)
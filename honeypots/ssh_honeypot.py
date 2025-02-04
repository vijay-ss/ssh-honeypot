import os
import socket
import paramiko
import threading
import logging
from logging.handlers import RotatingFileHandler

SSH_BANNER = "SSH-2.0-MySSHServer_1.0"

host_key = paramiko.RSAKey(filename="server.key")
base_dir = os.getcwd()
cmd_audits_log_filepath = os.path.join(base_dir, "log_files", "cmd_audits.log")
creds_audits_log_filepath = os.path.join(base_dir, "log_files", "creds_audits.log")


def create_logging_filehandler(
        logger_name: str,
        log_filepath: str,
        log_format: str,
        level = logging.INFO,
) -> RotatingFileHandler:
    logging_format = logging.Formatter(log_format)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    log_handler = RotatingFileHandler(log_filepath, maxBytes=2000, backupCount=3)
    log_handler.setFormatter(logging_format)
    logger.addHandler(log_handler)

    return logger

funnel_logger = create_logging_filehandler(logger_name="FunnelLogger", log_filepath=cmd_audits_log_filepath, log_format="%(message)s")
creds_logger = create_logging_filehandler(logger_name="CredsLogger", log_filepath=creds_audits_log_filepath, log_format="%(message)s")

def emulated_shell(channel, client_ip: str):
    """
        channel: way to send strings over ssh connection
    """
    shell_prompt = b"corporate-jumpbox2$ " # $ means elevated user permissions
    channel.send(shell_prompt)
    command = b""

    while True:
        char = channel.recv(1)
        channel.send(char)
        if not char:
            channel.close()
        
        command += char.strip()

        if char == b"\r":
            if command == b"exit":
                response = b"\n Goodbye!\n"
                channel.close()
            elif command == b"pwd":
                workdir = os.path.join("user", "local")
                response = b"\n" + workdir.encode() + b"\r\n"
                creds_logger.info(f"Command {command} executed by {client_ip}")
            elif command == b"whoami":
                response = b"\n" + b"corpuser1" + b"\r\n"
                creds_logger.info(f"Command {command} executed by {client_ip}")
            elif command == b"ls":
                response = b"\n" + b"jumpbox1.conf" + b"\r\n"
                creds_logger.info(f"Command {command} executed by {client_ip}")
            elif command == b"cat jumpbox1.conf":
                response == b"\n" + b"Go to xyz.com" + b"\r\n"
                creds_logger.info(f"Command {command} executed by {client_ip}")
            else:
                response = b"\n" + bytes(command) + b"\r\n"
                creds_logger.info(f"Command {command} executed by {client_ip}")
            channel.send(response)
            channel.send(shell_prompt)
            command = b""

class Server(paramiko.ServerInterface):

    def __init__(self, client_ip: str, input_username: str=None, input_password: str=None) -> None:
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
    
    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        funnel_logger.info(f"Client {self.client_ip} attempted conneciton with username: {username}, password {password}")
        creds_logger.info(f"{self.client_ip}, {username}, {password}")
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True
    
    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True

def client_handle(client, addr: str, username: str, password: str):
    client_ip = addr[0]
    print(f"{client_ip} has connected to the server.")

    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        server = Server(client_ip=client_ip, input_username=username, input_password=password)

        transport.add_server_key(host_key)

        transport.start_server(server=server)

        channel = transport.accept(100)
        if channel is None:
            print("No channel was opened.")
        
        standard_banner = "Welcome to Ubuntu 22.04 LTS (Jammy Jellyfish)!\r\n\r\n"
        channel.send(standard_banner)
        emulated_shell(channel, client_ip=client_ip)
    except Exception as error:
        print(error)
    finally:
        try:
            transport.close()
        except Exception as error:
            print(error)
        client.close()

def honeypot(address: str, port: str, username: str, password: str):
    """Listens for ipv4 connection on tcp port.
    """
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))

    socks.listen(100)
    print(f"SSH server is listening on port {port}...")

    while True:
        try:
            client, addr = socks.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            ssh_honeypot_thread.start()
        except Exception as error:
            print(error)

honeypot("127.0.0.1", 2223, username=None, password=None)
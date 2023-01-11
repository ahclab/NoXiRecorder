import socket
import datetime
import subprocess
from rich import print
import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--common_setting_path",
                        default="NoXirecorder/setting/common_setting.json")
    parser.add_argument(
        "--network_setting_path", default="NoXirecorder/setting/network_setting.json"
    )
    args = parser.parse_args()

    # init
    with open(args.common_setting_path) as f:
        setting = json.load(f)
        user = setting["user"]
    with open(args.network_setting_path) as f:
        setting = json.load(f)
        BUFSIZE = setting["record"]["bufsize"]
        IP = setting["record"][user]["ip"]
        PORT = setting["record"][user]["port"]
        HEADER = f"[{user.upper()}]"

    # Server startup and standby
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )  # Address already in use error avoidance
    print(f"IP: {IP}")
    print(f"PORT: {PORT}")
    server.bind((IP, PORT))  # Server start-up
    print("[bold magenta]waiting for a connection request...[/bold magenta]")
    server.listen()  # Waiting for client request
    client, addr = server.accept()
    print(f"[white]{client}[/white]")

    # Respond to client requests
    # client.sendall(f"{HEADER} Connected".encode("utf-8"))
    capture = None
    recorder = None
    option = None
    start_flag = False
    while True:
        data = client.recv(BUFSIZE)  # Commands from the client
        now = str(datetime.datetime.now())  # Current time
        print(f"[cyan][{now}][/cyan] [white]{data.decode()}[/white]")

        # exit command
        if data.decode("UTF-8") == "exit":
            client.sendall(f"{HEADER} closed".encode("utf-8"))
            client.close()
            break

        if data.decode("UTF-8") == "time":  # Send current time
            client.sendall(now.encode("utf-8"))

        elif data.decode("UTF-8") == "ready":  # Transmission of standby status
            client.sendall(f"{HEADER} OK.".encode("utf-8"))

        elif data.decode("UTF-8") == "set option":  # Optional Setup
            client.sendall(
                f"{HEADER} Please enter the optional settings.".encode("utf-8")
            )
            option = client.recv(BUFSIZE).decode()
            client.sendall(f"{HEADER} set {option}".encode("utf-8"))

        elif data.decode("UTF-8") == "cat option":  # Show options that have been set
            client.sendall(f"{HEADER} {option}".encode("utf-8"))

        elif data.decode("UTF-8") == "record":  # Execution of the recording program
            client.sendall(
                f"{HEADER} Launch the recording program".encode("utf-8"))
            if option == None:
                recorder = subprocess.Popen(
                    f"python NoXiRecorder/AVrecordeR.py",
                    shell=True,
                    stdin=subprocess.PIPE,
                )
            else:
                recorder = subprocess.Popen(
                    f"python NoXiRecorder/AVrecordeR.py {option}",
                    shell=True,
                    stdin=subprocess.PIPE,
                )
        elif data.decode("UTF-8") == "start":
            if recorder == None:
                client.sendall(
                    f"{HEADER} Recording program is not launch.".encode(
                        "utf-8")
                )
            else:
                start_flag = True
                client.sendall(
                    f"{HEADER} Start AV Recording Program".encode("utf-8"))
                recorder.stdin.write("s\n".encode("utf-8"))
                recorder.stdin.flush()
        elif data.decode("UTF-8") == "end":
            if recorder == None:
                client.sendall(
                    f"{HEADER} Recording program is not launch.".encode(
                        "utf-8")
                )
            elif not start_flag:
                client.sendall(
                    f"{HEADER} Recording program is not start.".encode("utf-8")
                )
            else:
                client.sendall(
                    f"{HEADER} End AV Recording program".encode("utf-8"))
                recorder.stdin.write("e\n".encode("utf-8"))
                recorder.stdin.flush()
        else:
            client.sendall(
                f"{HEADER} The command is not provided.".encode("utf-8"))

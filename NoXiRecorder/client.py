import socket
import sys
import time
import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--setting_path", default="NoXirecorder/setting/network_setting.json")
    args = parser.parse_args()

    # init
    flag = {"expert": False, "novice": False}
    client = {}
    with open(args.setting_path) as f:
        setting = json.load(f)
        client["expert"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client["novice"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        BUFSIZE = setting["record"]["bufsize"]
        for user in ["novice", "expert"]:
            IP = setting["record"][user]["ip"]
            PORT = setting["record"][user]["port"]
            print(f"USER: {user}")
            print(f"IP: {IP}")
            print(f"PORT: {PORT}")
            try:
                client[user].connect(
                    (IP,
                     PORT)
                )
                flag[user] = True
            except:
                print(f"Unable to connect ({user})")
                # sys.exit()

    if flag["expert"] == False & flag["novice"] == False:
        print("Unable to connect to server")
        exit(1)

    if (flag["expert"] == True & flag["novice"] == True):
        while True:
            msg = input(">>")
            client["expert"].sendall(msg.encode("utf-8"))
            client["novice"].sendall(msg.encode("utf-8"))

            data = client["expert"].recv(BUFSIZE)
            print(data.decode("UTF-8"))
            data = client["novice"].recv(BUFSIZE)
            print(data.decode("UTF-8"))

            if msg == "exit":
                break
    elif (flag["expert"] == True):
        while True:
            msg = input(">>")
            client["expert"].sendall(msg.encode("utf-8"))

            data = client["expert"].recv(BUFSIZE)
            print(data.decode("UTF-8"))

            if msg == "exit":
                break
    elif (flag["novice"] == True):
        while True:
            msg = input(">>")
            client["novice"].sendall(msg.encode("utf-8"))

            data = client["novice"].recv(BUFSIZE)
            print(data.decode("UTF-8"))

            if msg == "exit":
                break

    time.sleep(2)
    client["expert"].close()
    client["novice"].close()

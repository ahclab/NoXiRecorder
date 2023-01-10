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
    client = {}
    with open(args.setting_path) as f:
        setting = json.load(f)
        client["expert"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client["novice"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        BUFSIZE = setting["record"]["bufsize"]
        for user in ["novice", "expert"]:
            print(setting["record"][user]["ip"])
            try:
                client[user].connect(
                    (setting["record"][user]["ip"],
                     setting["record"][user]["port"])
                )
            except:
                print(f"Unable to connect ({user})")
                # sys.exit()

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

    time.sleep(2)
    client["expert"].close()
    client["novice"].close()

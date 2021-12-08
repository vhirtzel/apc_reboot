import configparser
import threading
import sys
import raritan.rpc
from raritan.rpc import pdumodel


def main(ip=sys.argv[1]):
    config = parseConfig()
    user = getUser(config)
    passwd = getPass(config)
    hosts = getHosts(config)
    jobs = []
    for host in hosts:
        jobs.append(threading.Thread(target=powercycle, args=(user, passwd, host, ip), daemon=True))

    [j.start() for j in jobs]
    [j.join() for j in jobs]


def parseConfig():
    config = configparser.ConfigParser()
    config.read("configfile.ini")
    return config


def getUser(config):
    user = config["Raritan"]["user"]
    return user


def getPass(config):
    passwd = config["Raritan"]["passwd"]
    return passwd


def getHosts(config):
    hosts = []
    for key in config["RaritanPDUs"]:
        hosts.append(config["RaritanPDUs"][key])
    return hosts

reboot_lock = threading.RLock()


def powercycle(user, passwd, host, ip):
    agent = raritan.rpc.Agent(
        "https", host, user, passwd, disable_certificate_verification=True
    )
    pdu = pdumodel.Pdu("model/pdu/0", agent)
    outlets = pdu.getOutlets()
    for outlet in outlets:
        name = outlet.getSettings().name
        if name == ip:
            with reboot_lock:
                outlet.cyclePowerState()
                quit()


if __name__ == "__main__":
    main()

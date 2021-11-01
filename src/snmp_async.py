import sys
import asyncio
import configparser
import aiosnmp
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def main(ip=sys.argv[1]):
    loop = asyncio.get_event_loop()
    oids = []
    for i in range(1, 25):
        oids.append(f".1.3.6.1.4.1.318.1.1.4.4.2.1.4.{i}")
    pdus = asyncio.Queue()
    config = parseConfig()
    hosts = getHosts(config)
    community = getCommunity(config)
    loop.run_until_complete(loop_over_ips(ip, community, oids, pdus, hosts))


def parseConfig():
    config = configparser.ConfigParser()
    config.read("configfile.ini")
    return config


def getHosts(config):
    hosts = []
    for key in config["Hosts"]:
        hosts.append(config["Hosts"][key])
    return hosts


def getCommunity(config):
    community = config["Credentials"]["community"]
    return community


def check_valid_ip(config, entry):
    entry_lst = entry.split(".")
    for ip_range in config["IP Ranges"]:
        range_str = config["IP Ranges"][ip_range]
        lst = range_str.split(".")
        if entry_lst[:3] != lst[:3]:
            continue
        range_lst = lst[3].split(":")
        if int(entry_lst[3]) in range(int(range_lst[0]), int(range_lst[1]) + 1):
            return True


async def loop_over_ips(ip, community, oids, pdus, hosts: list) -> None:
    tasks = []  # you should move tasks below first for loop
    for host in hosts:
        tasks.append(get_outlets(community, oids, pdus, host))
    tasks.append(reboot_machine(ip, community, pdus))
    await asyncio.gather(
        *tasks
    )  # or move gather outside first loop, it caused RuntimeError


async def get_outlets(community, oids, pdus, ip):
    async with aiosnmp.Snmp(
        host=ip,
        port=161,
        community=community,
        timeout=5,
        retries=1,
        max_repetitions=10,
    ) as snmp:
        # get
        try:
            results = await snmp.get(oids)
            i = 1
            for res in results:
                await pdus.put(
                    (
                        ip,
                        str(res.value)[2 : len(str(res.value)) - 1],
                        f".1.3.6.1.4.1.318.1.1.4.4.2.1.3.{i}",
                    )
                )
                i += 1
                print(f"Added Outlet {i}")
        except Exception:
            pass


async def reboot_machine(ip, community, pdus):
    processed = False
    while processed is False:
        item = await pdus.get()
        print(item)
        print(item[2])
        if item[1] == ip:
            async with aiosnmp.Snmp(
                host=item[0],
                port=161,
                community=community,
                timeout=5,
                retries=1,
                max_repetitions=10,
            ) as snmp:
                # get
                try:
                    await snmp.set([(item[2], 2)])
                except aiosnmp.exceptions.SnmpErrorGenErr:
                    pass
                await asyncio.sleep(1)
                try:
                    await snmp.set([(item[2], 1)])
                except aiosnmp.exceptions.SnmpErrorGenErr:
                    pass
                processed = True
    quit()


main()

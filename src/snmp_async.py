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
    config = configparser.ConfigParser()
    config.read("configfile.ini")
    hosts = getHosts(config)
    community = getCommunity(config)
    loop.run_until_complete(loop_over_ips(ip, community, oids, pdus, hosts))


def getHosts(config):
    """Collects the host IPs in a list to be iterated over

    Args:
        config (list[str]): The list generated from configparser.ConfigParser().read()

    Returns:
        list[str]: List of IP addresses of PDUs
    """
    hosts = []
    for key in config["Hosts"]:
        hosts.append(config["Hosts"][key])
    return hosts


def getCommunity(config):
    """Get the SNMPv1 community string from the config file

    Args:
        config (list[str]): The list generated from configparser.ConfigParser().read()

    Returns:
        str: The SNMPv1 community string with Write Access to the PDUs
    """
    community = config["Credentials"]["community"]
    return community


async def loop_over_ips(ip: str, community: str, oids: list[str], pdus: asyncio.Queue, hosts: list[str]) -> None:
    """Function to generate the tasks to be run asynchronously

    First it creates a task for getOutlets for each PDU to find the machine,
    then it adds a task to reboot the machine.

    Args:
        ip (str): IP address of Machine to be Rebooted
        community (str): SNMPv1 community string with write access
        oids (str): OIDs representing each outlet of the PDU to check
        pdus (asyncio.Queue): asyncio Queue Object that will hold the IP and OID 
        representing the PDU/outlet combination that the Machine represented by ip is plugged into
        hosts (list): List of PDU IPs gathered by getHosts()
    """
    tasks = [] 
    for host in hosts:
        tasks.append(get_outlets(community, oids, pdus, host))
    tasks.append(reboot_machine(ip, community, pdus))
    await asyncio.gather(
        *tasks
    )


async def get_outlets(ip: str, community: str, oids: list[str], pdus: asyncio.Queue) -> None:
    """With the

    Args:
        ip (str): IP address of Machine to be Rebooted
        community (str): SNMPv1 community string with write access
        oids (list[str]): List of OIDs representing each outlet of the PDU to check
        pdus (asyncio.Queue): asyncio Queue Object that will hold the IP and OID
    """
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


async def reboot_machine(ip: str, community: str, pdus: asyncio.Queue) -> None:
    """[summary]

    Args:
        ip (str): [description]
        community (str): [description]
        pdus (asyncio.Queue): [description]
    """
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
                # set
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

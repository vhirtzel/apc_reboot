# apc_reboot
Powercycling APC Outlets using SNMP write requests using aiosnmp, and Slack Bolt API for an interactive Slack Bot
## Setting up the Slack Bot
I followed the [guide here](https://api.slack.com/start/building/bolt-python) to setup a basic Bolt app.

## Using this script
### Using Docker
0) Update your APC PDU Outlet labels for all of your outlets with the IPv4 addresses of the machines plugged in. Add an SNMPv1 community string with Write Access.
1) Clone this repository and change directories to the root of the repo
2) Create a slack.env file that contains the SLACK_BOT_TOKEN and SLACK_APP_TOKEN variables in the following format:
```
SLACK_BOT_TOKEN=xoxb-<Your Bot Token Here>
SLACK_APP_TOKEN=xapp-<Your App Token Here>
```
3) In the src directory create a file called `configfile.ini` that follows the format outlined below.
4) Install Docker Engine for your platform: [Instructions here](https://docs.docker.com/engine/install/)
5) Build the Docker container: `docker build -t apc-reboot .`
6) Run the Docker container with the Slack Environment Variables `docker run --env-file slack.env -d -p 3000:3000 apc-reboot`
7) You can now interact with the Slack Bot to reboot machines plugged in to your APC PDUs

### Using pyenv
0) Update your APC PDU Outlet labels for all of your outlets with the IPv4 addresses of the machines plugged in. Add an SNMPv1 community string with Write Access.
1) Clone this respository
2) Create a virtual environment `python3 -m venv .venv`
3) Enter the environment: `source .venv/bin/activate`
4) Install the requirements `pip install -r requirements.txt` 
5) In the src directory create a file called `configfile.ini` that follows the format outlined below.
6) Set the Slack Bot Environment variable:
```
export SLACK_BOT_TOKEN=xoxb-<Your Bot Token Here>
export SLACK_APP_TOKEN=xapp-<Your App Token Here>
```
7) Navigate to the src directory in the terminal and run `python3 app.py`
8) You can now interact with the Slack Bot to reboot machines plugged in to your APC PDUs

## Requirements
* Python >= 3.9
* configfile.ini that has the following format:
```
[Credentials]
community = '(SNMPv1 community string with Write access on the APC PDU)

[Hosts]
rack1front = '(ip address for your rack1front pdu)'
rack1back = '(ip address for your rack1back pdu)'

[IP Ranges]
range1 = '(ip address range in the following format: 1.1.1.1:254')
```
## To Do
* Change Access to SNMPv3, perhaps need to help aiosnmp support SNMPv3
* Add a way to check if all IPs in the Range are present among the PDUs and alert in the Slack Channel if they are not

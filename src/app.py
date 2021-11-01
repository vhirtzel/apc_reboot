import re
import os
import configparser
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


config = configparser.ConfigParser()
config.read("configfile.ini")

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))


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


# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message(re.compile("(reboot|Reboot).*"))
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    text_breakdown = message["text"].split()
    reboot_status = False
    for word in text_breakdown:
        valid_ip = check_valid_ip(config, word)
        if valid_ip is True:
            print(f"Found valid IP {word}")
            say(
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"Hey there <@{message['user']}>! I've found {word} confirm reboot by pressing the button!",
                        },
                        "accessory": {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Confirm"},
                            "action_id": "button_click",
                            "value": f"{word}",
                        },
                    }
                ],
                text=f"Hey there <@{message['user']}>! I've found {word} confirm reboot by pressing the button!",
            )
            reboot_status = True
    if reboot_status is False:
        say(
            text=f"Hey there <@{message['user']}> I could not find a valid IP to reboot."
        )


@app.action("button_click")
def action_button_click(body, ack, respond):
    ack()
    print("Button Pressed!")
    os.system(f"python snmp_async.py {body['actions'][0]['value']}")
    respond(f"I've rebooted {body['actions'][0]['value']} for you")


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

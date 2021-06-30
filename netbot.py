#!/usr/bin/env python3.6

import requests
from urllib3.exceptions import InsecureRequestWarning
import json
import os
import time
import re
import functools
import pynetbox
from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
starterbot_id = None
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "get"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
NB_TOKEN = os.environ['NETBOX_TOKEN']
NB_ENDPOINT = "https://netbox-staging.robot.car"
nb_api_endpoints = ['device','ipam','circuits','interface']

def helper_readout():
    return '''I understand the following commands currently:
        @netbot get device <device_name>
        @netbot get device <device_name> <sub-key> <sub-sub-key> <sub-sub-sub-key>
        @netbot get list-devices-tag <tag_name>
        @netbot get ipam ip_addresses <ip_address_expression>
        @netbot get ipam vlans <site_name>
        @netbot get ipam prefixes <site_name>
    '''

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            print("Recieved message:'{0}',type:'{1}'".format(message,type(message)))
            if message == '':
                message = " help"
                print("Overwritten to '{}'".format(message))
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def init_netbox():
    """Creates session to netbox and returns a netbox connection object"""
    nb = pynetbox.api(url=NB_ENDPOINT, ssl_verify=False, token=NB_TOKEN)
    return nb

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    #default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)
    #default_response = helper_readout()
    nb = init_netbox()
    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        if command.startswith(EXAMPLE_COMMAND + " device"):
            sub_command = command.split(EXAMPLE_COMMAND + " device")[1].strip()
            sub_args = sub_command.split()
            dev = sub_args[0]
            try:
                dev_result = nb.dcim.devices.get(name=dev)
                if len(sub_args) == 1:
                    response = dict(dev_result)
                elif len(sub_args) > 1:
                    sub_key = sub_args[1:]
                    try:
                        response = functools.reduce(getattr,sub_key,dev_result)
                    except AttributeError:
                        response = "Sorry I couldn't find the attributes {} on device {}.".format(sub_key,dev)
            except RequestError:
                response = "Sorry I couldn't find a device with the name {0}.".format(dev)
        elif command.startswith(EXAMPLE_COMMAND + " list-devices-tag"):
            sub_command = command.split(EXAMPLE_COMMAND + " list-devices-tag")[1].strip()
            sub_args = sub_command.split()
            dev_tag = sub_args[0]
            try:
                dev_result = nb.dcim.devices.filter(tag=dev_tag)
                response = [x.name for x in dev_result]
            except Exception:
                response = "Sorry I couldn't find list of devices with tag {}".format(dev_tag)
        elif command.startswith(EXAMPLE_COMMAND + ' ipam'):
            sub_command = command.split(EXAMPLE_COMMAND + " ipam")[1].strip()
            sub_args = sub_command.split()
            section = sub_args[0]
            if section == "prefixes":
                result = nb.ipam.prefixes.filter(site=sub_args[1])
                response = [str(x) for x in result]
            elif section == "vlans":
                result = nb.ipam.vlans.filter(site=sub_args[1])
                response = [x.name for x in result]
            elif section == "ip_addresses":
                result = nb.ipam.ip_addresses.filter(sub_args[1])
                response = [(x.address,x.description) for x in result]
            else:
                response = "Sorry I couldn't find the attributes {} on ipam".format(section)
    elif command.startswith(' help'):
        #    response = "Sure...write some more code then I can do that!"
        print(command)
        response = "Hi I'm Netbot :robot_face: ! " + helper_readout()

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        #text=response or default_response
        text=response or helper_readout()
)

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")

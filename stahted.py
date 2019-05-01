#!/usr/bin/env python3

import re
import time
import json
import urllib
from slackclient import SlackClient
from keys import SLACK_KEY

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError as e:
    pass


class Stahted:
    DEFAULT_ALERT_DURATION = 10

    def __init__(self, alert_gpio):
        while not self.internet_on():
            time.sleep(3)
            pass

        self.slack = SlackClient(SLACK_KEY)
        self.alert_gpio = alert_gpio
        self.alert_start = None
        self.alert_duration = self.DEFAULT_ALERT_DURATION
        self.channels = set()

        # Fetch your Bot's User ID
        user_list = self.slack.api_call("users.list")
        for user in user_list.get('members'):
            if user.get('name') == "stahted":
                print('Found user `stahted`... continuing...')
                self.slack_user_id = user.get('id')
                break

        self.configure_gpio(self.alert_gpio)

    def listen(self):
        # Start connection
        if self.slack.rtm_connect():
            print("Connected!")
            return

            while True:
                if self.check_alert():
                    print("Done!")
                    for channel in self.channels:
                        self.slack.api_call(
                            "chat.postMessage",
                            channel=channel,
                            text="Alert complete :robot_face:",
                            as_user=True)
                    self.channels = set()

                for message in self.slack.rtm_read():
                    if self.at_message(message) or self.direct_message(message):
                        print("Message received: %s" % json.dumps(message, indent=2))
                        message_text = message['text']
                        if self.at_message(message):
                            message_text = message['text'].split("<@%s>" % self.slack_user_id)[1].strip()

                        try:
                            self.alert_duration = self.extract_int(message_text)
                        except ValueError:
                            pass

                        response = ''
                        if self.alert_duration > 600:
                            self.alert_duration = 600
                        if self.alert_duration != self.DEFAULT_ALERT_DURATION:
                            response = ' for {} seconds'.format(self.alert_duration)

                        # if re.match(r'.*(stahted).*', message_text, re.IGNORECASE):
                        self.alarm_on()
                        self.slack.api_call(
                            "chat.postMessage",
                            channel=message['channel'],
                            text=":alert: :alert: Jonathan Placa has been alerted{} :alert: :alert:".format(response),
                            as_user=True)
                        self.channels.add(message['channel'])

                time.sleep(1)

    def at_message(self, message):
        if 'user' in message and message['user'] != self.slack_user_id:
            return 'text' in message and "<@{}>".format(self.slack_user_id) in message['text']
        else:
            return False

    def direct_message(self, message):
        if 'user' in message and message['user'] != self.slack_user_id:
            return 'text' in message and 'channel' in message and message['channel'].startswith("D")
        else:
            return False

    def internet_on(self):
        try:
            urllib.request.urlopen('http://google.com', timeout=1)
            return True
        except urllib.request.URLError:
            return False

    def extract_int(self, msg):
        return int(''.join(list(filter(str.isdigit, msg))))

    def check_alert(self):
        current_time = time.time()
        if self.alert_start is not None and (current_time - self.alert_start) > self.alert_duration:
            self.alert_start = None
            self.alert_duration = self.DEFAULT_ALERT_DURATION
            self.alarm_off()
            return True
        else:
            return False

    def alarm_on(self):
        self.alert_start = time.time()
        self.set_gpio(self.alert_gpio, True)

    def alarm_off(self):
        self.set_gpio(self.alert_gpio, False)

    def configure_gpio(self, gpio):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(gpio, GPIO.OUT)
            self.alarm_off()
        except NameError as e:
            print("No RPi, let's say it's now configured...")

    def set_gpio(self, gpio, enabled):
        try:
            if enabled:
                GPIO.output(gpio, GPIO.LOW)
            else:
                GPIO.output(gpio, GPIO.HIGH)
        except NameError as e:
            print("No RPi, let's say we set the gpio {}...".format(enabled))


stahted = Stahted(alert_gpio=18)
stahted.listen()

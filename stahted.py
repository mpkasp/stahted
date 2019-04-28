#!/usr/bin/env python3

import re
import time
import json
from slackclient import SlackClient
from keys import SLACK_KEY

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError as e:
    pass


class Stahted:
    def __init__(self, alert_gpio):
        self.slack = SlackClient(SLACK_KEY)
        self.alert_gpio = alert_gpio
        self.alert_start = None
        self.alert_duration = 30

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

            while True:
                if self.check_alert():
                    self.slack.api_call(
                        "chat.postMessage",
                        channel=message['channel'],
                        text="",
                        as_user=True)

                for message in self.slack.rtm_read():
                    if 'text' in message and message['text'].startswith("<@%s>" % self.slack_user_id):
                        print("Message received: %s" % json.dumps(message, indent=2))
                        message_text = message['text'].\
                            split("<@%s>" % self.slack_user_id)[1].\
                            strip()

                        try:
                            self.alert_duration = self.extract_int(message_text)
                        except ValueError:
                            pass

                        response = ''
                        if self.alert_duration > 600:
                            self.alert_duration = 600
                        if self.alert_duration != 30:
                            response = ' for {} seconds'.format(self.alert_duration)

                        # if re.match(r'.*(stahted).*', message_text, re.IGNORECASE):
                        self.alarm_on()
                        self.slack.api_call(
                            "chat.postMessage",
                            channel=message['channel'],
                            text=":alert: :alert: Jonathan Placa has been alerted{} :alert: :alert:".format(response),
                            as_user=True)

                time.sleep(1)

    def extract_int(self, msg):
        return int(''.join(list(filter(str.isdigit, msg))))

    def check_alert(self):
        current_time = time.time()
        if self.alert_start is not None and (current_time - self.alert_start) > self.alert_duration:
            self.alert_start = None
            self.alert_duration = 30
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
        except NameError as e:
            print("No RPi, let's say it's now configured...")

    def set_gpio(self, gpio, enabled):
        try:
            if enabled:
                GPIO.output(gpio, GPIO.HIGH)
            else:
                GPIO.output(gpio, GPIO.LOW)
        except NameError as e:
            print("No RPi, let's say we set the gpio {}...".format(enabled))


stahted = Stahted(alert_gpio=18)
stahted.listen()

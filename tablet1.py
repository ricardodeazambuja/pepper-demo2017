#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use showImage Method"""

from naoqi import ALProxy
from naoqi import ALBroker

import qi
import argparse
import sys
import time


def main(NAO_IP,NAO_PORT):
    """
    """
    # Subscribe to the proxies services

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       NAO_IP,         # parent broker IP
       NAO_PORT)       # parent broker port


    # Warning: SpeachRec must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    # global SpeachRec
    tabletService = ALProxy("ALTabletService")

    # Display a local image located in img folder in the root of the web server
    # The ip of the robot from the tablet is 198.18.0.1
    # tabletService.showImage("http://198.18.0.1/img/help_charger.png")

    time.sleep(3)

    # Hide the web view
    # tabletService.hideImage()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()

    main(args.ip,args.port)

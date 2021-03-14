# Author : Kevin Shahnazari
# Date: March 12th 2021

"""
This script Scrapes Changes the IP using
NordVPN to hide our IP address when scraping.
"""

import time
import subprocess
import os


# Caution This Vpn Changer is only Written For NORDVPN! with windows (Could be implemented in linux aswell)!!
class VpnChanger:

    # Get the list of possible vpn connections.
    def __init__(self, vpnlist):
        self.vpntexts = vpnlist
        self.counter = 0

    def changevpn(self):
        # The way this function works is that it tries out different
        # VPN servers and checks if there is a connection and also if
        # the IP has indeed changed. We don't want our own IP to be exposed
        # and banned. If the vpn is not working change to the next possible one.
        # If the connection isn't established within ten tries then send an error
        # to show an error is happening somewhere.
        vpnsuc = -1
        for i in range(0, 10):
            vpnsuc = self.trychangevpn()
            if vpnsuc == 0:
                break
            else:
                self.counter += 1
                if self.counter == len(self.vpntexts):
                    break
        if vpnsuc == -1:
            print("Big error in change vpn for some reason")

    def trychangevpn(self):
        try:
            # Change mac address. Uncomment to use. Code below needs more testing:
            # os.popen('tmac -n YourNetowrkconnection -rm")
            # My own connection
            # os.popen('tmac -n Ethernet 9 -rm")
            
            # disconnect any vpn connections
            os.popen('"C:/Program Files/NordVPN/NordVPN.exe" -d')
            time.sleep(10)
            # Get currrent IP address
            curip = os.popen("nslookup myip.opendns.com resolver1.opendns.com").read()
            pos = curip.find("myip.opendns.com")
            # If we can't get the ip something has went wrong
            if pos == -1:
                return -1
            # Connect to a server with command line with NordVPN
            oscommand = (
                '"C:/Program Files/NordVPN/NordVPN.exe" -c -n '
                + '"'
                + self.vpntexts[self.counter]
                + '"'
            )
            os.popen(oscommand)
            time.sleep(15)
            # Check to see if IP change from the original IP was successful.
            chngip = os.popen("nslookup myip.opendns.com resolver1.opendns.com").read()
            if chngip.find("myip.opendns.com") != -1 and chngip != curip:
                return 0
            else:
                return -1
        except:
            print("Error in trychange vpn")
            return -1

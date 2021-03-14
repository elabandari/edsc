import subprocess
import time
from VpnChanger import VpnChanger
from urladder import add_one_url_registered,add_one_url_predicted
from jobpostadder import add_one_job
from urlinfoadder import add_one_url_info

vpnlist = []
for i in range(10,100):
  vpnlist.append("United States #50" + str(i))
vpc=VpnChanger(vpnlist)

while True:
  # After We have send 10 requests to each webpage
  # Change the Mac address and IP to avoid getting detected
  # Note this code only works on windows with the help of NordVPN and Technitium MAC 
  # Address Changer. This could be implemented in different operating softwares later.
  vpc.changevpn()

  for _ in range(0,10):
    # Check to see if the business has registered with google and added their url
    add_one_url_registered()
    # Get information about URL's such as register date, expiredate and renewal date
    add_one_url_info()
    # Get the numbers of job postings a company has in Job bank
    add_one_job()
    # If the business is not registered in google try to find the most possible domain for the business
    add_one_url_predicted()
    # We can't go on full speed when scraping. We need to wait a little!
    time.sleep(5)
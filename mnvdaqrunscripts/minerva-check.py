#!/usr/bin/env python

from xmlrpclib import ServerProxy, Fault
from time import gmtime, strftime
import sys
import os
import time
import smtplib
import datetime

#
#  minerva-check.py   (W.Badgett)
#
#  Every minute, check to see if there have been recent beam $A9 
#  events.   If there have, check to see if minerva has recently 
#  taken data.  If not, increment a counter; if yes, reset counter.
#  If the counter finds data missing for five times, then send 
#  out warning to experts
#
#  Require beam event $A9 how recently?  in seconds
recentBeamLimit = 120.0

# How recently should triggers have been present?  in seconds
recentTriggerLimit = 60.0

#  How many times must DAQ fail to have taken data before alarm?
alarmFailures = 3
failCounter=0

#  Frequency of checking status, in seconds
checkFrequency = 300.0

# Where to look for trigger file
lastTriggerFileName="/work/conditions/last_trigger.dat"

sender    = "minerva"
receivers = "minerva-run-sms@fnal.gov"
devices = [ "G:EA9SNC", "G:E00SNC", "G:E2ASNC" ]


url="http://www-bd.fnal.gov/xmlrpc/Accelerator"

def getError(stat):
  sp = ServerProxy(url)
  try:
    ret = sp.getErrorInfo(stat)
  except Fault, err:
    print 'XML-RPC error: '+str(err)
  except socket.error, err:
    print 'Socket error: '+str(err[1])
  return ret['verbose_text']

    
def checkMinerva():

  global failCounter

  # First check to see if $A9 is OK
  serverProxy = ServerProxy(url)

  try:
    deviceData = serverProxy.getReading(devices)
  except Fault, err:
    print 'XML-RPC error: '+str(err)
    return
  except socket.error, err:
    print 'Socket error: '+str(err[1])
    return

  # Only consider G:EA9SNC for now
  reading = deviceData[0]
  name    = reading['name']
  data    = float(reading['scaled'])
  status  = int(reading['status'])
  units   = reading['units']
  print "%s %s %f %s %d"%(str(datetime.datetime.now()),name,data,units,status)

  # Perform check only if we have reasonable data
  if status == 0 and data > 0.0 and data < recentBeamLimit :

    deviceText = name+" status "+str(status)+" last A9 "+str(data)+" seconds ago "

    # Now check for recent Minerva trigger
    try:
      with open(lastTriggerFileName,'r') as triggerFile:

        for line in triggerFile:

          if line.find('time') >= 0:
            line = line.strip('\n')
            zeit = float(line.split('=')[1]) / 1E6
            deltaT = time.time() - zeit
            print time.strftime("%Y.%m.%d %H:%M:%S")+" Last Trigger %f seconds ago" % deltaT

            if deltaT > recentTriggerLimit:
 
              failCounter = failCounter + 1
              print time.strftime("%Y.%m.%d %H:%M:%S")+" " + str(failCounter) + " failures so far"
              if failCounter == alarmFailures:

                message = """MIME-Version: 1.0
Content-type: text/html
Subject: Minerva Error """+deviceText+"""
Minerva DAQ not running """+time.strftime("%Y.%m.%d %H:%M:%S",time.localtime())+"""<BR>"""+deviceText+"""
<BR>Last trigger """+str(deltaT)+""" seconds ago<BR>"""
                print message
                try:
                  smtp = smtplib.SMTP()
                  smtp.connect();
                  smtp.sendmail(sender,receivers,message)
                except:
                  print time.strftime("%Y.%m.%d %H:%M:%S",time.localtime())+"Failed to sendmail "
            else:
              print "Status OK"
              failCounter = 0

      triggerFile.close()
    except:
      # Race condition with the DAQ sometime, so skip check this time
      print "Problem opening file "+lastTriggerFileName+" incrementing failCounter"
      failCounter = failCounter + 1
      if failCounter == alarmFailures:
         message = """MIME-Version: 1.0
Content-type: text/html
Subject: Minerva Error """+deviceText+"""
Minerva DAQ not running """+time.strftime("%Y.%m.%d %H:%M:%S",time.localtime())+"""<BR>"""+deviceText+"""
<BR>Run status file """+lastTriggerFileName+""" not found"""
         print message
         try:
           smtp = smtplib.SMTP()
           smtp.connect();
           smtp.sendmail(sender,receivers,message)
         except:
           print time.strftime("%Y.%m.%d %H:%M:%S",time.localtime())+"Failed to sendmail "

  else:
    print name+" status "+str(status)+" last A9 "+str(data)+" skip check"


def main():
  
  global checkFrequency

  print "Starting minerva-check"
  while 1:
    checkMinerva()
    sys.stdout.flush()
    time.sleep(checkFrequency)
        
if __name__ == '__main__':
    main()


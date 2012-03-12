'''
Created on 7. mars 2012

@author: Simon_ny
'''

import ntplib, time

class TimeStampHandler(object):
    def __init__(self):
        
        try:
            ntpTimeClient = ntplib.NTPClient()
            response = ntpTimeClient.request('europe.pool.ntp.org', version=3)
            
            self.timeOffset = response.tx_timestamp - time.time()
            
            print "OK - time synchronized with time server: europe.pool.ntp.org"
            print "Registered offset: ", self.timeOffset
        except:
            print "Error connecting to time server: europe.pool.ntp.org"
            exit()
                                       
    def getTimeStamp(self):
        timeStamp = time.time() + self.timeOffset
        #print "TimeStamp:", timeStamp
        return timeStamp
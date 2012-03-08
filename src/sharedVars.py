'''
Created on 8. mars 2012

@author: Simon_ny
'''

class sharedTimeStampVars(object):
    def __init__(self):
        self.timeStamp = 0
        
    def setTimeStamp(self, value):
        self.timeStamp = value
        
    def getTimeStamp(self, value):
        return self.timeStamp
    
    def getStringTimeStamp(self):
        return str(self.timeStamp)
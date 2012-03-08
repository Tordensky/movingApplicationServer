'''
Created on 7. mars 2012

@author: Simon_ny
'''

import httplib
import PhoneDBHandler
import json
import time
from DbHandler import DBhandler



timeStamp = 0

dbHandler = PhoneDBHandler.DBHandler()

class Client(object):
    def __init__(self):
        self.conn = httplib.HTTPConnection('129.242.112.213', 4500)
                
    def get_updates(self):
        print "Send time stamp, ", timeStamp
        self.conn.request("GET", "/updates/" + str(timeStamp))

        response = self.conn.getresponse()
        
        body = response.read()
        
        ResultHandler().updateFromResult(body)
        
        self.conn.close()


class ResultHandler(object):
    def updateBoxesFromResult(self, data):
        print data
        test = json.loads(data)
        print test["timeStamp"]
        list = test["boxes"]
        for row in list:
            print "Box:", row
            items = row["items"]
            for item in items:
                print "    item:", item["itemName"]
                
    def updateFromResult(self, data):
        
        messageDict = json.loads(data)
        print "New TimeStamp: \t", messageDict["TimeStamp"]
        
        timeStamp = messageDict["TimeStamp"]
        print timeStamp
                
        print "NewBoxes: \t",messageDict["NewBoxes"]
        dbHandler.create_Boxes_from_list(messageDict["NewBoxes"])
        
        print "UpdtBoxes: \t",messageDict["UpdatedBoxes"]
        dbHandler.update_Boxes_from_list(messageDict["UpdatedBoxes"])
        
        print "DelBoxes \t", messageDict["DeletedBoxes"]
        dbHandler.delete_Boxes_from_list(messageDict["DeletedBoxes"])
        
                
if __name__ == "__main__":
    client = Client()
    dbHandler.setupSimPhoneDB()
    #dbHandler.createTestData()
    while (1):
        print "\n\n------"
        client.get_updates()
        time.sleep(10)



    
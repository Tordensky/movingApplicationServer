'''
Created on 7. mars 2012

@author: Simon_ny
'''

import httplib
import PhoneDBHandler
import json
import time
from sharedVars import sharedTimeStampVars

shared = sharedTimeStampVars()
dbHandler = PhoneDBHandler.DBHandler()

class Client(object):
    def __init__(self):
        self.conn = httplib.HTTPConnection('129.242.112.213', 4500)
                
    def get_updates(self):
        print "Send time stamp, ", shared.getStringTimeStamp()
        self.conn.request("GET", "/updates/" + shared.getStringTimeStamp())

        response = self.conn.getresponse()
        
        body = response.read()
        
        MessageHandler().updateFromResult(body)
        
        self.conn.close()
        
    def post_changes(self):
        self.conn.request("POST", "/updates/", MessageHandler().createUpdateMessage())
        
        response = self.conn.getresponse()
        
        body = response.read()
        
        print "Body: ", body
        
        if (body == "OK"):
            print "TODO SHOULD CLEAN UP"
        else:
            print "Something wrong"
        # TODO check result, if ok reset status in DB else re - send
        
        self.conn.close()


class MessageHandler(object):
    
    ''' Update local DB from Updates from server'''            
    def updateFromResult(self, data):
        
        messageDict = json.loads(data)
        
        #print "New TimeStamp: \t", messageDict["TimeStamp"]
        shared.setTimeStamp(messageDict["TimeStamp"])
                        
        #print "NewBoxes: \t",messageDict["NewBoxes"]
        dbHandler.create_Boxes_from_list(messageDict["NewBoxes"])
        
        #print "UpdtBoxes: \t",messageDict["UpdatedBoxes"]
        dbHandler.update_Boxes_from_list(messageDict["UpdatedBoxes"])
        
        #print "DelBoxes \t", messageDict["DeletedBoxes"]
        dbHandler.delete_Boxes_from_list(messageDict["DeletedBoxes"])
        
        # TODO 
            # LOCATIONS AND ITEMS
    
    ''' Sync New Changes with Server'''        
    def createUpdateMessage(self):
        updates = {}
        updates["NewBoxes"] = dbHandler.get_boxes_created_after_last_sync()
        updates["UpdatedBoxes"] = dbHandler.get_boxes_updated_after_last_sync()
        updates["DeletedBoxes"] = dbHandler.get_boxes_deleted_after_last_sync()
        
        return json.dumps(updates)
        
                
if __name__ == "__main__":
    count = 1
    client = Client()
    dbHandler.setupSimPhoneDB()
    #dbHandler.createTestData()
    while (1):
        print "\n\nGET ------ REQUEST: ", count
        client.get_updates()
        time.sleep(2)
        count += 1
        
        print "\nPOST ------ REQUEST: ", count
        client.post_changes()
        time.sleep(60)
        count += 1



    
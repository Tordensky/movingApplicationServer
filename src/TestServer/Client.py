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
        self.conn = httplib.HTTPConnection('movingapp.no-ip.org', 47301)
                
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
        
        result = json.loads(body)
        
        if (result["Status"] == "OK"):
            
            MessageHandler().update_from_post_update(result)
            print "Clean UP"
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
        
        # TODO FIX INCOMMING MESSAGE
        print "Message", messageDict["TimeStamp"]                
        #print "NewBoxes: \t",messageDict["NewBoxes"]
        dbHandler.create_Boxes_from_list(messageDict["NewBoxes"])
        
        #print "UpdtBoxes: \t",messageDict["UpdatedBoxes"]
        dbHandler.update_Boxes_from_list(messageDict["UpdatedBoxes"])
        
        #print "DelBoxes \t", messageDict["DeletedBoxes"]
        dbHandler.delete_Boxes_from_list(messageDict["DeletedBoxes"])
        
        # TODO 
            # LOCATIONS AND ITEMS
    
    
    def update_from_post_update(self, result):
        dbHandler.update_after_sync()
        dbHandler.set_box_bids_from_dict(result["BoxIdMap"]);
    
    ''' Sync New Changes with Server'''        
    def createUpdateMessage(self):
        updates = {}
        updates["NewBoxes"]     = dbHandler.get_boxes_created_after_last_sync()
        updates["UpdatedBoxes"] = dbHandler.get_boxes_updated_after_last_sync()
        updates["DeletedBoxes"] = dbHandler.get_boxes_deleted_after_last_sync()
        
        updates["NewItems"]     = dbHandler.get_items_created_after_last_sync()
        updates["UpdatedItems"] = dbHandler.get_items_updated_after_last_sync()
        updates["DeletedItems"] = dbHandler.get_items_deleted_after_last_sync()
        
        updates["NewLocations"] = dbHandler.get_locations_created_after_last_sync()
        updates["UpdatedLocations"] = dbHandler.get_locations_updated_after_last_sync()
        updates["DeletedLocations"] = dbHandler.get_locations_deleted_after_last_sync()
        
        return json.dumps(updates)
        
                
if __name__ == "__main__":
    count = 1
    client = Client()
    #dbHandler.setupSimPhoneDB()
    #dbHandler.createTestData()
    while (1):
        print "\n\nGET ------ REQUEST: ", count
        client.get_updates()
        time.sleep(2)
        count += 1
        
        print "\nPOST ------ REQUEST: ", count
        client.post_changes()
        time.sleep(2)
        count += 1
        
        if (count == 10):
            break



    
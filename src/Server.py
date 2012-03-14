import web
import json
import ServerDBHandler
import TimeStampHandler


urls = (
        '/', 'index',
        '/boxes/(.*)', 'Boxes',
        '/updates/(.*)', 'Updates'
        )

app = web.application(urls, globals())

testMessage = [{"BoxName": "Mordi", "BoxDescription": "Fardi"}, {"BoxName": "Fett", "BoxDescription": "Funker"}];
#print testMessage

timeHandler = TimeStampHandler.TimeStampHandler()
#movingDBHandler = DbHandler.DBhandler()

class index:
    def GET(self):

        #dbHandle = dbHandler.DBhandler()
        return "DRIT FETT"#json.dumps(movingDBHandler.get_boxes())
    
    def POST(self):
        print "KOMMER INN I POST"
        print "POST REQ: ", web.data()
    
class Updates:
    def GET(self, method_id):
        timeStamp = format(method_id)
        timeStamp = timeStamp.split('/')[0]
    
        #return json.dumps(message)
        return MessageHandler().createUpdateMessage(int(timeStamp))
        
    def POST(self, method_id):
                
        body = web.data()
        
        print "incoming post", body
        
        print "POST REQUEST"
        return MessageHandler().updateFromPost(body)
    
class Boxes:
    def GET(self, method_id):
        timeStamp = format(method_id)
        
        timeStamp = timeStamp.split('/')[0]
        movingDBHandler = ServerDBHandler.DBhandler()
        
        message = {}
        
        message["boxes"] = movingDBHandler.get_boxes_after_time(int(timeStamp))
        message["timeStamp"] = int(timeHandler.getTimeStamp())
        return json.dumps(message);
    
    def POST(self):
        web.data();
        pass
    
class MessageHandler(object):
    def createUpdateMessage(self, timeStamp):
        try:
            movingDBHandler = ServerDBHandler.DBhandler()
            
            message = {}
            
            message["NewLocations"] =       movingDBHandler.get_locations_created_after(timeStamp) 
            message["NewBoxes"] =           movingDBHandler.get_boxes_created_after(timeStamp)
            message["NewItems"] =           movingDBHandler.get_items_created_after(timeStamp)
            message["UpdatedLocations"] =   movingDBHandler.get_locations_updated_after(timeStamp)
            message["UpdatedBoxes"] =       movingDBHandler.get_boxes_updated_after(timeStamp)
            message["UpdatedItems"] =       movingDBHandler.get_items_updated_after(timeStamp)
            message["DeletedLocations"] =   movingDBHandler.get_locations_deleted_after(timeStamp)
            message["DeletedBoxes"] =       movingDBHandler.get_boxes_deleted_after(timeStamp)
            message["DeletedItems"] =       movingDBHandler.get_items_deleted_after(timeStamp)
            message["TimeStamp"] =          int(timeHandler.getTimeStamp())
            
            return json.dumps(message)
        
        except:
            return "SERVER ERROR"
    
    def updateFromPost(self, data):
        #try:
            movingDBHandler = ServerDBHandler.DBhandler()
            updates = json.loads(data)
            
            print "NL ", len(updates["NewLocations"])
            locationIDmap = movingDBHandler.create_locations_from_client(updates["NewLocations"], timeHandler)
            print "Location Map",  locationIDmap
            print "UL ", len(updates["UpdatedLocations"])
            print "DL ", len(updates["DeletedLocations"])
            
            
            print "NB ", len(updates["NewBoxes"])
            boxIdMap = movingDBHandler.create_boxes_from_client(updates["NewBoxes"], locationIDmap, timeHandler)
            print "BOX MAP", boxIdMap
            
            print "UB ", len(updates["UpdatedBoxes"])
            movingDBHandler.update_boxes_from_client(updates["UpdatedBoxes"], locationIDmap, timeHandler)
            
            print "DB ", len(updates["DeletedBoxes"])
            movingDBHandler.delete_boxes_from_client(updates["DeletedBoxes"], timeHandler)
            
            print "NI ", len(updates["NewItems"])
            itemIdMap  = movingDBHandler.create_items_from_client(updates["NewItems"], boxIdMap, timeHandler)
            print "Item Map", itemIdMap
            print "UB ", len(updates["UpdatedItems"])
            print "DB ", len(updates["DeletedItems"])
            
            response = {}
            response["Status"] = "OK"
            response["LocationIdMap"] = locationIDmap
            response["BoxIdMap"] = boxIdMap
            response["ItemIdMap"] = itemIdMap
        
            return json.dumps(response)
        #except:
        #    return "ERROR"
        # TODO return new BIDS
        
    
if __name__ == "__main__": 
        print "Starting Moving Server @: "
        ServerDBHandler.DBhandler().setupDb(timeHandler)
        #ServerDBHandler.DBhandler().createTestData(timeHandler)
        app.run()
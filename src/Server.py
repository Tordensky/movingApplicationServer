import web
import json
import ServerDBHandler
import TimeStampHandler


urls = (
        '/updates/(.*)', 'Updates'
        )

app = web.application(urls, globals())

timeHandler = TimeStampHandler.TimeStampHandler()


    
class Updates:
    def GET(self, method_id):
        timeStamp = format(method_id)
        timeStamp = timeStamp.split('/')[0]
    
        return MessageHandler().createUpdateMessage(int(timeStamp))
        
    def POST(self, method_id):
                
        body = web.data()      
        
        print "POST REQUEST"
        return MessageHandler().updateFromPost(body)
    
    
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
        try:
            movingDBHandler = ServerDBHandler.DBhandler()
            updates = json.loads(data, encoding='latin1')
            
            print "NL ", len(updates["NewLocations"])
            locationIDmap = movingDBHandler.create_locations_from_client(updates["NewLocations"], timeHandler)
            
            print "UL ", len(updates["UpdatedLocations"])
            movingDBHandler.update_locations_from_client(updates["UpdatedLocations"], timeHandler)
               
            print "DL ", len(updates["DeletedLocations"])
            movingDBHandler.delete_locations_from_client(updates["DeletedLocations"], timeHandler);           
            
            print "NB ", len(updates["NewBoxes"])
            boxIdMap = movingDBHandler.create_boxes_from_client(updates["NewBoxes"], locationIDmap, timeHandler)
            
            print "UB ", len(updates["UpdatedBoxes"])
            movingDBHandler.update_boxes_from_client(updates["UpdatedBoxes"], locationIDmap, timeHandler)
            
            print "DB ", len(updates["DeletedBoxes"])
            movingDBHandler.delete_boxes_from_client(updates["DeletedBoxes"], timeHandler)
            
            print "NI ", len(updates["NewItems"])
            itemIdMap  = movingDBHandler.create_items_from_client(updates["NewItems"], boxIdMap, timeHandler)

            print "UI ", len(updates["UpdatedItems"])
            movingDBHandler.update_items_from_client(updates["UpdatedItems"], boxIdMap, timeHandler)
            
            print "DI ", len(updates["DeletedItems"])
            movingDBHandler.delete_items_from_client(updates["DeletedItems"], timeHandler)
            
            response = {}
            response["Status"] = "OK"
            response["LocationIdMap"] = locationIDmap
            response["BoxIdMap"] = boxIdMap
            response["ItemIdMap"] = itemIdMap
        
            return json.dumps(response)
        except:
            return "ERROR"

           
if __name__ == "__main__": 
        print "Starting Moving Server @: "
        app.run()
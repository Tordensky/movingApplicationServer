import web
import json
import DbHandler
import TimeStampHandler


urls = (
        '/', 'index',
        '/login', 'login',
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
        movingDBHandler = DbHandler.DBhandler()
        #dbHandle = dbHandler.DBhandler()
        return json.dumps(movingDBHandler.get_boxes())
    

class login:
    def GET(self):
        return "Logged In"

class Updates:
    def GET(self, method_id):
        timeStamp = format(method_id)
        timeStamp = timeStamp.split('/')[0]
        movingDBHandler = DbHandler.DBhandler()
        
        message = {}
        message["TimeStamp"] = int(timeHandler.getTimeStamp())
        message["NewBoxes"] = movingDBHandler.get_boxes_created_after(int(timeStamp))
        message["UpdatedBoxes"] = movingDBHandler.get_boxes_updated_after(int(timeStamp))
        message["DeletedBoxes"] = movingDBHandler.get_boxes_deleted_after(int(timeStamp))
    
        return json.dumps(message)
    
    def POST(self, method_id):
                
        body = web.data()
        
        print "incoming post", body
        
        print "POST REQUEST"
        return MessageHandler().updateFromPost(body)
    
class Boxes:
    def GET(self, method_id):
        timeStamp = format(method_id)
        
        timeStamp = timeStamp.split('/')[0]
        movingDBHandler = DbHandler.DBhandler()
        
        message = {}
        message["timeStamp"] = int(timeHandler.getTimeStamp())
        message["boxes"] = movingDBHandler.get_boxes_after_time(int(timeStamp))
        
        return json.dumps(message);
    
    def POST(self):
        web.data();
        pass
    
class MessageHandler(object):
    def updateFromPost(self, data):
        try:
            updateDict = json.loads(data)
            
            print "New Boxes: ", updateDict["NewBoxes"]
            print "Updated Boxes: ", updateDict["UpdatedBoxes"]
            print "DeletedBoxes: ", updateDict["DeletedBoxes"] 
        
            return "OK"
        except:
            return "ERROR"
        # TODO return new BIDS
        
    
if __name__ == "__main__": 
        print "Starting Moving Server @: "
        app.run()
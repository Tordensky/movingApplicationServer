import web
import json
import DbHandler


urls = (
        '/', 'index',
        '/login', 'login',
        '/boxes' 'Boxes'
        )

app = web.application(urls, globals())

testMessage = [{"BoxName": "Mordi", "BoxDescription": "Fardi"}, {"BoxName": "Fett", "BoxDescription": "Funker"}];
#print testMessage

#movingDBHandler = DbHandler.DBhandler()

class index:
    def GET(self):
        movingDBHandler = DbHandler.DBhandler()
        #dbHandle = dbHandler.DBhandler()
        return json.dumps(movingDBHandler.get_boxes())
    

class login:
    def GET(self):
        return "Logged In"
    
class Boxes:
    def GET(self):
        
        return "BOXES"
    
    def POST(self):
        pass
    
if __name__ == "__main__": app.run()
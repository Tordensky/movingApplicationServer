import web
import json

urls = (
        '/', 'index',
        '/login', 'login'
        )

app = web.application(urls, globals())

testMessage = {"Boxes": "Works"};



class index:
    def GET(self):
        #dbHandle = dbHandler.DBhandler()
        return json.dumps(testMessage)
    

class login:
    def GET(self):
        return "Logged In"
    
if __name__ == "__main__": app.run()
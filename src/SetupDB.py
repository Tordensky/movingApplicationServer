import sqlite3
import json

class SetupDBhandler(object):
    def __init__(self):
        self.conn = sqlite3.connect('test.db');        
        self.setupDb()
            
    def setupDb(self):
        c = self.conn.cursor()
        
        c.execute('DROP TABLE if exists  Boxes')
        c.execute('DROP TABLE if exists  Items')
        c.execute('DROP TABLE if exists  Locations')
        
        # Create Boxes Table
        boxString = """ CREATE TABLE Boxes(
                            BID INTEGER, 
                            boxName TEXT, 
                            boxDescription TEXT, 
                            boxLocation INTEGER,
                            PRIMARY KEY(BID ASC)
                            )"""
        
        # Create Items table
        itemString = """ CREATE TABLE Items(
                            IID INTEGER, 
                            itemName TEXT, 
                            itemDescription TEXT, 
                            quantity INTEGER, 
                            boxID INTEGER, 
                            PRIMARY KEY(IID ASC) FOREIGN KEY(boxID) REFERENCES Boxes(BID) ON DELETE CASCADE
                            ) """
                            
        # Create Location table
        locationString = """ CREATE TABLE Locations (
                            LID INTEGER,
                            locationName TEXT,
                            PRIMARY KEY(LID ASC)
                            )"""
        
        print boxString 
        print itemString
        print locationString
        
        c.execute(boxString)
        c.execute(itemString)
        c.execute(locationString)
        
        
        
        # # # # # # # # #
        # Run some test queries with some test values
        # # # # # # # # #
        
        # Create some boxes
        c.execute('''INSERT INTO Boxes (boxName, boxDescription, boxLocation) VALUES ("Kitchen stuff", "Holds most of the kitchen stuff", 1)''')
        c.execute('''INSERT INTO Boxes (boxName, boxDescription, boxLocation) VALUES ("CD's", "The music collection", 2)''')
        c.execute('''INSERT INTO Boxes (boxName, boxDescription, BoxLocation) VALUES ("TV", "This is the actual TV", 3)''')
        
        # Create some Items
        #Kitchen box
        c.execute('INSERT INTO Items (itemName, itemDescription, quantity, boxID) VALUES ("Plates", "The old plates from grandma", 6, 1)')
        c.execute('INSERT INTO Items (itemName, itemDescription, quantity, boxID) VALUES ("Silver ware", "Forks, Spoons, Knifes", 24, 1)')
        c.execute('INSERT INTO Items (itemName, itemDescription, quantity, boxID) VALUES ("Big Pan", "The big old pan", 1, 1)')
        c.execute('INSERT INTO Items (itemName, itemDescription, quantity, boxID) VALUES ("Wine glasses", "", 6, 1)')
        
        c.execute('''INSERT INTO Items (itemName, itemDescription, quantity, boxID) VALUES ("Old cd's", "", 45, 2)''')
        
        c.execute('''INSERT INTO Items (itemName, itemDescription, quantity, boxID) VALUES ("RemoteControll", "", 1, 3)''')
        
        #Create some locations
        c.execute('INSERT INTO Locations (locationName) VALUES ("OldHome")')
        c.execute('INSERT INTO Locations (locationName) VALUES ("NewHome")')
        c.execute('INSERT INTO Locations (locationName) VALUES ("Depot")')
        
        c.execute('SELECT * FROM Items')
        print '\nAll items\n'
        for row in c:
            print row
            
        c.execute('SELECT boxName, itemName FROM Boxes, Items WHERE BID = boxID')
        print '\nAll boxes and there items\n'
        for row in c:
            print row
            
        c.execute('SELECT locationName, boxName FROM Locations, Boxes WHERE BoxLocation = LID')
        print '\nAll destinations and there boxes\n'
        for row in c:
            print row
            
        c.close()
        
        self.conn.commit()
        
if __name__ == "__main__": 
    dbtest = SetupDBhandler()




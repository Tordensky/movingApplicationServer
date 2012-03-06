import sqlite3
import json

def dict_factory(cursor, row):
    d = {}
    for idx,col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DBhandler(object):
    def __init__(self):
        self.conn = sqlite3.connect('test.db');        
        self.conn.row_factory = dict_factory
       
    
    def setupTestData(self):
        self.setupDb()
            
    def get_boxes(self):
        boxCursor = self.conn.cursor()
        boxCursor.execute('SELECT * FROM Boxes')
        
        itemCursor = self.conn.cursor()
        RowList = [];
        for box in boxCursor:
            BID = box["BID"]
            itemCursor.execute("SELECT * FROM Items WHERE "+str(BID)+" = boxID")
            itemList = []
            for item in itemCursor:
                itemList.append(item)
            box["items"] = itemList
            RowList.append(box)
            
        
        return RowList
    
    def get_boxes_with_items(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM Boxes')
        RowList = [];
        for row in c:
            print row["BID"]
            
            
            
            RowList.append(row)
        return RowList
        
            
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
        
        print self.get_boxes()
        
if __name__ == "__main__": 
    dbtest = DBhandler()
    dbtest.setupDb()




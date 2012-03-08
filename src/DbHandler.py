import sqlite3
import time
import TimeStampHandler

def dict_factory(cursor, row):
    d = {}
    for idx,col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_time():
    return time.strftime("%Y%m%d%H%M%S")



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
    
    
    def get_boxes_created_after(self, timeStamp):
        boxCursor = self.conn.cursor()
        boxCursor.execute("""   SELECT * FROM Boxes 
                                Where  boxCreated >= %d AND 
                                       boxDeleted == 0 
                                    """ % timeStamp);
        RowList = []
        for box in boxCursor:
            RowList.append(box)
        return RowList
    
    def get_boxes_updated_after(self, timeStamp):
        boxCursor = self.conn.cursor()
        boxCursor.execute("""   SELECT * FROM Boxes 
                                Where boxUpdated >= %d AND 
                                      boxCreated < %d AND
                                      boxDeleted == 0
                                      """ % (timeStamp, timeStamp));
        RowList = []
        for box in boxCursor:
            RowList.append(box)
        return RowList
    
    def get_boxes_deleted_after(self, timeStamp):
        boxCursor = self.conn.cursor()
        boxCursor.execute("""   SELECT * FROM Boxes 
                                Where  boxDeleted >= %d AND
                                       boxCreated <= %d
                                       """ % (timeStamp, timeStamp));
        RowList = []
        for box in boxCursor:
            RowList.append(box)
        return RowList
            
    def create_Box(self, boxName, boxDescription, boxLocationId, timeHandler):
        c = self.conn.cursor()
        c.execute("""   INSERT INTO Boxes (boxName, boxDescription, BoxLocation, boxCreated) 
                        VALUES ("%s", "%s", %d, %d)
                        """% (boxName,boxDescription, boxLocationId, int(timeHandler.getTimeStamp())))
        c.close()
        self.conn.commit()
        
    def update_Box(self, BID, boxName, boxDescription, boxLocationId, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Boxes
                        SET boxName = "%s", boxDescription = "%s", BoxLocation = %d, boxUpdated = %d
                        WHERE BID = %d 
                        """ % (boxName, boxDescription, boxLocationId, int(timeHandler.getTimeStamp()), BID))
        c.close()
        self.conn.commit()
            
    def delete_Box(self, BID, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Boxes
                        Set boxDeleted = %d
                        WHERE BID = %d
                        """ % (int(timeHandler.getTimeStamp()), BID))
        c.close()
        self.conn.commit()
         
    def putItem(self, itemName, itemDescription, boxID, timeHandler):
        c = self.conn.cursor()
        c.execute("""   INSERT INTO Items (itemName, itemDescription, boxID, itemUpdated) 
                        VALUES ("%s", "%s", %d, %d)
                        """% (itemName, itemDescription, boxID, int(timeHandler.getTimeStamp())))
        c.close()
        self.conn.commit()
    
    # TODO OLD METHOD REMOVE
    def get_boxes_after_time(self, time):
        boxCursor = self.conn.cursor()
        boxCursor.execute('SELECT * FROM Boxes Where boxUpdated >= %d' % time);
        itemCursor = self.conn.cursor()
        
        RowList = []
        for box in boxCursor:
            BID = box["BID"]
            
            itemCursor.execute("SELECT * FROM Items WHERE %d = boxID AND itemUpdated >= %d " % (BID, time))
            itemList = []
            for item in itemCursor:
                itemList.append(item)
            box["items"] = itemList
            RowList.append(box);
        return RowList
    
    # TODO OLD METHOD REMOVE
    def get_boxes_with_items(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM Boxes')
        RowList = [];
        for row in c:
            print row["BID"]
             
            RowList.append(row)
        return RowList
    
    
        
    # Setup a test db            
    def setupDb(self, timeHandler):
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
                            boxCreated INTEGER NOT NULL DEFAULT 0,
                            boxUpdated INTEGER NOT NULL DEFAULT 0,
                            boxDeleted INTEGER NOT NULL DEFAULT 0,
                            PRIMARY KEY(BID ASC)
                            )"""
        
        # Create Items table
        itemString = """ CREATE TABLE Items(
                            IID INTEGER, 
                            itemName TEXT, 
                            itemDescription TEXT, 
                            quantity INTEGER, 
                            boxID INTEGER,
                            itemUpdated INTEGER, 
                            PRIMARY KEY(IID ASC) FOREIGN KEY(boxID) REFERENCES Boxes(BID) ON DELETE CASCADE
                            ) """
                            
        # Create Location table
        locationString = """ CREATE TABLE Locations (
                            LID INTEGER,
                            locationName TEXT,
                            PRIMARY KEY(LID ASC)
                            )"""
                
        c.execute(boxString)
        c.execute(itemString)
        c.execute(locationString)
                    
        c.close()
        
        self.conn.commit()
    
    def createTestData(self, timeHandler):
        self.create_Box("Box 1", "This is a box", 0, timeHandler)
        self.create_Box("Box 2", "This is a box", 0, timeHandler)
        self.create_Box("Box 3", "This is a box", 0, timeHandler)
        self.create_Box("Box 4", "This is a box", 0, timeHandler)
        
        self.update_Box(1, "Box updated" , "Endra", 1, timeHandler)
        
        self.delete_Box(3, timeHandler)
        self.delete_Box(2, timeHandler)
        
        
        
if __name__ == "__main__": 
    dbtest = DBhandler()
    timeHandler = TimeStampHandler.TimeStampHandler()
    #dbtest.setupDb(timeHandler)
    #dbtest.createTestData(timeHandler)
    #dbtest.update_Box(1, "Arne", "Mordi", 1, timeHandler)
    #dbtest.delete_Box(4, timeHandler)
    dbtest.create_Box("This is a new box", "This is a box", 0, timeHandler)





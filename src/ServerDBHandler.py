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

## BOX START
    
    ''' Gets all boxes created after time stamp and the items in this box'''
    def get_boxes_created_after(self, timeStamp):
        boxCursor = self.conn.cursor()
        boxCursor.execute("""   SELECT * FROM Boxes 
                                Where  boxCreated >= %d AND 
                                       boxDeleted == 0 
                                    """ % timeStamp);
        RowList = []
        for box in boxCursor:
            box["NewItems"] = self.get_items_created_after(timeStamp)
            RowList.append(box)
        return RowList
    
    ''' Gets all boxes updated after time stamp '''
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
    
    ''' Gets all boxes deleted after time stamp '''
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
    
    
    ''' Creates a new box and returns BID '''        
    def create_Box(self, boxName, boxDescription, boxLocationId, timeHandler):
        c = self.conn.cursor()
        c.execute("""   INSERT INTO Boxes (boxName, boxDescription, BoxLocation, boxCreated) 
                        VALUES ("%s", "%s", %d, %d)
                        """% (boxName,boxDescription, boxLocationId, int(timeHandler.getTimeStamp())))
        
        BID = c.lastrowid
        print "  last BID:", BID 
        c.close()
        self.conn.commit()
        return BID
    
    ''' Updates boxName, boxDescription and boxLocation from BID '''    
    def update_Box(self, BID, boxName, boxDescription, boxLocationId, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Boxes
                        SET boxName = "%s", boxDescription = "%s", BoxLocation = %d, boxUpdated = %d
                        WHERE BID = %d 
                        """ % (boxName, boxDescription, boxLocationId, int(timeHandler.getTimeStamp()), BID))
        c.close()
        self.conn.commit()
    
    ''' Deletes box from BID'''        
    def delete_Box(self, BID, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Boxes
                        Set boxDeleted = %d
                        WHERE BID = %d
                        """ % (int(timeHandler.getTimeStamp()), BID))
        c.close()
        self.conn.commit()

## BOX END   
    
    def create_locations_from_client(self, new_locations, timeHandler):
        idMap = {}
        count = 0
        LID = 0
        for location in new_locations:
            count += 1
            LID = self.create_location(location["locationName"], location["locationDescription"], timeHandler)
            idMap[location["id"]] = LID
        print "Location id map", idMap
        return idMap
        
    ''' Update Boxes from Client'''
    def create_boxes_from_client(self, new_boxes, locationIdMap, timeHandler):
        idMap = {}
        count = 0
        BID = 0
        LID = 0
        for box in new_boxes:
            count += 1
            LID = int(box["LID"])
            
            if (box["localLID"] == 0):
                LID = 0
            else:    
                LID = locationIdMap[int(box["localLID"])]


            BID = self.create_Box(box["boxName"], box["boxDescription"], LID, timeHandler)
            idMap[box["id"]] = BID
        print "idMap", idMap
        return idMap
    
    # TODO WRONG WRONG WRONG
    def create_items_from_client(self, new_items, boxIdMap, timeHandler):
        idMap = {}
        count = 0
        BID = 0
        IID = 0
        for item in new_items:
            count += 1
            BID = int(item["BID"])
            
            if (item["localBID"] == 0):
                BID = 0
            else:
                BID = boxIdMap[item["localBID"]]
                
            IID = self.create_item(item["itemName"],item["itemDescription"], BID, timeHandler)
            idMap[item["id"]] = IID
        return idMap
## ITEMS START
    
    ''' Returns items created after given time stamp '''
    def get_items_created_after(self, timeStamp):
        c = self.conn.cursor()
        c.execute("""   SELECT * FROM Items 
                        Where  itemCreated >= %d AND 
                               itemDeleted == 0 
                        """ % timeStamp);
        RowList = []
        for item in c:
            RowList.append(item)
        c.close()    
        return RowList
    
    ''' Returns items updated after given time stamp '''
    def get_items_updated_after(self, timeStamp):
        c = self.conn.cursor()
        c.execute("""   SELECT * FROM Items 
                        Where itemUpdated >= %d AND 
                              itemCreated < %d AND
                              itemDeleted == 0
                        """ % (timeStamp, timeStamp));
        RowList = []
        for item in c:
            RowList.append(item)
        c.close()    
        return RowList
    
    ''' Returns items deleted after given time stamp '''
    def get_items_deleted_after(self, timeStamp):
        c = self.conn.cursor()
        c.execute("""   SELECT * FROM Items 
                        Where  itemDeleted >= %d AND
                               itemCreated <= %d
                        """ % (timeStamp, timeStamp));
        RowList = []
        for item in c:
            RowList.append(item)
        return RowList
    
    # TODO should return the new IID
    ''' Creates a new item, BID references owner box id'''        
    def create_item(self, itemName, itemDescription, BID, timeHandler):
        c = self.conn.cursor()
        c.execute("""   INSERT INTO Items (itemName, itemDescription, BID, itemCreated) 
                        VALUES ("%s", "%s", %d, %d)
                        """ % (itemName, itemDescription, BID, int(timeHandler.getTimeStamp())))
        
        
        IID = c.lastrowid
        print "    last IID:", IID 
        c.close()
        self.conn.commit()
        return IID
    
    ''' Updates item name and description from IID'''    
    def update_item(self, IID, newItemName, newItemDescription, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Items
                        SET itemName = "%s", itemDescription = "%s", boxUpdated = %d
                        WHERE IID = %d 
                        """ % (newItemName, newItemDescription, int(timeHandler.getTimeStamp()), IID))
        c.close()
        self.conn.commit()
    
    ''' Deletes item from IID'''        
    def delete_item(self, IID, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Item
                        Set itemDeleted = %d
                        WHERE IID = %d
                        """ % (int(timeHandler.getTimeStamp()), IID))
        c.close()
        self.conn.commit()

## ITEMS END        
## LOCATIONS START
    
    # TODO MOST ADD BOXES
    ''' Returns locations created after given time stamp '''
    def get_locations_created_after(self, timeStamp):
        c = self.conn.cursor()
        c.execute("""   SELECT * FROM Locations 
                        Where  locationCreated >= %d AND 
                               locationDeleted == 0 
                        """ % timeStamp);
        RowList = []
        for location in c:
            RowList.append(location)
        c.close()    
        return RowList
    

    ''' Returns locations updated after given time stamp '''
    def get_locations_updated_after(self, timeStamp):
        c = self.conn.cursor()
        c.execute("""   SELECT * FROM Locations 
                        Where locationUpdated >= %d AND 
                              locationCreated < %d AND
                              locationDeleted == 0
                        """ % (timeStamp, timeStamp));
        RowList = []
        for location in c:
            RowList.append(location)
        c.close()    
        return RowList
    

    ''' Returns locations deleted after given time stamp '''
    def get_locations_deleted_after(self, timeStamp):
        c = self.conn.cursor()
        c.execute("""   SELECT * FROM Locations 
                        Where  locationDeleted >= %d AND
                               locationCreated <= %d
                        """ % (timeStamp, timeStamp));
        RowList = []
        for location in c:
            RowList.append(location)
        return RowList
    

    ''' Creates a new location '''        
    def create_location(self, locationName, locationDescription, timeHandler):
        c = self.conn.cursor()
        c.execute("""   INSERT INTO Locations (locationName, locationDescription, locationCreated) 
                        VALUES ("%s", "%s", %d)
                        """ % (locationName, locationDescription, int(timeHandler.getTimeStamp())))
        
        LID = c.lastrowid
        print "last LID:", LID 
        c.close()
        self.conn.commit()
        return LID
    

    ''' Updates location name and description from IID'''    
    def update_location(self, LID, newLocationName, newLocationDescription, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Locations
                        SET locationName = "%s", locationDescription = "%s", locationUpdated = %d
                        WHERE LID = %d 
                        """ % (newLocationName, newLocationDescription, int(timeHandler.getTimeStamp()), LID))
        c.close()
        self.conn.commit()
    
    # TODO
    ''' Deletes item from IID'''        
    def delete_location(self, LID, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Locations
                        Set locationDeleted = %d
                        WHERE LID = %d
                        """ % (int(timeHandler.getTimeStamp()), LID))
        c.close()
        self.conn.commit()
        
## LOCATIONS END


    
    # TODO OLD REMOVE     
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
            
            itemCursor.execute("SELECT * FROM Items WHERE %d = BID AND itemUpdated >= %d " % (BID, time))
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
            
    ''' Setup for server DB '''            
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
                            BID INTEGER,
                            itemCreated INTEGER NOT NULL DEFAULT 0,
                            itemUpdated INTEGER NOT NULL DEFAULT 0,
                            itemDeleted INTEGER NOT NULL DEFAULT 0, 
                            PRIMARY KEY(IID ASC)
                            ) """
                            
        # Create Location table
        locationString = """ CREATE TABLE Locations (
                            LID INTEGER,
                            locationName TEXT,
                            locationDescription TEXT,
                            locationCreated INTEGER NOT NULL DEFAULT 0,
                            locationUpdated INTEGER NOT NULL DEFAULT 0,
                            locationDeleted INTEGER NOT NULL DEFAULT 0, 
                            PRIMARY KEY(LID ASC)
                            )"""
                
        c.execute(boxString)
        c.execute(itemString)
        c.execute(locationString)
                    
        c.close()
        
        self.conn.commit()
    
    ''' Helper function for creating some test data '''
    def createTestData(self, timeHandler):
        
        # TODO create test locations, test updates and deletes
        
        for locNum in range (3):
            locationName = "Location: " + str(locNum)
            locationDescription = "location " + str(locNum) + " description"            
            LID = self.create_location(locationName, locationDescription, timeHandler)
            
            for boxNum in range (5):
                boxName = "Box: " + str(boxNum)
                boxDescription = "box " + str(boxNum) + " description"
                BID = self.create_Box(boxName, boxDescription, LID, timeHandler)
                
                for itemNum in range (10):
                    itemName = "Item " +  str(itemNum)
                    itemDescription = "item from box: "+  str(boxNum)
                    self.create_item(itemName, itemDescription, BID, timeHandler)
        
        
        
        #self.update_Box(1, "Box updated" , "Endra", 1, timeHandler)
        
        #self.delete_Box(3, timeHandler)
        #self.delete_Box(2, timeHandler)
        
        
        
if __name__ == "__main__": 
    dbtest = DBhandler()
    timeHandler = TimeStampHandler.TimeStampHandler()
    #dbtest.setupDb(timeHandler)
    dbtest.createTestData(timeHandler)






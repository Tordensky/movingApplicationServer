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
            #box["NewItems"] = self.get_items_created_after(timeStamp)
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
    
    ''' Update boxes from Client '''
    def update_boxes_from_client(self, boxes, locationIdMap, timeHandler):
        LID = 0;
        for box in boxes:
            LID = self.remote_Id_to_local(box, "localLID", "LID", locationIdMap)                               
            self.update_Box(int(box["BID"]), box["boxName"], box["boxDescription"], LID, timeHandler)
    
            
    ''' Deletes box from BID'''        
    def delete_Box(self, BID, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Boxes
                        Set boxDeleted = %d
                        WHERE BID = %d
                        """ % (int(timeHandler.getTimeStamp()), BID))
        c.close()
        self.conn.commit()
    
    ''' Deletes boxes from Client '''    
    def delete_boxes_from_client(self, boxes, timeHandler):
        for box in boxes:
            self.delete_Box(int(box["BID"]), timeHandler)

## BOX END   
    def remote_Id_to_local(self, row, localIdName, IdName, idMap):        
        LOCAL_ID = int(row[IdName])
        if (LOCAL_ID > 0):
            pass
        elif (int(row[localIdName]) > 0):
            LOCAL_ID = idMap[int(row[localIdName])]
        else:    
            LOCAL_ID = 0
        return LOCAL_ID
    
    ''' Create new locations from client, return ID map'''
    def create_locations_from_client(self, new_locations, timeHandler):
        idMap = {}
        count = 0
        LID = 0
        for location in new_locations:
            count += 1
            LID = self.create_location(location["locationName"], location["locationDescription"], timeHandler)
            idMap[int(location["_id"])] = LID
        return idMap
        
    ''' Create new Boxes from Client'''
    def create_boxes_from_client(self, new_boxes, locationIdMap, timeHandler):
        idMap = {}
        count = 0
        BID = 0
        LID = 0
        for box in new_boxes:
            count += 1
            LID = self.remote_Id_to_local(box, "localLID", "LID", locationIdMap)

            BID = self.create_Box(box["boxName"], box["boxDescription"], LID, timeHandler)
            idMap[int(box["_id"])] = BID
        return idMap
    
    ''' Create new items from client, return ID map'''
    def create_items_from_client(self, new_items, boxIdMap, timeHandler):
        idMap = {}
        count = 0
        BID = 0
        IID = 0
        for item in new_items:
            count += 1
            BID = self.remote_Id_to_local(item, "localBID", "BID", boxIdMap)
                
            IID = self.create_item(item["itemName"],item["itemDescription"], BID, timeHandler)
            idMap[int(item["_id"])] = IID
        return idMap
    
    ''' Deletes items from Client '''    
    def delete_items_from_client(self, items, timeHandler):
        for item in items:
            self.delete_item(int(item["IID"]), timeHandler)
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
        c.close()
        self.conn.commit()
        return IID
    
    ''' Updates item name and description from IID'''    
    def update_item(self, IID, newItemName, newItemDescription, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Items
                        SET itemName = "%s", itemDescription = "%s", itemUpdated = %d
                        WHERE IID = %d 
                        """ % (newItemName, newItemDescription, int(timeHandler.getTimeStamp()), IID))
        c.close()
        self.conn.commit()
        
    ''' Update items from Client '''
    def update_items_from_client(self, items, boxIdMap, timeHandler):
        BID = 0;
        for item in items:
            BID = self.remote_Id_to_local(item, "localBID", "BID", boxIdMap)                               
            self.update_item(int(item["IID"]), item["itemName"], item["itemDescription"], BID, timeHandler)
    
    ''' Deletes item from IID'''        
    def delete_item(self, IID, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Items
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
        
    ''' Update location from Client '''
    def update_locations_from_client(self, locations, timeHandler):
        for location in locations:
            self.update_location(int(location["LID"]), location["locationName"], location["locationDescription"], timeHandler)                             

    # TODO
    ''' Deletes Location from LID'''        
    def delete_location(self, LID, timeHandler):
        c = self.conn.cursor()
        c.execute("""   UPDATE Locations
                        Set locationDeleted = %d
                        WHERE LID = %d
                        """ % (int(timeHandler.getTimeStamp()), LID))
        c.close()
        self.conn.commit()
        
    ''' Deletes locations from Client '''    
    def delete_locations_from_client(self, locations, timeHandler):
        for location in locations:
            self.delete_location(int(location["LID"]), timeHandler)
        
## LOCATIONS END
 
            
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

        boxNameNum = 0
        itemNameNum = 0
        
        for locNum in range (3):
            locationName = "Location: " + str(locNum)
            locationDescription = "location " + str(locNum) + " description"            
            LID = self.create_location(locationName, locationDescription, timeHandler)
            
            for boxNum in range (2):
                boxName = "Box: " + str(boxNameNum)
                boxDescription = "box " + str(boxNameNum) + " description"
                BID = self.create_Box(boxName, boxDescription, LID, timeHandler)
                boxNameNum += 1
                
                for itemNum in range (2):
                    itemName = "Item " +  str(itemNameNum)
                    itemDescription = "item from box: "+  str(itemNameNum)
                    self.create_item(itemName, itemDescription, BID, timeHandler)
                    itemNameNum += 1
        
    ''' Helper function for updating some test data '''    
    def createUpdates(self, timeHandler):
        for x in range(10):
            self.update_location(x, "UPDATED LOCATION", "UPDT LOC", timeHandler)
        
        for x in range (10):
            self.update_Box(x, "UPDATED2", "UPDATED2", 2, timeHandler);
            
        for x in range (100):
            self.update_item(x, "Updated item", "Updated Item", timeHandler)    

    ''' Helper function for deleting some test data '''    
    def deleteShit(self, timeHandler):
        for x in range(10):
            self.delete_location(x, timeHandler)
            
        for x in range(20):
            self.delete_item(x, timeHandler)
            
        for x in range(2):
                self.delete_Box(x, timeHandler)
        
               
if __name__ == "__main__": 
    dbtest = DBhandler()
    timeHandler = TimeStampHandler.TimeStampHandler()
    dbtest.setupDb(timeHandler)
    dbtest.createTestData(timeHandler)
    #dbtest.createUpdates(timeHandler)
    #dbtest.deleteShit(timeHandler)
    #dbtest.get_boxes_after_time(TimeStampHandler.TimeStampHandler().getTimeStamp())

    





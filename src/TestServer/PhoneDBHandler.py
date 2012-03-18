'''
Created on 7. mars 2012

@author: Simon_ny
'''
import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx,col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class DBHandler(object):
    def __init__(self):
        self.conn = sqlite3.connect('simPhoneDB.db')
        self.conn.row_factory = dict_factory
        
# BOXES HANDLER
    
    ''' Create a box. sets updated to true so this box is synced to server'''
    def create_Box(self, boxName, boxDescription, localLID = 0, LID = 0, boxCreated = 1, BID = 0):
        c = self.conn.cursor()
#    IF EXISTS (SELECT * FROM Table1 WHERE Column1='SomeValue')
#    UPDATE Table1 SET (...) WHERE Column1='SomeValue'
#    ELSE
#    INSERT INTO Table1 VALUES (...)
        c.execute("""SELECT * FROM Boxes Where BID = %d AND BID != 0""" % BID)
        data = c.fetchone()
        if data is None:


        
        
        
            c.execute("""   
                            INSERT INTO Boxes 
                            (BID, boxName, boxDescription, localLID, LID, Created) 
                            VALUES (%d, "%s", "%s", %d, %d, %d)
                            """ % (BID, boxName, boxDescription, localLID, LID, boxCreated))
            
            
    #        c.execute("""   INSERT INTO Boxes 
    #                        (BID, boxName, boxDescription, localLID, LID, Created) 
    #                        VALUES ("%d", "%s", "%s", %d, %d, %d)
    #                        """ % (BID, boxName, boxDescription, localLID, LID, boxCreated))
            c.close()
            self.conn.commit()
    
    ''' Creates boxes from list of box dicts '''
    def create_Boxes_from_list(self, boxList):
        count = 0
        for box in boxList:
            count += 1
            self.create_Box(box["boxName"], box["boxDescription"], int(box["boxLocation"]), 0, BID = int(box["BID"]), boxCreated = 0)  
    

        
    ''' Update box data, box identified by either BID(Remote ID on server OR rowID (local id))'''
    def update_Box(self, rowID,  boxName, boxDescription, BID = 0, boxLocation = 0, boxUpdated = 1):
        c = self.conn.cursor()
        c.execute("""   UPDATE Boxes
                        SET boxName = "%s", boxDescription = "%s", localLID = "%s", Updated = %d
                        WHERE BID = %d OR id = %d
                        """ % (boxName, boxDescription, boxLocation, boxUpdated, BID, rowID))        
        c.close()
        self.conn.commit()
        
    ''' Update boxes from list of box dicts '''
    def update_Boxes_from_list(self, boxList):
        count = 0
        for box in boxList:
            count += 1
            self.update_Box(0, int(box["BID"]), box["boxName"], box["boxDescription"], int(box["boxLocation"], 0)) 
        

            
    ''' Set box BId given from server after POSTING new boxes '''
    def set_box_bid(self, rowID, BID):
        c = self.conn.cursor()
        c.execute("""   UPDATE Boxes
                        SET BID = %d
                        WHERE id = %d
                        """ % (BID, rowID))
    
    ''' Set box BID's from dict'''
    def set_box_bids_from_dict(self, BidMap):
        for rowID in BidMap:
            self.set_box_bid(int(rowID), int(BidMap[rowID]))
        
    ''' Delete box from table'''    
    def delete_Box_Hard(self, rowID, BID):
        # TODO should delete items in this box Hard
        c = self.conn.cursor()
        c.execute("""   DELETE FROM Boxes
                        WHERE id = %d OR BID = %d
                        """ % (rowID, BID))
        c.close()
        self.conn.commit()  
        
    ''' Set box to deleted state, could not be deleted until synced with server '''
    def delete_Box_Soft(self, box_id):
        # TODO should delete items in this box soft
        c = self.conn.cursor()
        c.execute("""   UPDATE Boxes
                        SET Deleted = 1
                        WHERE id = %d
                        """ % (box_id))
        c.close()
        self.conn.commit()
        
    ''' Update boxes from list of box dicts '''
    def delete_Boxes_from_list(self, boxList):
        count = 0
        for box in boxList:
            count += 1
            self.delete_Box_Hard(0, int(box["BID"]))


# Boxes    
    ''' Get boxes created after last sync with server'''
    def get_boxes_created_after_last_sync(self):
        return self._get_created_after_last_sync("Boxes")
    
    ''' Get boxes updated after last sync with server'''
    def get_boxes_updated_after_last_sync(self):
        return self._get_updated_after_last_sync("Boxes")
    
    ''' Get boxes deleted after last sync with server'''
    def get_boxes_deleted_after_last_sync(self):
        return self._get_deleted_after_last_sync("Boxes")

# Items      
    ''' Get items created after last sync with server'''
    def get_items_created_after_last_sync(self):
        return self._get_created_after_last_sync("Items")
    
    ''' Get items updated after last sync with server'''
    def get_items_updated_after_last_sync(self):
        return self._get_updated_after_last_sync("Items")
    
    ''' Get items deleted after last sync with server'''
    def get_items_deleted_after_last_sync(self):
        return self._get_deleted_after_last_sync("Items")

# Locations    
    ''' Get items created after last sync with server'''
    def get_locations_created_after_last_sync(self):
        return self._get_created_after_last_sync("locations")
    
    ''' Get items updated after last sync with server'''
    def get_locations_updated_after_last_sync(self):
        return self._get_updated_after_last_sync("locations")
    
    ''' Get items deleted after last sync with server'''
    def get_locations_deleted_after_last_sync(self):
        return self._get_deleted_after_last_sync("locations")
    
    
    def _get_created_after_last_sync(self, table):
        c = self.conn.cursor() 
        c.execute('''   SELECT * 
                        FROM %s
                        Where (Created == 1 OR
                              (Created == 1 AND
                              Updated == 1)) AND
                              Deleted == 0  
                        ''' % (table))
        return self.result_to_list(c)
        
    
    def _get_updated_after_last_sync(self, table):
        c = self.conn.cursor() 
        c.execute("""   SELECT * 
                        FROM %s
                        WHERE Created = 0 AND
                              Updated = 1 AND
                              Deleted = 0  
                        """ % table)
        return self.result_to_list(c)
    
    def _get_deleted_after_last_sync(self, table):
        c = self.conn.cursor()
        c.execute("""   SELECT *
                        FROM %s
                        WHERE Created = 0 AND
                              Deleted = 1 
                        """ % table)
        return self.result_to_list(c)
    
    
    # TODO set BID, LID AND IID from result
    ''' Update data after sync '''
    def update_after_sync(self):
        self._reset_update_create_flags("Locations")
        self._reset_update_create_flags("Boxes")
        self._reset_update_create_flags("Items")
        
        self._delete_synced_records("Locations")
        self._delete_synced_records("Boxes")
        self._delete_synced_records("Items")
    
    ''' Set create and update flags to 0'''    
    def _reset_update_create_flags(self, table):
        c = self.conn.cursor()
        c.execute("""   UPDATE %s
                        SET Created = 0, Updated = 0
                        """ % (table))
        
    ''' Delete records from table where deleted = 1'''
    def _delete_synced_records(self, table):
        c = self.conn.cursor()
        c.execute("""   DELETE FROM %s
                        WHERE Deleted = 1
                        """ % (table))
        c.close()
        self.conn.commit()          
    
    ''' Takes DB cursor and returns list of rows'''
    def result_to_list(self, result):
        rowList = []
        for row in result:
            rowList.append(row)
        result.close()
        return rowList
    
    
    ''' Create Tables in DB'''
    def setupSimPhoneDB(self):
        c = self.conn.cursor()
        
        c.execute('DROP TABLE IF exists Locations')
        c.execute('DROP TABLE IF exists Boxes')
        c.execute('DROP TABLE IF exists Items')
        
        
        locationString = """
                        CREATE TABLE Locations (
                        id INTEGER,
                        LID INTEGER,
                        locationName TEXT,
                        locationDescription TEXT,
                        Created INTEGER NOT NULL DEFAULT 0,
                        Updated INTEGER NOT NULL DEFAULT 0,
                        Deleted INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY(id ASC)
                        )"""
        
        boxString = """ CREATE TABLE Boxes(
                        id INTEGER,
                        BID INTEGER, 
                        boxName TEXT, 
                        boxDescription TEXT, 
                        localLID INTEGER,
                        LID INTEGER,
                        Created INTEGER NOT NULL DEFAULT 0,
                        Updated INTEGER NOT NULL DEFAULT 0,
                        Deleted INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY(id ASC)
                        )"""
                        
        itemString = """CREATE TABLE Items(
                        id INTEGER,
                        IID INTEGER
                        itemName TEXT,
                        itemDescription TEXT,
                        BID INTEGER,
                        localBID INTEGER,
                        Created INTEGER NOT NULL DEFAULT 0,
                        Updated INTEGER NOT NULL DEFAULT 0,
                        Deleted INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY(id ASC)
                        )"""
        
        c.execute(locationString)
        c.execute(itemString)                    
        c.execute(boxString)
        c.close()
        self.conn.commit()
        
    def createTestData(self):
        
#        self.create_Box("TestBox", "TestBoxDescription")
#        self.create_Box("TestBox1", "TestBoxDescription1")
#        self.create_Box("TestBox2", "TestBoxDescription2")
#        self.create_Box("TestBox3", "TestBoxDescription3")
        self.update_Box(3, "Should be updated", "UPDATED DESCRIPTION")
        #self.delete_Box_Soft(3)


                
if __name__ == "__main__":
    self = DBHandler()
    self.setupSimPhoneDB()



    
    
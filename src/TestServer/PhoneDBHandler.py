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
    def create_Box(self, BID, boxName, boxDescription, boxLocation, boxCreated = 1):
        c = self.conn.cursor()
        c.execute("""   INSERT INTO Boxes 
                        (BID, boxName, boxDescription, boxLocation, boxCreated, boxDeleted) 
                        VALUES ("%d", "%s", "%s", %d, %d, %d)
                        """ % (BID, boxName, boxDescription, boxLocation, boxCreated, 0))
        c.close()
        self.conn.commit()
    
    ''' Creates boxes from list of box dicts '''
    def create_Boxes_from_list(self, boxList):
        count = 0
        for box in boxList:
            count += 1
            self.create_Box(int(box["BID"]), box["boxName"], box["boxDescription"], int(box["boxLocation"]), 0)  
    
        print "Created boxes: ", count 
        
    ''' Update box data, box identified by either BID(Remote ID on server OR rowID (local id))'''
    def update_Box(self, rowID, BID, boxName, boxDescription, boxLocation, boxUpdated = 1):
        c = self.conn.cursor()
        c.execute("""   UPDATE Boxes
                        SET boxName = "%s", boxDescription = "%s", boxLocation = "%s", BID = %d, boxUpdated = %d
                        WHERE BID = %d OR id = %d
                        """ % (boxName, boxDescription, boxLocation, BID, BID, rowID, boxUpdated))        
        c.close()
        self.conn.commit()
        
    ''' Update boxes from list of box dicts '''
    def update_Boxes_from_list(self, boxList):
        count = 0
        for box in boxList:
            count += 1
            self.update_Box(0, int(box["BID"]), box["boxName"], box["boxDescription"], int(box["boxLocation"], 0)) 
        
        print "Updated Boxes: ", count
            
    ''' Set box BId given from server after POSTING new boxes '''
    def set_box_bid(self, rowID, BID):
        c = self.conn.cursor()
        c.execute("""   UPDATE Boxes
                        SET BID = %d
                        """ % (BID))
        
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
                        SET boxDeleted = 1
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
        print "Deleted boxes: ", count
    
    ''' Get boxes created after last sync with server'''
    def get_boxes_created_after_last_sync(self):
        c = self.conn.cursor() 
        c.execute("""   SELECT * 
                        FROM Boxes
                        WHERE boxCreated == 1 OR
                              boxUpdated == 1 AND
                              boxDeleted == 0  
                        """)
        boxList = []
        for box in c:
            boxList.append(box) 
        c.close()
        return boxList
    
    ''' Get boxes updated after last sync with server'''
    def get_boxes_updated_after_last_sync(self):
        c = self.conn.cursor() 
        c.execute("""   SELECT * 
                        FROM Boxes
                        WHERE boxCreated == 0 AND
                              boxUpdated == 1 AND
                              boxDeleted == 0  
                        """)
        boxList = []
        for box in c:
            boxList.append(box) 
        c.close()
        return boxList
    
    ''' Get boxes deleted after last sync with server'''
    def get_boxes_deleted_after_last_sync(self):
        c = self.conn.cursor() 
        c.execute("""   SELECT * 
                        FROM Boxes
                        WHERE boxCreated == 0 AND
                              boxDeleted == 1  
                        """)
        boxList = []
        for box in c:
            boxList.append(box) 
        c.close()
        return boxList
    
    ''' Create Tables in DB'''
    def setupSimPhoneDB(self):
        c = self.conn.cursor()
        
        c.execute('DROP TABLE IF exists Boxes')
        
                # Create Boxes Table
        boxString = """ CREATE TABLE Boxes(
                        id INTEGER,
                        BID INTEGER, 
                        boxName TEXT, 
                        boxDescription TEXT, 
                        boxLocation INTEGER,
                        boxCreated INTEGER NOT NULL DEFAULT 0,
                        boxUpdated INTEGER NOT NULL DEFAULT 0,
                        boxDeleted INTEGER NOT NULL DEFAULT 0,
                        PRIMARY KEY(id ASC)
                        )"""
                            
        c.execute(boxString)
        c.close()
        self.conn.commit()
        
    def createTestData(self):
        
        self.create_Box(0, "TestBox", "TestBoxDescription", 0)
        self.create_Box(0, "TestBox1", "TestBoxDescription1", 0)
        self.create_Box(0, "TestBox2", "TestBoxDescription2", 0)
        self.create_Box(0, "TestBox3", "TestBoxDescription3", 0)
        self.delete_Box_Soft(1)
        self.delete_Box_Soft(2)

                
if __name__ == "__main__":
    self = DBHandler()
    #self.setupSimPhoneDB()
    self.createTestData()

    
    
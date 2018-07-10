import os
import sqlite3
class CBMDefaultsInterface(object):

    def __init__(self, sqlitePath, createNew=True):
        if createNew and os.path.exists(sqlitePath):
            os.remove(sqlitePath)
        self.conn = sqlite3.connect(sqlitePath)
        self.cur = self.conn.cursor()
        self.sqlitePath = sqlitePath
    
    def executeDDLFile(self, ddlPath):
        with open(ddlPath, 'r') as ddlfile:
            for ddl in [x for x in ddlfile.read().split(";") if x is not None]:
                self.cur.execute(ddl)

    def commitChanges(self):
        self.conn.commit()
        self.conn.close()
       
    def add_record(self, table_name, **kwargs):

        record_values = kwargs
        col_list = kwargs.keys()

        query = "INSERT INTO {table_name} ({col_list}) VALUES ({values})" \
            .format(
                table_name=table_name,
                col_list=",".join(col_list),
                values=",".join(["?"]*len(col_list))
            )
        params = [kwargs[k] for k in col_list]
        self.cur.execute(query, params)
            

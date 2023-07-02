from sqlalchemy import create_engine, text
import openpyxl as xl
import os
import uuid

def make_count_sheet(catagory, site, sloc, file):
    db_connection_string = "mysql+pymysql://rct26osfx6yxi9ml2tf6:pscale_pw_3GezCF2721gQEt3DZL9oYDrSgiXarePZDbLe5MyYrRN@aws.connect.psdb.cloud/inventory?charset=utf8mb4"
    # mecl_db_connection_string = "mysql+pymysql://mec_wh"
    engine = create_engine(
        db_connection_string, 
        connect_args={
        "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"
        }
        })
    tbl_name = uuid.uuid4()
    tbl_name= str(tbl_name)
    tbl_name = tbl_name.split('-')
    tbl_name = "tmp_tbl_"+tbl_name[0]

    with engine.connect() as conn:
        result = conn.execute(text("CREATE TABLE "+tbl_name+" AS SELECT * FROM inventory."+str(file)+" where Site = '"+str(site)+"' and Category ='"+str(catagory)+"' and Sloc ='"+str(sloc)+"'"))
        
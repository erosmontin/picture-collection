o={
    "picture_table_name":"MyPhotos",
    "sqlite3_db_name":None
}
import json
import os

CFGFILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.json')
with open(CFGFILE, 'w') as f:
    json.dump(o, f)
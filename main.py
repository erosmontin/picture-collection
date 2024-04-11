import pynico_eros_montin.pynico as pn
import imghdr

from PIL import Image,TiffImagePlugin

TRUSTED_DEVICES = ['ilce-5000','pixel 4','pixel 6']
STD_DEVICES = ['ilce-5000','pixel 4','pixel 6']

def fixDict(O):
    if isinstance(O,dict):
        for k,v in O.items():
            if isinstance(v,bytes):
                O[k]=v.decode('utf-8')
            if isinstance(v,tuple):
                O[k]=[float(l) for l in list(v)]
            if isinstance(v,dict):
                O[k]=fixDict(v)
            if isinstance(v,TiffImagePlugin.IFDRational):
                O[k]=float(v)
    return O
def isImage(file):
    Image_file_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp','tif']
    if any(file.endswith(extension.lower()) for extension in Image_file_extensions):
        if imghdr.what(file) is not None:
            return True
        else:
            return False
    else:
        return False

def isVideo(filename):
    video_file_extensions = ['.mp4', '.avi', '.mov', '.flv', '.mkv', '.wmv']
    return any(filename.endswith(extension.lower()) for extension in video_file_extensions)

from PIL import Image
from PIL.ExifTags import TAGS as _TAGS
import PIL
from pymediainfo import MediaInfo


def getMediaInfo(file):
    media_info = MediaInfo.parse(file)

    tags = {}
    for track in media_info.tracks:
        tags[track.track_type] = track.to_data()
    return tags
def getExif(file):
    # Open the image
    tags={}
    if isImage(file):
        img = Image.open(file)
        # Get the EXIF data
        exif_data=img._getexif()
        tags= {_TAGS.get(tag): value for tag, value in exif_data.items() if tag in _TAGS and isinstance(_TAGS.get(tag), str)}
        tags.update(getMediaInfo(file))
    elif isVideo(file):
        media_info = MediaInfo.parse(file)
        for track in media_info.tracks:
            tags[track.track_type] = track.to_data()
    return fixDict(tags)

def getImageSource(file,exif=None):
    if exif is None:
        exif=getExif(file)
    # Check if the image was taken with a Sony camera
    if 'Make' in exif:
        return exif['Model'].lower()
    return 'other'

def fixDate(O,file=None,exif=None):
    # Split the date and time
    if exif is None:
        exif=getExif(file)
    # Check
    model=getImageSource(file,exif)
    if model in STD_DEVICES:
        date, time = O.split(' ')
        # Split the date into year, month and day
        year, month, day = date.split(':')
        # Split the time into hour, minute and second
        hour, minute, second = time.split(':')
        # Return the date in the format YYYY-MM-DD HH:MM:SS
    return {'Y':year,
            'M':month,
            'D':day,
            'h':hour,
            'm':minute,
            's':second
    }
def getDate(file,exif=None  ):
    # Get the EXIF data
    if exif is None:
        exif = getExif(file)
    # Check if the EXIF data contains the date the picture was taken
    O=None
    
    if 'DateTimeOriginal' in exif:
        O= exif['DateTimeOriginal']
    elif 'DateTime' in exif and O is None:
        O= exif['DateTime']
    elif 'DateTimeDigitized' in exif and O is None:
        O= exif['DateTimeDigitized']
    else:
        return None
    return fixDate(O,file,exif)
    
from datetime import datetime
    
def getDateUTF(date_string):

    date = datetime.strptime(date_string, 'UTC %Y-%m-%d %H:%M:%S')
    year = date.year
    month = date.month
    day = date.day
    hour = date.hour
    minute = date.minute
    second = date.second
    
    return {'Y':year,
            'M':month,
            'D':day,
            'h':hour,
            'm':minute,
            's':second
    }



def getShotDate(file,exif=None,device=None):
    # Get the EXIF data
    if exif is None:
        exif = getExif(file)
    # Check if the EXIF data contains the date the picture was taken
    if device is None:
        device = getImageSource(file,exif=exif)
    if device in TRUSTED_DEVICES:
        return getDate(file,exif=exif)
    
def copyfile(INF,OUTF,DELETE,TAGS,conn,config):
    cur=conn.cursor()       
    md5=pn.calculateMd5(INF)
    # Execute the query
    cur.execute(f"SELECT * FROM {config['picture_table_name']} WHERE md5 = ?", (md5,))
    # Fetch the result
    result = cur.fetchall()
    if len(result)>0:
        print("File already exists")
    else:
        print("File does not exist")

        O=pn.securecopy(INF,OUTF,delete_after_copy=DELETE,md5=md5)

        if O["status"]=="ok":
            #update the database
            FN=os.path.basename(INF)
            # Convert the TAGS JSON object to a string
        tags_str = json.dumps(TAGS)

# Insert the data into the table
        cur.execute(f"INSERT INTO '{config['picture_table_name']}' (name, path, md5, tags) VALUES (?, ?, ?, ?)",
            (FN, OUTPT, O['md5'], tags_str))
        print("done")
        conn.commit()
    
    
    
if __name__=="__main__":
    import argparse

    # Create the parser
    parser = argparse.ArgumentParser(description="Copy images")

    # Add the arguments
    parser.add_argument('--in','-i', type=str, help='The input file',dest="INF")
    parser.add_argument('--db','-d', type=str, help='sqlite Databse input file',dest="DB",default=None)
    # parser.add_argument('--out','-o', type=str, help='The output file',dest="OUTF")
    parser.add_argument('--outdir', type=str, help='The output directory',dest="OUTPT",default=None)
    parser.add_argument('--indir', type=str, help='The input directory',dest="INPT",default=None)
    parser.add_argument('--delete', default=False, action=argparse.BooleanOptionalAction,dest="DELETE")
    parser.add_argument('--dateorder', default=False, action=argparse.BooleanOptionalAction,dest="DATEORDER")
    parser.add_argument('--tags', nargs='*', help='Tags for the picture',default=None,dest="TAGS")
    parser.add_argument('--conf','-c', default=None, type=str,dest="CONF")


    # Parse the arguments
    args = parser.parse_args()
    #use argpars instead
    
    INF=args.INF
    DELETE=args.DELETE
    DB=args.DB
    OUTPT=args.OUTPT
    INPT=args.INPT
    TAGS=args.TAGS
    DATEORDER=args.DATEORDER
import json
import os
import json
import sqlite3

os.makedirs(OUTPT, exist_ok=True)
if args.CONF is None:
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    args.CONF = os.path.join(current_file_path, 'config.json')
    # Load the configuration file
with open(args.CONF, 'r') as f:
    config = json.load(f)
    # Update the arguments

if OUTPT is None:
    print("You must provide an output file or directory")
    exit(1)
if INF is None and INPT is None:
    print("You must provide an input file or directory")
    exit(1)

# Connect to the SQLite DB
if DB is None:
    # Create a new one
    if config["sqlite3_db_name"] is None:
        DB = os.path.join(OUTPT,'new_database.db')
        #update the config file
        config["sqlite3_db_name"] = DB
        with open(args.CONF, 'w') as f:
            json.dump(config, f)
    else:
        DB = config["sqlite3_db_name"]
                                    
if not os.path.exists(DB):
    with open(DB, 'w') as f:
        pass
    
    
                 
conn = sqlite3.connect(DB)

cur = conn.cursor()
# Execute the query

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (config['picture_table_name'],))
result = cur.fetchall()

    # Check if the table exists
if len(result)>0:
    print("Table 'picture_collection' exists.")
else:
    cur.execute(f'''
        CREATE TABLE {config["picture_table_name"]} (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            "md5" TEXT NOT NULL,
            "tags" TEXT
        );
    ''')
    print("Table 'picture_collection' does not exist.")


import glob
LIST= glob.glob(INPT+"/*")
for INF in LIST:
    tags={"common":TAGS}
    name=os.path.basename(INF)
    if DATEORDER:
        try:
            if isImage(INF):
                exif=getExif(INF)
                DATE=getShotDate(INF,exif=exif)
                tags.update(exif)
            if isVideo(INF):
                exif=getExif(INF)
                DATE=getDateUTF(exif["Video"]["encoded_date"])
                tags.update(fixDict(exif))   
                for k,v in DATE.items():
                    if v<100:
                        DATE[k]=f'{v:02d}'
                    else:
                        DATE[k]=str(v)
            if not DATE is None:
                _OUTPT=os.path.join(OUTPT,DATE['Y'],DATE['M'],DATE['D'])
                os.makedirs(_OUTPT, exist_ok=True)
                name=DATE['h']+"_"+DATE['m']+"_"+DATE['s'] + "_" + name
            else:
                print(f"No date found can't handle the file {INF}")
                continue        
            OUTF=os.path.join(_OUTPT,name)
        except:
            print(f"Can't handle the file {INF}")
            continue
    else:
        OUTF=os.path.join(OUTPT,name)
    copyfile(INF= INF,OUTF=OUTF,DELETE=DELETE,TAGS=tags,conn=conn,config=config)
conn.close()
    
    

   def get_date_taken(self):
        try:
            return Image.open(self.location)._getexif()[36867]
        except:
            return None
    def get_date_taken1(self):
        try:
            im= Image.open(self.location)
            exif = im.getexif()
            exif["DateTimeOriginal"]
        except:
            return None

    def get_date_taken0(self):
        try:
            im= Image.open(self.location)
            exif = im.getexif()
            exif["DateTimeDigitized"]
        except:
            return None
 
    def get_date_from_filename(self):
        datetime_object='0'
        f=re.findall(r'\d+', self.filename)
        try:
            if len(f)==1:
                if len(f[0])>8:
                    datetime_object = datetime.datetime.strptime(str(f[0][0:8])+" 000000", '%Y%m%d %H%M%S')
                else:
                    datetime_object = datetime.datetime.strptime(str(f[0])+" 000000", '%Y%m%d %H%M%S')
            if len(f)==2:
                datetime_object = datetime.datetime.strptime(str(f[0])+" "+str(f[1]), '%Y%m%d %H%M%S')
            if len(f)==3:
                datetime_object = datetime.datetime.strptime(str(f[0])+" "+str(f[1][0:6]), '%Y%m%d %H%M%S')
            if len(f)==4:
                datetime_object = datetime.datetime.strptime(str(f[0])+" "+str(f[1][0:6]), '%Y%m%d %H%M%S')
            if len(f)==6: 
                datetime_object = datetime.datetime.strptime(str(f[0])+str(f[1])+str(f[2])+" "+str(f[3])+str(f[4])+str(f[5]), '%Y%m%d %H%M%S')
            if len(f)==7:
                datetime_object = datetime.datetime.strptime(str(f[0])+str(f[1])+str(f[2])+" "+str(f[3])+str(f[4])+str(f[5]), '%Y%m%d %H%M%S')
            return datetime_object.strftime(date_formart)            
        except:
            return None
  
    def getAllExifs(self):
        try:
            img = Image.open(self.location)
            return  { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if (k in ExifTags.TAGS) & (not isBinary(v)) }
        except:
            return None
    def getAllExifsLabels(self):
        try:
            img = Image.open(self.location)
            return  { ExifTags.TAGS[k] for k in ExifTags.TAGS }
        except:
            return None
    def getFileCreationDate(self):
        try:
            return datetime.datetime.fromtimestamp(os.path.getctime(self.location)).strftime('%Y:%m:%d %H:%M:%S')
        except:
            return None
    def getFileModificationDate(self):
        try:
            return datetime.datetime.fromtimestamp(os.path.getmtime(self.location)).strftime('%Y:%m:%d %H:%M:%S')
        except:
            return None
        
  
def plausableDate(dt):
    MINY=1995
    plausable=True
    #transform indatetimem obj
    datetime_object = datetime.datetime.strptime(dt,date_formart)
    if(datetime_object.hour>23):
        datetime_object=datetime_object.replace(hour=23)
    if(datetime_object.year<MINY | datetime_object.year>2100):
        datetime_object=datetime_object.replace(year=1000)
        plausable=False
    return datetime_object.strftime(date_formart),plausable


def getCreationDate(self):
    date=None
    p=False #date is not plausable
    try:
        info =self.getAllExifs()
    except:
        info={}
    
    try:
        date,p=plausableDate(self.get_date_taken())
    except:
        try:
            date,p=plausableDate(self.get_date_taken0())    
        except:
            try:
                date,p=plausableDate(self.get_date_taken1())    
            except:
                try:
                    date,p=plausableDate(self.get_date_from_filename())    
                except:
                    try:
                        if self.intialGuessDate is None:
                    
                            date,p=plausableDate(self.getFileModificationDate())    
                            # print('creation date ') 
                    except:
                        try:
                            if self.intialGuessDate is None:
                                # print('modified date guess') 
                                date,p=plausableDate(self.getFileCreationDate())
                                # print('modified date!') 
                        except:
                            s="do nothing"
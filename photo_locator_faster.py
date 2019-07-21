#!/usr/bin/env python

#todo: downsize images for icons if it becomes clear that smaller file sizes help with the memory consumption of google earth pro
from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS
import datetime, sys, os
import subprocess
import pyexiftool
Image.MAX_IMAGE_PIXELS = None #for "decompression bomb DOS attack" error. very safe.

#EXIF -> LAT + LONG FUNCTIONS
def get_decimal_from_dms(dms, ref): #turn degrees minutes seconds to decimal

    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)

def get_coords_from_geotag(geotags): #return the latitude and longitude from GPS data
    lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])
    lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])

    return (lat,lon)

def get_coordinates(directory,filename,exiftool): #extract only the gps data from exif
    mov_time = datetime.datetime.now()
    if filename.lower().endswith(".mov"): #we got a movie on our hands, can't use pillow
        print("using exiftool on ", filename)
        # result = subprocess.run(['exiftool', '-GPSLatitude#', os.path.join(directory,filename)], stdout=subprocess.PIPE)
        result = exiftool.get_metadata(os.path.join(directory,filename))
        latitude = result.get('Composite:GPSLatitude',0)
        longitude = result.get('Composite:GPSLongitude',0)
        date = result.get('QuickTime:CreateDate','')

        mov_time1 = datetime.datetime.now()
        print("movie processing: ",(mov_time1-mov_time).total_seconds())
        return {'coords':(latitude,longitude), 'date':date}
    else:
        #get exif
        image = Image.open(os.path.join(directory,filename))
        image.verify()
        exif = image._getexif()
        if not exif:
            print("No EXIF metadata found found. Skipping ", filename)
            return {'coords':(0,0), 'date':''}

        #get geotagging
        geotagging = {}
        for (idx, tag) in TAGS.items():
            if tag == 'GPSInfo':
                if idx not in exif:
                    print("No EXIF geotagging found. Skipping ", filename)
                    return {'coords':(0,0), 'date':''}
                for (key, val) in GPSTAGS.items():
                    if key in exif[idx]:
                        geotagging[val] = exif[idx][key]
            if tag == 'DateTimeOriginal':
                if idx not in exif:
                    print("No EXIF Date found.")
                    date = ''
                else:
                    date = exif[idx]
        img_time = datetime.datetime.now()
        print("image processing: ",(img_time-mov_time).total_seconds())
        return {'coords':get_coords_from_geotag(geotagging),'date':date}

#KML stuff
header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
	<name>pte pics</name>
	<open>1</open>


    <!-- FOR VIDEOS -->
    <StyleMap id="msn_icon">
		<Pair>
			<key>normal</key>
			<styleUrl>#sn_icon</styleUrl>
		</Pair>
		<Pair>
			<key>highlight</key>
			<styleUrl>#sh_icon</styleUrl>
		</Pair>
	</StyleMap>

	<Style id="sn_icon">
        <LabelStyle>
            <scale>0</scale>
        </LabelStyle>
		<IconStyle>
			<scale>1.1</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/paddle/go.png</href>
			</Icon>
			<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
		</IconStyle>
		<BalloonStyle>
		</BalloonStyle>
		<ListStyle>
			<ItemIcon>
				<href>http://maps.google.com/mapfiles/kml/paddle/go-lv.png</href>
			</ItemIcon>
		</ListStyle>
	</Style>

	<Style id="sh_icon">
		<IconStyle>
			<scale>1.3</scale>
			<Icon>
				<href>http://maps.google.com/mapfiles/kml/paddle/go.png</href>
			</Icon>
			<hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
		</IconStyle>
		<BalloonStyle>
		</BalloonStyle>
		<ListStyle>
			<ItemIcon>
				<href>http://maps.google.com/mapfiles/kml/paddle/go-lv.png</href>
			</ItemIcon>
		</ListStyle>
	</Style>

    <!-- FOR IMAGES -->
    <StyleMap id="msn_icon_img">
        <Pair>
            <key>normal</key>
            <styleUrl>#sn_icon_img</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#sh_icon_img</styleUrl>
        </Pair>
    </StyleMap>

    <Style id="sn_icon_img">
        <LabelStyle>
            <scale>0</scale>
        </LabelStyle>
        <IconStyle>
            <scale>1.1</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png</href>
            </Icon>
            <hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
        </IconStyle>
        <BalloonStyle>
        </BalloonStyle>
        <ListStyle>
            <ItemIcon>
                <href>http://maps.google.com/mapfiles/kml/paddle/ylw-stars-lv.png</href>
            </ItemIcon>
        </ListStyle>
    </Style>

    <Style id="sh_icon_img">
        <IconStyle>
            <scale>1.3</scale>
            <Icon>
                <href>http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png</href>
            </Icon>
            <hotSpot x="32" y="1" xunits="pixels" yunits="pixels"/>
        </IconStyle>
        <BalloonStyle>
        </BalloonStyle>
        <ListStyle>
            <ItemIcon>
                <href>http://maps.google.com/mapfiles/kml/paddle/ylw-stars-lv.png</href>
            </ItemIcon>
        </ListStyle>
    </Style>
"""
thumbnail = """
<!-- Each thumbnail (needs) a StyleMap, Style with scale 1.1, Style with Scale 1.3 -->
<StyleMap id="msn_%(filename)s"> <!-- m for map -->
    <Pair>
        <key>normal</key>
        <styleUrl>#sn_%(filename)s</styleUrl> <!-- n for normal -->
    </Pair>
    <Pair>
        <key>highlight</key>
        <styleUrl>#sh_%(filename)s</styleUrl> <!-- h for higlight -->
    </Pair>
</StyleMap>
<Style id="sn_%(filename)s">
    <IconStyle>
        <scale>1.1</scale>
        <Icon>
            <href>file://%(directory)s/%(filename)s</href>
        </Icon>
    </IconStyle>
</Style>
<Style id="sh_%(filename)s">
    <IconStyle>
        <scale>1.3</scale>
        <Icon>
            <href>file://%(directory)s/%(filename)s</href>
        </Icon>
    </IconStyle>
</Style>
"""

placemark = """<!-- add placemarks -->
<Placemark>
    <name>%(date)s</name>
    <description>
        <![CDATA[
            %(description)s
            <a href="file://%(directory)s/%(filename)s">%(filename)s</a>
          <img style="max-width:500px;" src="file://%(directory)s/%(filename)s">
        ]]>
    </description>
    <LookAt>
        <longitude>%(longitude)f</longitude>
        <latitude>%(latitude)f</latitude>
        <altitude>0</altitude>
        <heading>-4.203478555548052e-07</heading>
        <tilt>0</tilt>
        <range>2805632.763722554</range>
        <gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
    </LookAt>
    <styleUrl>#msn_icon_img</styleUrl> <!-- use filename if you're creating thumbnails -->
    <Point>
        <gx:drawOrder>1</gx:drawOrder>
        <coordinates>%(longitude)f,%(latitude)f,0</coordinates>
    </Point>
</Placemark>
"""
placemark_mov = """<!-- add placemarks -->
<Placemark>
    <name>%(date)s</name>
    <description>
        <![CDATA[
            %(description)s
            <a href="file://%(directory)s/%(filename)s">%(filename)s</a>
          <div style="width:500px;height:400px">
            <video style="max-width:500px;" controls>
                <source src="file://%(directory)s/%(filename)s" type="video/mp4">
            </video>
          </div>
        ]]>
    </description>
    <LookAt>
        <longitude>%(longitude)f</longitude>
        <latitude>%(latitude)f</latitude>
        <altitude>0</altitude>
        <heading>-4.203478555548052e-07</heading>
        <tilt>0</tilt>
        <range>2805632.763722554</range>
        <gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>
    </LookAt>
    <styleUrl>#msn_icon</styleUrl>
    <Point>
        <gx:drawOrder>1</gx:drawOrder>
        <coordinates>%(longitude)f,%(latitude)f,0</coordinates>
    </Point>
</Placemark>
"""
footer = """</Document>
</kml>
"""
# finding all files in directory NOT RECURSIVE, check out this for files within subdirs: https://stackoverflow.com/questions/10377998/how-can-i-iterate-over-files-in-a-given-directory

# python photo_locator.py 'directory'
if len(sys.argv) > 1:
    directory = sys.argv[1]
else:
    directory = null
    print('error, need directory name')
directory_in_bytes = os.fsencode(directory)

# make an ExifTool
exiftool = pyexiftool.ExifTool()
exiftool.start()

# writing file
f = open(('%s/ptepics%s.kml'%(directory,str(datetime.datetime.now()).replace(':', '-'))),'w')
f.write(header)

for file in os.listdir(directory_in_bytes):
     filename = os.fsdecode(file)
     if filename.lower().endswith(".jpg") or filename.lower().endswith(".mov"):
         coord_dict= get_coordinates(directory,filename,exiftool)
         latitude = coord_dict['coords'][0]
         longitude = coord_dict['coords'][1]
         if ((latitude == 0) and (longitude == 0)):
             continue
         image_data = {
             'filename': filename,
             'description': '', #if there is a description use </br> at end
             'directory': os.path.realpath(directory),
             'longitude': longitude,
             'latitude': latitude,
             'date':coord_dict['date']
         }
         # print("writing xml data for %s", filename)
         if (filename.lower().endswith(".mov")):
             f.write(placemark_mov%image_data)
         else:
             # f.write(thumbnail%image_data)
             f.write(placemark%image_data)
         continue
     else:
         print("skipping ", filename)
         continue
f.write(footer)
f.close()

exiftool.terminate()
print("🦉")

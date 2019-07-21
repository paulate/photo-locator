# photo-locator
 Show location of photos on goog earth; makes a kml file from directory of photos and videos

 ![what it looks like](image.png)

## Usage:
In terminal, running `python photo_locator_faster.py '[directory]'` will create a kml file in that directory of all photos and videos that have GPS metadata.
Open the .kml file in a kml viewer like Google Earth; placemarks show where the photos/videos are located. You can view the media by clicking on the placemarks.

## Requires:
* http://github.com/smarnach/pyexiftool
* Pillow `pip install Pillow`
* exiftool in terminal `brew install exiftool`

## File info:
* photo_locator_faster.py: uses generic icons as placemarks.
* photo_locator.py: uses the actual image file as placemark icons. If you have more than a handful of images, viewing these on Google Earth will slowly consume
your computer's entire memory. :D

## Known wrongs:
* Create thumbnail versions of the images to use as placemark icons to fix the memory issue.

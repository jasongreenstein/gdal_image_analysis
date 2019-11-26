"""
jason_lab4.py

Purpose: This script is for GIS 663 lab 4. It classifies an image using the minimum
         distance method.

Author: Jason Greenstein
"""
#import modules
import numpy, math, sys, gdal, gdalconst, csv

#read parameters
inputImg = sys.argv[1]
inputTxt = sys.argv[2]
outputImg = sys.argv[3]

#### 1 - Read the row/col numbers of seeds from the text file

seedPixels = []                                     #list to store seed pixels

with open(inputTxt) as txtfile:
    csv_reader = csv.reader(txtfile, delimiter=',')
    header = next(csv_reader)
    for line in csv_reader:
        seedPixels.append(line)



##### 2 - Read the image file and store the data in a numpy matrix

inImg = gdal.Open(inputImg, gdalconst.GA_ReadOnly)
if inImg is None:
    print ("Cannot access the image file!\n")
    sys.exit(0)

projection = inImg.GetProjection()
transformation = inImg.GetGeoTransform()
colNum = inImg.RasterXSize
rowNum = inImg.RasterYSize
bandNum = inImg.RasterCount


imgData = numpy.zeros((rowNum,colNum,bandNum),dtype=numpy.int64)

for iband in range(bandNum):
    imgBand = inImg.GetRasterBand(iband+1)
    imgData[:,:,iband] = imgBand.ReadAsArray(0,0,colNum,rowNum)

##### 4 - Create a numpy matrix to hold the output classification
classImg = numpy.zeros((rowNum,colNum),dtype=numpy.int8)

##### 3 - Read the pixel values for each seed from the input image data

def SpDist(p1,p2,n):
    sumDif = 0
    for i in range(n):
        sumDif = sumDif + (p1[i] - p2[i])**2
    return sumDif**0.5

for irow in range(rowNum):
    for icol in range(colNum):
        pixel = imgData[irow,icol,:]
        currentClass = 0
        outputClass = 0
        minD = float("inf")
        for sp in seedPixels:
            currentClass += 1
            ##### 5a - calculate spectral distance from pixel to seeds
            sd = SpDist(pixel, imgData[int(sp[1]),int(sp[0]),:], bandNum)
            ##### 5b - determine which seed has the shortest spectral distance
            if sd < minD:
                minD = sd
                ##### 5c - assign pixel to that seed's group
                outputClass = currentClass
        classImg[irow,icol] = outputClass




##### 6 - write output matrix to ouput file
outClassImg = gdal.GetDriverByName('GTIFF').Create(outputImg,colNum,rowNum,1, gdalconst.GDT_Byte)

outClassImg.SetProjection(projection)
outClassImg.SetGeoTransform(transformation)

outClassImg.GetRasterBand(1).WriteArray(classImg[:,:])

inputImg = None
outClassImg = None

print('done')
"""
jason_lab5.py

Purpose: This script is for GIS 662 Lab 5. It performs a region growing on one
         seed pixel and a spectral distace threshold.

Author: Jason Greenstein
"""

#import modules
import numpy, gdal, math, sys, gdalconst
from collections import deque

#read parameters
inputImg = sys.argv[1]
seedRow = int(sys.argv[2])
seedCol = int(sys.argv[3])
sdThresh = int(sys.argv[4])
outImg = sys.argv[5]

#spectral distance funtion
def SpDist(p1,p2,n):
    sumDif = 0
    for i in range(n):
        sumDif = sumDif + (p1[i] - p2[i])**2
    return sumDif**0.5

##### 1  - read the image file and store the data in a numpy matrix

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



##### 2 & 3 - keeping track of visited pixels, pixels to be evaluated, and grow region

need2Eval = deque()
visitedPixels = numpy.zeros((rowNum,colNum),dtype=numpy.int8)
growRegion = numpy.zeros((rowNum,colNum),dtype=numpy.int8)

need2Eval.append([seedRow,seedCol])             #add seed pixel to these structures
visitedPixels[seedRow,seedCol] = 1
growRegion[seedRow,seedCol] = 1


##### 4 - create array for output image
finalImg = numpy.zeros((rowNum,colNum),dtype=numpy.int8)

#### 5 - loop through pixels in need2Eval queue

#remove item in que and save its row and col
while len(need2Eval) != 0:
    neighborCheck = need2Eval.pop()
    neighborCheckRow = neighborCheck[0]
    neighborCheckCol = neighborCheck[1]

    neighbors = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]

#get locations of the 8 neighboring pixels
    for ineighbor in neighbors:
        neighborRow = neighborCheckRow + ineighbor[0]
        neighborCol = neighborCheckCol + ineighbor[1]

#check if neighboring pixels are inside image
        if  0 < neighborCol < colNum:
                if 0 < neighborRow < rowNum:

                        # check if pixel has been evaluated
                        if visitedPixels[neighborRow,neighborCol] == 0:
                            visitedPixels[neighborRow,neighborCol] = 1

                            #calcualtes spectral distance
                            SD = SpDist(imgData[neighborRow,neighborCol,:], imgData[seedCol,seedRow,:], bandNum)

                            #check spectral distance against the threshold
                            if SD < sdThresh:
                                growRegion[neighborRow,neighborCol] = 1
                                need2Eval.append([neighborRow,neighborCol])


#### 6 - write grow region matrix to output file

outGrowImg = gdal.GetDriverByName('HFA').Create(outImg,colNum,rowNum,1, gdalconst.GDT_Byte)

outGrowImg.SetProjection(projection)
outGrowImg.SetGeoTransform(transformation)

outGrowImg.GetRasterBand(1).WriteArray(growRegion[:,:])

inputImg = None
outGrowImg = None
outImg = None


print('done')












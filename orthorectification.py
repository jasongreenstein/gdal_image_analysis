"""
orthorectification.py

Purpose: This script will generate a ortho image from
         a DEM and an aerial image.

Author: Jason Greenstein

#############################################
Not functioning. col/row values are too high#
#############################################
"""
#import modules
import numpy, sys, math, gdal, gdalconst, csv



# 1 # read parameters (aerial image, dem, txt file)
inputImg = sys.argv[1]
inputDEM = sys.argv[2]
inputTxt = sys.argv[3]
outupOrtho = sys.argv[4]




# 2 # store parameters in numpy matrices

#AERIAL IMAGE#
#open input image
imgIn = gdal.Open(inputImg, gdalconst.GA_ReadOnly)
if imgIn is None:
    print ("Cannot access the aerial image file!\n")
    sys.exit(0)

#read image metadata
projectionfrom = imgIn.GetProjection()
geotransform = imgIn.GetGeoTransform()
colNums = imgIn.RasterXSize
rowNums = imgIn.RasterYSize
bandNums = imgIn.RasterCount

#copy image to numpy matrix
imgData = numpy.zeros((rowNums,colNums),dtype=numpy.float) #create template array
imgband=imgIn.GetRasterBand(1)                             #retrieve the only band
imgData[:,:,]=imgband.ReadAsArray(0,0,colNums,rowNums)     #copy band to template array



#DEM#
#open input DEM
demIn = gdal.Open(inputDEM, gdalconst.GA_ReadOnly)
if demIn is None:
    print ("Cannot access the DEM file!\n")
    sys.exit(0)

#read DEM metadata
projectionfrom_dem = demIn.GetProjection()
geotransform_dem = demIn.GetGeoTransform()
colNums_dem = demIn.RasterXSize
rowNums_dem = demIn.RasterYSize
bandNums_dem = demIn.RasterCount

#copy DEM to numpy matrix
demData = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.float)   #create template array
demband = demIn.GetRasterBand(1)                                     #retrieve the only band
demData[:,:] = demband.ReadAsArray(0,0,colNums_dem,rowNums_dem)      #copy band to template array


#TXT file#
#read txt file parameters
txtparam = {}                             #dictionary to hold text parameters

j = 0                                     #variable to hold number of parameters

with open(inputTxt) as txtfile:
    csv_reader = csv.reader(txtfile)
    for line in csv_reader:
        key = line[0].split('=')[0]
        value = line[0].split('=')[1]
        txtparam[key] = value
        j += 1



# 3 # create template array to hold output ortho photo
outOrtho = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.float)  #same dimensions DEM

print('step 3 done')

# 4 # calculate DEM's normalized (X,Y,Z)

#X
demXp = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.float)  #template for X'
demX = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.float)   #template for X

ul_x = geotransform_dem[0]                                        #value for upper left x
sr_x = geotransform_dem[1]                                        #value for spatial resolution x
x_off = float(txtparam['xOffset'])                                #value for x offset
x_scale = float(txtparam['xScale'])                               #value for x scale

for x in range (colNums_dem):
    demXp[:,x] = ul_x + (x * sr_x) #ul_x + sr_x*(x-1)             #array of DEM X' values
    demX[:,x] = (demXp[:,x] - x_off) / x_scale                    #convert to X

#Y
demYp = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.float)  #template for Y'
demY = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.float)   #template for Y

ul_y = geotransform_dem[3]                                        #value for upper left y
sr_y = geotransform_dem[5]                                        #value for spatial resolution y
y_off = float(txtparam['yOffset'])                                #value for y offset
y_scale = float(txtparam['yScale'])                               #value for y scale

for y in range(rowNums_dem):
    demYp[y,:] = ul_y + (y * sr_y) #ul_y - sr_y*(y-1)             #array of DEM Y' values
    demY[y,:] = (demYp[y,:] - y_off) / y_scale                    #convert to Y

print('step 4 done')

# 5 # calculate normalized (x,y) with DLT model

#converts str parameters to float
a0 = float(txtparam['a0'])
a1 = float(txtparam['a1'])
a2 = float(txtparam['a2'])
a3 = float(txtparam['a3'])
b0 = float(txtparam['b0'])
b1 = float(txtparam['b1'])
b2 = float(txtparam['b2'])
b3 = float(txtparam['b3'])
c1 = float(txtparam['c1'])
c2 = float(txtparam['c2'])
c3 = float(txtparam['c3'])
z_off = float(txtparam['zOffset'])
z_scale = float(txtparam['zScale'])


#z
z = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.float)   #create template array for z
for irow in range(rowNums_dem):
    for icol in range (colNums_dem):
        z[irow,icol] = (demData[irow,icol] - z_off) / z_scale

#x
x = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.float)   #create template array for x

for irow in range(rowNums_dem):
    for icol in range (colNums_dem):
        x[irow,icol] = (a0 + a1*demX[irow,icol] + a2*demY[irow,icol] + a3*z[irow,icol]) / \
                       (1  + c1*demX[irow,icol] + c2*demY[irow,icol] + c3*z[irow,icol])



#y
y = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.float)   #create template array for y

for irow in range (rowNums_dem):
    for icol in range (colNums_dem):
        y[irow,icol] = (b0 + b1*demX[irow,icol] + b2*demY[irow,icol] + b3*z[irow,icol]) / \
                       (1  + c1*demX[irow,icol] + c2*demY[irow,icol] + c3*z[irow,icol])



print('step 5 done')


# 6 # calculate (col,row)

#converts str parameters to float
colScale = float(txtparam['colScale'])                            #value for column scale
colOffset = float(txtparam['colOffset'])                          #value for column offset
rowScale = float(txtparam['rowScale'])                            #value for row scale
rowOffset = float(txtparam['rowOffset'])                          #value for row offset


#col
col = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.uint32)   #create template array for col

for irow in range (rowNums_dem):
    for icol in range (colNums_dem):
        col[irow,icol] = int(round((x[irow,icol] * colScale) + colOffset))
        #col[irow,icol] = int(round(col[irow,icol]))                   #nearest neightbor

#row
row = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.uint32)   #create template array for row

for irow in range (rowNums_dem):
    for icol in range (colNums_dem):
        row[irow,icol] = int(round((y[irow,icol] * rowScale) + rowOffset))
        #row[irow,icol] = int(round(row[irow,icol]))                   #nearest neightbor



print('step 6&7 done')
# 8 & 9 # interpolate pixel value from aerial image that within row,col values
ortho = numpy.zeros((rowNums_dem,colNums_dem),dtype=numpy.float) #create template array for ortho image

for irow in range (rowNums_dem):
    for irow in range (rowNums_dem):
        try:
            ortho[irow,icol] = imgData[row[irow,icol],col[irow,icol]]
        except IndexError:
            ortho[irow,icol] = -999



print('step 8&9 done')

# 10 # write ortho image to output file

orthoOut = gdal.GetDriverByName('GTIFF').Create(outupOrtho, colNums_dem, rowNums_dem, 1, gdalconst.GDT_Float32)

#set projection and transformation
orthoOut.SetProjection(projectionfrom_dem)
orthoOut.SetGeoTransform(geotransform_dem)

#write ortho values to output image
orthoOut.GetRasterBand(1).WriteArray(ortho[:])

#close the input aerial image, DEM, and output ortho image
inputImg = None
inputDEM = None
inputTxt = None
outupOrtho = None
orthoOut = None

print('done')



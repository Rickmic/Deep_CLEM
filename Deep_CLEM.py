# @File(label="Select electron microscopic image", required=false, persist=true, style="extensions:tif") EMfilepath
# @File(label="Select chromatin image", required=false, persist=true, style="extensions:tif") rLMfilepath
#@File[] listOfPaths(label="Add different channels of interest from light microscope", style="extensions:tif")
# @File(label="working directory", required=false, persist=true, style=directory) workdir
# @File(label="Model file", required=false, persist=true, style="extension:zip") modelFile
# @Boolean(label="Show progress dialog", required=false, value=true) showProgressDialog
# @DatasetIOService io
# @CommandService command
# @ModuleService module

import os
import sys
import java.util.Arrays
import java.io.File
import shutil
from ij import IJ, ImagePlus, ImageStack
from ij.process import ImageConverter
from java.io import File
from ij.io import FileSaver 
from ij.io import OpenDialog
from ij.io import DirectoryChooser 
from ij.gui import GenericDialog
from ij.plugin import ChannelSplitter
from ij.plugin import RGBStackMerge, RGBStackConverter
from fiji.util.gui import GenericDialogPlus 
from de.csbdresden.csbdeep.commands import GenericNetwork
from register_virtual_stack import Register_Virtual_Stack_MT
from register_virtual_stack import Transform_Virtual_Stack_MT

# define some parameters
nTiles = 16
overlap = 32
normalizeInput = True
percentileBottom = 0.5
percentileTop = 99.8
clip = True
# EM = electron microscopic image
# rLM = real light microscopic image (ground truth) with chromatin channel
# pLM = predictet light microscopic image
# c1LM, c2LM, c3LM ... = channels of interest (COI)

############################################ preprocessing

# java.io.File to string
EMfilepath = EMfilepath.toString()
rLMfilepath = rLMfilepath.toString()
workdir = workdir.toString()

# create a couple of folder in workdir
# for prediction
inputdir = os.path.join(workdir, "input")
os.mkdir(inputdir)
outputdir = os.path.join(workdir, "output")
# for alignment
os.mkdir(outputdir)
transformdir = os.path.join(workdir, "transform")
os.mkdir(transformdir)
COIinputdir = os.path.join(workdir, "COIinput")
os.mkdir(COIinputdir)
COIoutputdir = os.path.join(workdir, "COIoutput")
# for transformation of EM image
os.mkdir(COIoutputdir)
transformEMdir = os.path.join(workdir, "transformEM")
os.mkdir(transformEMdir)
EMindir = os.path.join(workdir, "EMin")
os.mkdir(EMindir)
EMoutdir = os.path.join(workdir, "EMout")
os.mkdir(EMoutdir)

# open EM image
EM = IJ.openImage(EMfilepath)

# equalize histogramm
IJ.run(EM, "Enhance Contrast...", "saturated=0.3 equalize")

# resize EM image
ip = EM.getProcessor()
width = ip.getWidth()
height = ip.getHeight()

EM.setProcessor (EM.getTitle(), EM.getProcessor().resize(256, 256))
ImageConverter(EM).convertToGray8()


EMstack = ImageStack(EM.getWidth(), EM.getHeight())
EMstack.addSlice(str(1), EM.getProcessor())
EMstack.addSlice(str(2), EM.getProcessor())
EM = ImagePlus(EM.getTitle(), EMstack)


saveEMfilepath = os.path.join(workdir, "EM.tif")
fs = FileSaver(EM) 
fs.saveAsTiff(saveEMfilepath)

# create path to save pLM image
savepLMfilepath = os.path.join(workdir, "input", "pLM.tif")

print("(-   )preprocessing done")
############################################ predict image
# run plugin CSBDeep (https://github.com/CSBDeep/CSBDeep_fiji/blob/master/script/CARE_generic.py)
def runNetwork(saveEMfilepath, savepLMfilepath):
	imp = io.open(saveEMfilepath)
	mymod = (command.run(GenericNetwork, False,
		"input", imp,
		"nTiles", nTiles,
		"overlap", overlap,
		"normalizeInput", normalizeInput,
		"percentileBottom", percentileBottom,
		"percentileTop", percentileTop,
		"clip", clip,
		"showProgressDialog", showProgressDialog,
		"modelFile", modelFile)).get()
	myoutput = mymod.getOutput("output")
	io.save(myoutput, savepLMfilepath)

runNetwork(saveEMfilepath, savepLMfilepath)

# open pLM image
pLM = IJ.openImage(savepLMfilepath)


# display precicted image

gd = GenericDialogPlus("Options")  
gd.addMessage("groundtruth SEM image:")
gd.addImage(EM)
gd.addMessage("prediction Chromatin:")
gd.addImage(pLM)
gd.showDialog() 

# resize pLM image
pLM.setProcessor (pLM.getTitle(), pLM.getProcessor().resize(width, height))
fs = FileSaver(pLM) 
fs.saveAsTiff(savepLMfilepath)

# save rLMimage
rLM = IJ.openImage(rLMfilepath)
saverLMfilepath = os.path.join(workdir, "input", "rLM.tif")
fs = FileSaver(rLM) 
fs.saveAsTiff(saverLMfilepath)

print("(--  )prediction done")
############################################ align pLM and rLM image
# source directory
source = inputdir + os.sep
source_dir = source
# output directory
target = outputdir +os.sep
target_dir = target
# transforms directory
transform = transformdir + os.sep
transf_dir = transform
# reference image
reference_name = "pLM.tif"
# shrinkage option (false)
use_shrinking_constraint = 0

 
p = Register_Virtual_Stack_MT.Param()
# The "maximum image size":
p.sift.maxOctaveSize = 1024
# The "inlier ratio":
p.minInlierRatio = 0.05
# Implemented transformation models for choice 
# 0=TRANSLATION, 1=RIGID, 2=SIMILARITY, 3=AFFINE, 4=ELASTIC, 5=MOVING_LEAST_SQUARES 
p.registrationModelIndex = 2 
# Implemented transformation models for choice
# 0=TRANSLATION, 1=RIGID, 2=SIMILARITY, 3=AFFINE
p.featuresModelIndex = 2
# run plugin Register Virtual Stack (https://imagej.net/Register_Virtual_Stack_Slices#Scripting_.2F_PlugIn)
Register_Virtual_Stack_MT.exec(source_dir, target_dir, transf_dir, 
reference_name, p, use_shrinking_constraint)
# close generated image stack
stack = IJ.getImage()
stack.close()

print("(--- )alignment done")
############################################ create overlay images


### preprocess COI
# java.io.File to list
listOfPathslist = listOfPaths.tolist()
rlmXmlPath= os.path.join(transform, "rLM.xml") 
i = 0
for channel in listOfPathslist:
	# save cLM image
	cLMfilepath = listOfPathslist[i]
	cLMfilepath = str(cLMfilepath)
	cLMname = os.path.basename(cLMfilepath)
	filename, file_extension = os.path.splitext(cLMname)
	cLM = IJ.openImage(cLMfilepath)
	savecLMfilepath = os.path.join(workdir, "COIinput", filename + ".tif")
	fs = FileSaver(cLM) 
	fs.saveAsTiff(savecLMfilepath)
	#duplicate rLM.xml file in transform
	i = i +1
	cLMxmlName = filename + ".xml"
	clmXmlPath= os.path.join(transform, cLMxmlName)
	shutil.copy(rlmXmlPath, clmXmlPath) 

# move and rename rLM.xml transformation_LM_image.xml
transformation_LM_imageXmlPath = os.path.join(workdir, "transformation_LM_image.xml")
shutil.copy(rlmXmlPath, transformation_LM_imageXmlPath)

### preprocess EM image


# move pLM.xml and copy rLM.xml file in transformEM -> EM image must be transformed during transformation of rLM. Otherwise the size wouldn't fit.
plmXmlPath= os.path.join(transform, "pLM.xml")
shutil.move(plmXmlPath, os.path.join(transform, "EM.xml")) # move and rename
#shutil.copy(rlmXmlPath, transformEMdir) # copy

# save original EM image for transformation
EM = IJ.openImage(EMfilepath)
fs = FileSaver(EM) 
fs.saveAsTiff(os.path.join(COIinputdir, "EM.tif"))

# copy rLM image for transformation
saverLMpath = os.path.join(outputdir, "rLM.tif")
shutil.copy(saverLMpath, os.path.join(COIinputdir, "rLM.tif")) # copy

# run plugin Transform Virtual Stack (https://javadoc.scijava.org/Fiji/register_virtual_stack/Transform_Virtual_Stack_MT.html)
#source_dir = EMindir + os.sep
#target_dir = EMoutdir + os.sep
#transf_dir = transformEMdir + os.sep
#print(source_dir)
#print(target_dir)
#print(transf_dir)
#interpolate = True
#Transform_Virtual_Stack_MT.exec(source_dir, target_dir, transf_dir, interpolate)
# close generated image stack
#stack = IJ.getImage()
#stack.close()


# run plugin Transform Virtual Stack (https://javadoc.scijava.org/Fiji/register_virtual_stack/Transform_Virtual_Stack_MT.html)
COIinput = COIinputdir + os.sep
source_dir = COIinput
COIoutput = COIoutputdir + os.sep
target_dir = COIoutput
transf_dir = transform 
interpolate = True
Transform_Virtual_Stack_MT.exec(source_dir, target_dir, transf_dir, interpolate)
# close generated image stack
stack = IJ.getImage()
stack.close()

### overlay EM and rLM image
# transformed EM to 8 bit
EM = IJ.openImage(os.path.join(COIoutput, "EM.tif"))
IJ.run(EM, "8-bit", "")
# overwrite EM stack with transformed EM image
fs = FileSaver(EM) 
fs.saveAsTiff(saveEMfilepath)
# open EM image as ImagePlus for merging channel
EM = ImagePlus(saveEMfilepath)
# split rLM image in different channels
saverLMpath = os.path.join(COIoutput, "rLM.tif")
rLM = IJ.openImage(saverLMpath)
R, G, B = ChannelSplitter.split(rLM)
overlay = RGBStackMerge.mergeChannels([None, None, B, EM, None, None, None], True) # Change R,G, B if the chromatin channel is a different one.
# If you want a different color for the chromatin in the overlay image, change the  position of the letter R,G,B, 
# e.g. [B, None, None, EM, None, None, None] for displaying chromatin in the red channel.
RGBStackConverter.convertToRGB(overlay)
saveoverlaypath = os.path.join(workdir, "EMoverlayChromatin.tif")
fs = FileSaver(overlay) 
fs.saveAsTiff(saveoverlaypath)

# clean up working directory

# remove temp files
#shutil.copy(saverLMpath, os.path.join(workdir, "chromatin.tif"))
#shutil.rmtree(COIinputdir)
#shutil.rmtree(inputdir)
#shutil.rmtree(outputdir)
#shutil.rmtree(transformdir)



print("(----)everything done")

#stuff

# get size of aligned image
#savepLMfilepath = os.path.join(outputdir, "pLM.tif")
#pLM = IJ.openImage(savepLMfilepath)
#ip = pLM.getProcessor()
#width = ip.getWidth()
#height = ip.getHeight()

# get set canvas size of EM image
EM = IJ.openImage(EMfilepath)
#w = str(width)
#h = str(height)
#args = "width="+w+" height="+h+" position=Center"
#IJ.run(EM, "Canvas Size...", args);
fs = FileSaver(EM) 
fs.saveAsTiff(saveEMfilepath)









# create rlmXmlPath
rlmXmlPath= os.path.join(transform, "rLM.xml")

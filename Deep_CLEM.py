# @File(label="Select electron microscopic image", required=false, persist=true, style="extensions:tif/png") EMfilepath
# @File(label="Select chromatin image", required=false, persist=true, style="extensions:tif/png") rLMfilepath
# @File[] listOfPaths(label="Add different channels of interest from light microscope")
# @File(label="working directory", required=false, persist=true, style=directory) workdir
# @File(label="Trained Network", required=false, persist=true, style="extension:zip") modelFile
# @Boolean(label="Show progress dialog", required=false, value=true) showProgressDialog
# @DatasetIOService io
# @CommandService command
# @ModuleService module

import os
import sys
import shutil
import java.util.Arrays
import java.io.File
from ij import IJ, ImagePlus, ImageStack
from ij.process import ImageConverter
from java.io import File
from fiji.util.gui import GenericDialogPlus 
from ij.io import FileSaver, OpenDialog, DirectoryChooser 
from ij.plugin import ChannelSplitter, RGBStackMerge, RGBStackConverter
from de.csbdresden.csbdeep.commands import GenericNetwork
from register_virtual_stack import Register_Virtual_Stack_MT
from register_virtual_stack import Transform_Virtual_Stack_MT

# define some variables
# EM = electron microscopic image
# rLM = real light microscopic image (ground truth) with chromatin channel
# pLM = predictet light microscopic image
# c1LM, c2LM, c3LM ... = channels of interest (COI)

# define input (java.io.File to string)
EMfilepath = EMfilepath.toString()
rLMfilepath = rLMfilepath.toString()
workdir = workdir.toString()

# check if workdir is empty

if len(os.listdir(workdir) ) != 0: 
	gd = GenericDialogPlus("Options")  
	gd.addMessage("Working directory must be empty!")
	gd.addMessage("Please delete all files in the working directory, or choose another working directory and restart the Deep CLEM Plugin.")
	gd.showDialog()
	
if len(os.listdir(workdir) ) != 0: 
    sys.exit()

# create a couple of folder in workdir

# for registration
registration_inputdir = os.path.join(workdir, "registration_input")
os.mkdir(registration_inputdir)
registration_outputdir = os.path.join(workdir, "registration_output")
os.mkdir(registration_outputdir)

# for transformation
transformdir = os.path.join(workdir, "transform")
os.mkdir(transformdir)
transformation_inputdir = os.path.join(workdir, "transformation_input")
os.mkdir(transformation_inputdir)
transformation_outputdir = os.path.join(workdir, "transformation_output")
os.mkdir(transformation_outputdir)


############################################ preprocessing


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

# create stack z=2
EMstack = ImageStack(EM.getWidth(), EM.getHeight())
EMstack.addSlice(str(1), EM.getProcessor())
EMstack.addSlice(str(2), EM.getProcessor())
EM = ImagePlus(EM.getTitle(), EMstack)

# save EM image
saveEMfilepath = os.path.join(workdir, "EM.tif")
fs = FileSaver(EM) 
fs.saveAsTiff(saveEMfilepath)

print("(-     )preprocessing done")


############################################ predict image


# use plugin CSBDeep (https://github.com/CSBDeep/CSBDeep_fiji/blob/master/script/CARE_generic.py)

# create path to save pLM image
savepLMfilepath = os.path.join(workdir, "registration_input", "pLM.tif")

# define some parameters
nTiles = 16
overlap = 32
normalizeInput = True
percentileBottom = 0.5
percentileTop = 99.8
clip = True

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

# resize and save pLM image
pLM.setProcessor (pLM.getTitle(), pLM.getProcessor().resize(width, height))
fs = FileSaver(pLM) 
fs.saveAsTiff(savepLMfilepath)

# save rLM image
rLM = IJ.openImage(rLMfilepath)
saverLMfilepath = os.path.join(workdir, "registration_input", "rLM.tif")
fs = FileSaver(rLM) 
fs.saveAsTiff(saverLMfilepath)

print("(--    )prediction done")


############################################ register pLM and rLM image


# uses plugin Register Virtual Stack Slices (https://imagej.net/Register_Virtual_Stack_Slices)

# define some variables
# source directory
source = registration_inputdir + os.sep
source_dir = source
# output directory
target = registration_outputdir +os.sep
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

# run plugin 
Register_Virtual_Stack_MT.exec(source_dir, target_dir, transf_dir, 
reference_name, p, use_shrinking_constraint)

# close generated image stack
stack = IJ.getImage()
stack.close()

print("(---   )registration done")


############################################ transform images


###### preprocess COI

# java.io.File to list
listOfPathslist = listOfPaths.tolist()
rlmXmlPath= os.path.join(transform, "rLM.xml") 
i = 0

# save one xml file for each COI image with the corresponding name.
for channel in listOfPathslist:
	# save cLM image
	cLMfilepath = listOfPathslist[i]
	cLMfilepath = str(cLMfilepath)
	cLMname = os.path.basename(cLMfilepath)
	filename, file_extension = os.path.splitext(cLMname)
	cLM = IJ.openImage(cLMfilepath)
	savecLMfilepath = os.path.join(workdir, "transformation_input", filename + ".tif")
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

###### preprocess EM and rLM image

# move pLM.xml and copy rLM.xml file in transformEM -> EM image must be transformed during transformation of rLM. Otherwise the size wouldn't fit.
plmXmlPath= os.path.join(transform, "pLM.xml")
shutil.move(plmXmlPath, os.path.join(transform, "EM.xml")) # move and rename

# save original EM image for transformation
EM = IJ.openImage(EMfilepath)
fs = FileSaver(EM) 
fs.saveAsTiff(os.path.join(transformation_inputdir, "EM.tif"))

# save rLM image for transformation
shutil.copy(rLMfilepath, os.path.join(transformation_inputdir, "rLM.tif")) # copy

###### run plugin

# run plugin Transform Virtual Stack (https://javadoc.scijava.org/Fiji/register_virtual_stack/Transform_Virtual_Stack_MT.html)
# define some variables
transformation_input = transformation_inputdir + os.sep
source_dir = transformation_input
transformation_output = transformation_outputdir + os.sep
target_dir = transformation_output
transf_dir = transform 
interpolate = True

# run plugin
Transform_Virtual_Stack_MT.exec(source_dir, target_dir, transf_dir, interpolate)

# close generated image stack
stack = IJ.getImage()
stack.close()

print("(----  )transformation done")


############################################ overlay EM and rLM image


# transformed EM to 8 bit
EM = IJ.openImage(os.path.join(transformation_output, "EM.tif"))
IJ.run(EM, "8-bit", "")

# overwrite EM stack with transformed EM image
fs = FileSaver(EM) 
fs.saveAsTiff(saveEMfilepath)

# open EM image as ImagePlus for merging channel
EM = ImagePlus(saveEMfilepath)

# split rLM image in different channels
saverLMpath = os.path.join(transformation_output, "rLM.tif")
rLM = IJ.openImage(saverLMpath)
R, G, B = ChannelSplitter.split(rLM)

# Merge channels
overlay = RGBStackMerge.mergeChannels([None, None, B, EM, None, None, None], True) # Change R,G, B if the chromatin channel is a different one.
# If you want a different color for the chromatin in the overlay image, change the  position of the letter R,G,B, 
# e.g. [B, None, None, EM, None, None, None] for displaying chromatin in the red channel.
RGBStackConverter.convertToRGB(overlay)

# save overlay
saveoverlaypath = os.path.join(workdir, "overlay_EM_Chromatin.tif")
fs = FileSaver(overlay) 
fs.saveAsTiff(saveoverlaypath)

print("(----- )overlay EM and rLM image done")


############################################ clean up


# copy important files into the working directory 
os.remove(os.path.join(workdir, "EM.tif"))
shutil.move(os.path.join(transformation_output, "EM.tif"), os.path.join(workdir, "SEM.tif")) 
shutil.move(os.path.join(transformation_output, "rLM.tif"), os.path.join(workdir, "Chromatin.tif"))
COIfiles = os.listdir (transformation_output)
for fileName in COIfiles:
	filePath = os.path.join(workdir, fileName)
	if filePath.endswith(".tif"):
		shutil.move(os.path.join(transformation_output, fileName), os.path.join(workdir, fileName))

# remove all created directorys

# If you need aditional files uncomment the following commands
shutil.rmtree(registration_inputdir) # uncomment if you need the predicted image
shutil.rmtree(registration_outputdir) # uncomment if you need the registered, predicted and real image, that shows the chromatin channel
shutil.rmtree(transformdir) # uncomment if you need the transforms (XML-files) for EM, rLM and COI's
shutil.rmtree(transformation_inputdir)
shutil.rmtree(transformation_outputdir)



print("(------)everything done")


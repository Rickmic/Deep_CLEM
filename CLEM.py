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

# create input/output/transform/channelOfInterest folder in workdir
inputdir = os.path.join(workdir, "input")
os.mkdir(inputdir)
outputdir = os.path.join(workdir, "output")
os.mkdir(outputdir)
transformdir = os.path.join(workdir, "transform")
os.mkdir(transformdir)
COIinputdir = os.path.join(workdir, "COIinput")
os.mkdir(COIinputdir)
COIoutputdir = os.path.join(workdir, "COIoutput")
os.mkdir(COIoutputdir)

# open EM image
EM = IJ.openImage(EMfilepath)

# resize EM image
ip = EM.getProcessor()
width = ip.getWidth()
height = ip.getHeight()
ip.resize(256, 256)
EM.setProcessor (ip)
ImageConverter(EM).convertToGray8()

EMstack = ImageStack(EM.getWidth(), EM.getHeight())
EMstack.addSlice(EM.getProcessor())
EMstack.addSlice(EM.getProcessor())
EM = EMstack
saveEMfilepath = os.path.join(workdir, "input", "EM.tif")
fs = FileSaver(EM) 
fs.saveAsTiffStack(saveEMfilepath)

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

runNetwork(EMfilepath, savepLMfilepath)

# open pLM image
pLM = IJ.openImage(savepLMfilepath)

# resize pLM image
ip = pLM.getProcessor()
ip.resize(width, height)
pLM.setProcessor (ip)
IJ.saveAsTiff(pLM, savepLMfilepath)

# display precicted image

gd = GenericDialogPlus("Options")  
gd.addMessage("groundtruth SEM image:")
gd.addImage(EM)
gd.addMessage("prediction Chromatin:")
gd.addImage(pLM)
gd.showDialog() 

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
############################################ process channels of interest

# java.io.File to list
listOfPathslist = listOfPaths.tolist()

# remove pLM.xml file in transform
plmXmlPath= os.path.join(transform, "pLM.xml")
os.remove(plmXmlPath)

#create rlmXmlPath
rlmXmlPath= os.path.join(transform, "rLM.xml")
i = 0

for channel in listOfPathslist:
	# save cLM image
	cLMfilepath = listOfPathslist[i]
	cLMfilepath = str(cLMfilepath)
	cLM = IJ.openImage(cLMfilepath)
	cLMname = os.path.basename(cLMfilepath)
	savecLMfilepath = os.path.join(workdir, "COIinput", cLMname)
	fs = FileSaver(cLM) 
	fs.saveAsTiff(savecLMfilepath)
	#duplicate rLM.xml file in transform
	i = i +1
	cLMxmlName = str(i) + "LM.xml"
	clmXmlPath= os.path.join(transform, cLMxmlName)
	shutil.copy(rlmXmlPath, clmXmlPath) 

# remove rLM.xml file in transform
os.remove(rlmXmlPath)

COIinput = COIinputdir + os.sep
source_dir = COIinput
COIoutput = COIoutputdir + os.sep
target_dir = COIoutput
transf_dir = transform # defined in align pLM and rLM image
interpolate = True
# run plugin Transform Virtual Stack (https://javadoc.scijava.org/Fiji/register_virtual_stack/Transform_Virtual_Stack_MT.html)
Transform_Virtual_Stack_MT.exec(source_dir, target_dir, transf_dir, interpolate)
# close generated image stack
stack = IJ.getImage()
stack.close()

print("(----)everything done")


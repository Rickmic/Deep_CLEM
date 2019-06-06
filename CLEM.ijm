
// EM = electron microscopic image
// rLM = real light microscopic image (ground truth) with chromatin channel
// pLM = predictet light microscopic image
// c1LM, c2LM, c3LM ... = channels of interest

///////////////////////////////// preprocessing

// select EM image
EMfilepath=File.openDialog("Select electron microscopic image (only greyscale tif)");
//EMfile=File.openAsString(EMfilepath); 

// open rLM image
rLMfilepath=File.openDialog("Select light microscopic image (only greyscale tif)"); 
//rLMfile=File.openAsString(rLMfilepath); 

// open EM image
open(EMfilepath);
EMname = getTitle();

//open LM image
open(rLMfilepath);
rLMname = getTitle();

///////////////////////////////// prediction

// predict pLM image
selectWindow(EMname)
run("Run your network", "input=EMname normalizeinput=true percentilebottom=3.0 percentiletop=99.8 clip=false ntiles=9 blockmultiple=32 overlap=32 batchsize=1 modelfile=/home/rick/CLEM/CSBDeep/my_model/TF_SavedModel.zip showprogressdialog=true");

//////////////////////////////// registration

//select working directory
workingdir = getDirectory("Choose a working directory")

// create input directory
inputdirectory = workingdir + "input" + File.separator
File.makeDirectory(inputdirectory)

// create outputdirectory
outputdirectory = workingdir + "output" + File.separator
File.makeDirectory(outputdirectory)

// save rLM image
selectWindow(rLMname)
rLMsavepath = inputdirectory + rLMname
saveAs("Tiff", rLMsavepath);

// convert and save result image
selectWindow("result");
setOption("ScaleConversions", true);
run("16-bit");
resultsavepath = inputdirectory + "result.tif"
saveAs("Tiff", resultsavepath);

// register virtual stack slice
run("Register Virtual Stack Slices", "source="+inputdirectory+" output="+outputdirectory+" feature=Rigid registration=[Rigid                -- translate + rotate                  ] save");



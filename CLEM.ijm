// EM = electron microscopic image
// rLM = real light microscopic image (ground truth) with chromatin channel
// pLM = predictet light microscopic image


EMfilepath=File.openDialog("Select electron microscopic image (only greyscale tif)");
EMfile=File.openAsString(EMfilepath); 
rLMfilepath=File.openDialog("Select light microscopic image (only greyscale tif)"); 
rLMfile=File.openAsString(rLMfilepath); 
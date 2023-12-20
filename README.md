# DeepCLEM

This repository contains the code and data for

### DeepCLEM: automated registration for correlative light and electron microscopy using deep learning

*Rick Seifert, Sebastian M. Markert, Sebastian Britz, Veronika Perschin, Christoph Erbacher, Christian Stigloher and Philip Kollmannsberger*

F1000Research 9:1275 (2020), https://doi.org/10.12688/f1000research.27158.1

> Below you find information how to [install and run](#install) the Fiji plugin with the included pretrained network model, as well as instructions how to [train a custom model](#train) on your own data. If you need help or have questions, feel free to open an <a href="https://github.com/CIA-CCTB/Deep_CLEM/issues">issue</a> or contact the corresponding author by <a href="mailto:philipk@gmx.net">email</a>. For general questions related to Fiji or CSBDeep, we recommend the <a href="https://forum.image.sc/">image.sc</a> forum.

This work was part of the BSc thesis project of Rick Seifert in the Computational Image Analysis group at the [Center for Computational and Theoretical Biology](https://www.biozentrum.uni-wuerzburg.de/cctb/cctb/) together with the [Imaging Core Facility](https://www.biozentrum.uni-wuerzburg.de/em/startseite/) of the University of Würzburg, performed in 2019.

<p align="center"> 
  <img src="https://f1000researchdata.s3.amazonaws.com/manuscripts/30002/0db554d6-8849-4105-ac0c-0a019fef925d_figure1.gif" width=450px>
</p>

----
<a id="install"></a>
## (A) Install and run Fiji plugin Deep_CLEM

### 1. Install Fiji

<p align="justify">
Please download and install Fiji following the <a href="https://imagej.net/Fiji/Downloads">instructions</a>.
</p>


### 2. Install Fiji plugin CSBDeep


<p align="justify">
Please download and install the CSBDeep plugin following the <a href="https://github.com/CSBDeep/CSBDeep_website/wiki/CSBDeep-in-Fiji-%E2%80%93-Installation">instructions</a>
</p>


### 3. Clone this repository

#### 3.1 Linux and MacOS

```sh
git clone https://github.com/CIA-CCTB/Deep_CLEM.git
cd Deep_CLEM
```

#### 3.2 Windows

<p align="justify">
  <ul>
    <li>
      click the green button <i>Clone or Download</i> and then select <i>Download ZIP</i>
    </li>
    <li>
      save the ZIP file in a directory of your choice
    </li>
    <li>
      open the directory with an explorer and unzip the file
    </li>
    <li>
      open the unzipped directory 
    </li>
  </ul>
</p>

### 4. Copy Deep_CLEM.py into your Fiji.app/plugins directory

#### 4.1 Linux and macos

```sh
cp Deep_CLEM.py [path to Fiji]/Fiji.app/plugins/
```

#### 4.2 Windows

<p align="justify">
  copy the file <i>Deep_CLEM.py</i> in your Fiji plugin folder (/Fiji.app/plugins/)
</p>

### 5. Restart Fiji

<p align="justify">
  If Fiji was restarted, you should be able to find the plugin Deep_CLEM. (Plugins > Deep_CLEM)
</p>

### 6. Start Deep_CLEM


<p align="justify">
  <ul>
    <li>
      If you run the plugin Deep_CLEM, the following window should be visible:
    </li>
  </ul>
</p>



<p align="center"> 
  <img src="../assets/GUI1.png">
</p>


<p align="justify">
  <ul>
    <li>
      Select an electron microscopic image and corresponding light microscopic image as well as one or more light microscopic channels of interest, a working directory and a trained model. The working directory should be an empty, already existing directory and as trained network you can use the file <i>Trained_Network.zip</i>. After that, select Run. 
    </li>
    <li>
      It is recommended to test at first the correlation with example images. Use as electron microscopic image <i>EM.png</i>, as light microscopic image <i>Chromatin.png</i> and as channel of interest the image <i>Channel_of_interest.png</i>. These images were taken by Sebastian Markert (Image Core Facility University of Wuerzburg).
    </li>
    <li>
      If you use your own input images, they must fulfill the following criteria:
      <ul>
        <li>
          The electron microscopic image should have similar contrast and resolution as the test image <i>EM.png</i> if you use the pretrained network included with DeepCLEM. If your EM images look very different, you can train your own model as described below.
        </li>
        <li>
          All image files should be either in .png or .tif format.
        </li>
        <li>
          The chromatin channel and the electron microscopic image need to have at least <b>three</b> matching <b>nuclei</b> for the automated registration to work. Alternatively, other stains than chromatin can be used for prediction and correlation if you train your own network model. 
        </li>
        <li>
          As chromatin channel, a RGB image with the chromatin information in the blue channel is required. If your chromatin image is in greyscale format, you can convert it to RGB using Fiji.
        <li>
          All light microscopic channels should have the <b>same dimensions</b>.
        </li>
        <li>
          Select <b>at least one image as Channel of interest</b>, otherwise you will be asked to select one during running the plugin.
        </li>
      </ul>
    </li>
    <li>
      If you have selected <i>show process dialog</i>, the process window of CSBDeep will be visible.
    </li>
    <li>
      After a short time, (depending on your CPU/GPU), a new window will appear. This window shows you the electron microscopic and the predicted light microscopic image. Check if the predicted light microscopic image shows roughly the shape of the chromatin in the electron microscopic image and proceed with <i>OK</i>. 
    </li>
  </ul>
</p>



<p align="center"> 
  <img src="../assets/GUI2.png">
</p>


<p align="justify"> 
  <ul>
    <li>
      If the plugin is ready you can see <i>Command finished: Deep CLEM</i> in the Status Bar.
    </li>
    <li>
      Deep CLEM created several images and one xml file:
      <img src="../assets/GUI3.png">
      <ul>
        <li>
          The file <i>transformation_LM_image.xml</i> contains all transformations that were applied to the light microscopic images to align them to the electron microscopic images. You can use the .xml file for example with the Fiji plugin <a href="https://imagej.net/Transform_Virtual_Stack_Slices">Transform Virtual Stack Slices</a> to repeat the transformation with another image.
        </li>
        <li>
          Furthermore, one correlated electron microscopic image (<i>SEM.tif</i>) was created.
        </li>
        <li>
          The image <i>Chromatin.tif</i> contains the correlated image of the chromatin channel.
        </li>
        <li>
          <i>overlay_EM_Chromatin.tif</i> shows the chromatin image in the blue channel and the electron microscopic image in the greyscale channel.
        </li>
        <li>
          In addition, all selected images that present a channel of interest were correlated and saved in the working directory.
        </li>
      </ul>
    </li>
    <li>
      The color channels of all created images can be split and merged with <a href="https://fiji.sc/">Fiji</a> using the <a href="https://imagej.net/Color_Image_Processing">splitting multi channel images and merging images</a> option.
    </li>
  </ul>
</p>

----

<a id="train"></a>
## (B) Train your own network

### 1. Set up the python environment

<p align="justify">
  <ul>
    <li>
      Install <a href="https://www.anaconda.com/distribution/">Anaconda</a>
    </li>
    <li>
      Clone this repository if you haven't done this yet.
    </li>
    <li>
      Navigate into the directory Deep_CLEM
    </li>
  </ul>
</p>

```sh
  cd Deep_CLEM
  ```

<p align="justify">
  <ul>
    <li>
      Install <a href="https://github.com/mamba-org/mamba/">Mamba</a> for fast dependency solving:
    </li>
  </ul>
</p>

  ```sh
  conda activate
  conda install mamba -n base -c conda-forge
  ```

<p align="justify">
  <ul>
    <li>
      Create a new conda environment with all requirements for the two python notebooks:
    </li>
  </ul>
</p>

  ```sh

  mamba env create --file DeepCLEM.yml
  conda activate DeepCLEM
  ```
  
<p align="justify">
  This environment file will install recent versions of Tensorflow, CUDA and CSBDeep 
  and thus should work with the newest GPU hardware. The notebooks were tested under 
  Windows 10 with Tensorflow 2.3.0, CUDA 11.3 and CSBDeep 0.7.4. If you encounter problems, 
  you may have to specify these versions explicitly in the .yml file.
</p>

### 2. Training data

<p align="justify">
  <ul>
    <li>
      For training, 60-100 correlated images are neccessary. It is possible to use images from Z-stacks.
    </li>
    <li>
      Electron and fluorescent microscopic images should be stored in two different folders.
    </li>
    <li>
      The electron and fluorescent microscopic images could be greyscale or RGB images.
    </li>
    <li>
      Each pair of electron and fluorescent microscopic images should be named with the same filename.
    </li>
  </ul>
</p>
This repository contains a small demo dataset to test if the training works. The full training dataset used in the paper is available on Zenodo: https://zenodo.org/record/6973994#.YvD2lOxBzQ0

### 3. Preprocess images

<p align="justify">
  For preprocessing you have to start <a href="https://jupyter.readthedocs.io/en/latest/running.html">jupyter notebook</a> and preprocess your images for training with the jupyter notebook <a href="https://github.com/CIA-CCTB/Deep_CLEM/blob/master/load_data.ipynb"><i>load_data.ipynb.</i></a> This jupyter notebook script is based on <a href="https://github.com/CSBDeep/CSBDeep/blob/master/examples/denoising3D/1_datagen.ipynb">this script</a>.
</p>

### 4. Train network

<p align="justify">
  Train your network with the jupyter notebook <a href="https://github.com/CIA-CCTB/Deep_CLEM/blob/master/train_network.ipynb"><i>train_network.ipynb</i></a> , based on <a href="https://github.com/CSBDeep/CSBDeep/blob/master/examples/denoising3D/2_training.ipynb">this script</a>.
</p>

# Deep_CLEM

## Install and run Fiji plugin DeepCLEM

### 1. Install Fiji


<p align="justify">
  <a href="https://imagej.net/Fiji/Downloads">Source</a>
</p>


### 2. Install Fiji plugin CSBDeep


<p align="justify">
  <a href="https://github.com/CSBDeep/CSBDeep_website/wiki/CSBDeep-in-Fiji-%E2%80%93-Installation">Source</a>
</p>


### 3. Clone this repo

#### 3.1 Linux and macos

```sh
git clone https://github.com/Rickmic/Deep_CLEM.git
cd Deep_CLEM
```

#### 3.2 Windows

<p align="justify">
  <ul>
    <li>
      click the green button <i>Clone or Download</i> and Select <i>Download ZIP</i>
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
  Now you should be able to find the plugin (Plugins > Deep_CLEM)
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
      Select an electron microscopic image, a light microscopic image, several light microscopic channels of interest, a   working directory and a trained network. The working directory should be an empty, already existing directory and as trained network you can use the file <i>Trained_Network.zip</i>. After that, select Run. 
    </li>
    <li>
      It will be recommended to test at first the correlation with example images. Use as electron microscopic image <i>EM.png</i>, as light microscopic image <i>Chromatin.png</i> and as channel of interest the image <i>Channel_of_interest.png</i>.
    </li>
    <li>
      If you use own input images, they must fulfill the following criteria:
      <ul>
        <li>
          electron microscopic image should look like the testing image <i>EM.png</i>
        </li>
        <li>
          either a <b>PNG</b> or an <b>TIF</b> file
        </li>
        <li>
          at least <b>two</b> matching <b>nucleoli</b> in chromatin channel and electron microscopic image
        </li>
        <li>
          all light microscopic channels should have the <b>same dimensions</b>
        </li>
        <li>
          select <b>at least one image as Channel of interest</b>, otherwise you will be asked to select one during running the plugin
        </li>
      </ul>
    </li>
    <li>
      If you have selected show process dialog, the process window of CSBDeep will be visible.
    </li>
  </ul>
</p>



<p align="center"> 
  <img src="../assets/GUI2.png">
</p>


<p align="justify"> 
  <ul>
    <li>
      After a short time, (depending on your CPU/GPU) another window will be visible. This window shows you the electron microscopic and the predicted light microscopic image. Check if the predicted light microscopic image shows roughly the shape of the chromatin in the electron microscopic image and proceed with OK. 
    </li
    <li>
      If the plugin is ready you can see <i>Command finished: Deep CLEM</i> in the Status Bar.
    </li>
    <li>
      Deep CLEM created several images and one xml file: 
      <ul>
        <li>
          The file <i>transformation_LM_image.xml</i> contains all transformations, that were made to the light microscopic images to align them to the electron microscopic images. You can use the xml file for example with the Fiji plugin <a href="https://imagej.net/Transform_Virtual_Stack_Slices">Transform Virtual Stack Slices</a> to repeat the transformation with another image.
        </li>
        <li>
          Furthermore, one correlated electron microscopic image (<i>SEM.tif</i>) was created.
        </li>
        <li>
          The image <i>Chromatin.tif</i> contains the correlated image of the chromatin channel.
        </li>
        <li>
          In addition all selected images, that present an channel of interest were correlated and saved in the working directory.
        </li>
      </ul>
    </li>
    <li>
      The color channels of all created images can be splitted and merged with <a href="https://fiji.sc/">Fiji</a> using the <a href="https://imagej.net/Color_Image_Processing">splitting multi channel images and merging images</a> option.
    </li>
  </ul>
</p>



## Train your own network

### 1. Set up the python environment

<p align="justify">
  <ul>
    <li>
      Install <a href="https://www.anaconda.com/distribution/">Anaconda</a>
    </li>
    <li>
      Clone this repo if you haven't done this yet.
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
      create a new conda environment with all requirements for the two python scripts
    </li>
  </ul>
</p>

  ```sh
  conda activate
  conda env create --file DeepCLEM.yml
  conda activate DeepCLEM
  ```
  
<p align="justify">
  This environment was tested under <i>Ubuntu 16.04.5 LTS</i> with CUDA version <i>9.2.148</i>. If you use another CUDA version you may   have to install a different tensorflow version as in the yml file.
</p>


### 2. Preprocess images

<p align="justify">
  Preprocess your images for training with the jupyter notebook _load_data.ipynb._ This jupyter notebokk script is based on <a href="https://nbviewer.jupyter.org/url/csbdeep.bioimagecomputing.com/examples/denoising3D/1_datagen.ipynb">this script</a>
</p>

### 3. Train network

<p align="justify">
  Train your network with the jupyter notebok _train_network.ipynb_, that is based on <a href="https://nbviewer.jupyter.org/url/csbdeep.bioimagecomputing.com/examples/denoising3D/2_training.ipynb">this script</a>
</p>

# Deep_CLEM

## Install Fiji plugin DeepCLEM

**1. Install Fiji**

[source](https://imagej.net/Fiji/Downloads)

**2. Install Fiji plugin CSBDeep**

[source](https://github.com/CSBDeep/CSBDeep_website/wiki/CSBDeep-in-Fiji-%E2%80%93-Installation)

**3. Clone this repo**

```sh
git clone https://github.com/Rickmic/Deep_CLEM.git
cd Deep_CLEM
```

**4. Copy Deep_CLEM.py into your Fiji.app/plugins directory**

```sh
cp Deep_CLEM.py [path to Fiji]/Fiji.app/plugins/
```

**5. Restart Fiji**

Now you should be able to run the plugin (Plugins > Deep_CLEM)

**6. 

![UI](/assets/Bildschirmfoto vom 2019-06-28 13-41-35.png)


# Train your own network


load_data.ipynb is based on [this script](https://nbviewer.jupyter.org/url/csbdeep.bioimagecomputing.com/examples/denoising3D/1_datagen.ipynb)

train_network.ipynb is based on [this script](https://nbviewer.jupyter.org/url/csbdeep.bioimagecomputing.com/examples/denoising3D/2_training.ipynb)

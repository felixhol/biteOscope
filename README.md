# biteOscope

### Running a biteOscope and processing data. 

Cages can be made out of acrylic using a laser cutter, design files are provided in the cageDesigns directory. Temperature control is provided by tempControl.py and requires a raspberry pi, a waterproof DS18B20 temperature probe, and a 5V relay. 

Image analysis code is provided as .py files and notebooks (notebook filenames are appended with 'NB') and can be tested using the demo data available as a zip file. 

1. trackMosq.py finds centroids of all mosquitoes in images and tracks them over time. 
	* trackingResultsMovie.ipynb creates a video in which tracking results are marked to verify output. 
2. cropTracks_features.py stores cropped images centered on the focal mosquito of all frames belonging to a single track and calculates various features (e.g. movement and feeding stats).
3. inferenceAlbo_test.py does DeepLabCut based body part tracking

The playground folder contains various notebooks for downstream analysis and is under continuous development. 


<p align="center">
  <img width="402" height="414" src="/playground/stylet03.gif">
</p>

### Dependencies

The biteOscope code uses the following modules:

* numpy
* matplotlib
* pandas
* scipy
* scikit-image
* scikit-learn
* trackpy
* opencv
* joblib
* deeplabcut
* tqdm





<!-- ![alt text](/playground/stylet03.gif "Tracking image")
 -->
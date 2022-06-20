# mvgen-win10

MVGEN WINDOWS 10 INSTALLATION + SETUP DOCUMENTATION
INSTALL MVGEN-MASTER FROM GITHUB LINK BELOW
https://github.com/scraper24124/mvgen

INSTALL PYTHON AND FFMPEG
Link to FFMPEG: https://www.ffmpeg.org/download.html#build-windows

ADD FFMPEG TO PATH
Follow this guide: https://www.wikihow.com/Install-FFmpeg-on-Windows

INSTALL PACKAGES
Navigate to mvgen-master folder and run python setup.py install
Alternatively, you can manually install the following packages using pip: 
Attrs=21.2.0, numpy==1.21.0, pandas==1.3.0, PyYAML==5.4.1, PyWavelets==1.1.1, scipy==1.7.0, tqdm==4.61.1, aubio==0.4.9, unidecode=1.2.0
CREATE CONFIG.YAML FILE INSIDE THE MVGEN-MASTER DIRECTORY
By default, there is already a config.yaml file that you can edit
![image](https://user-images.githubusercontent.com/107861190/174609668-3f1bb598-2883-49dd-9e25-d4c342c022df.png)


Add the paths of the directories to the first 5 variables above
 
![image](https://user-images.githubusercontent.com/107861190/174609709-856ad61f-b5e8-429b-9465-585fb67be0f2.png)

IMPORTANT: Create another directory inside the raw_directory that has the same name as the enclosing raw_directory, but ensure that the paths added to any files point to the first directory

ADD PATH TO MVGEN.PY
Navigate to mvgen.py (under the directory ‘mv’) and add the source directory path (same path as raw_directory in the previous step) to line 43 between the speech marks

![image](https://user-images.githubusercontent.com/107861190/174609722-01e816f6-2f78-463b-88d5-4cd6ccf04394.png)




Leave the ‘r’ 



All done!
Add your videos to the inner raw directory and run python main.py -s {name_of_raw_directory}
The finished product will be inside the ready_directory when complete.

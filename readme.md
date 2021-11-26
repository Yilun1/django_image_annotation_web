**! in order to make the functions of this tool simple to understand, I made a demo.mp4 video showing what this website is like !**


**Basic description:**


this is a student project of a simple scene character annotation website，

it can also be used in other image annotation tasks，

it features a file manager, an annotation tool and a detection algorithm(only for detecting scene characters)


**Image annotation tool:**


the code of the js image annotation tool is in the canvas_modify_multifiles.html，

because I only used var instead of let or const, there are warnings but it works fine，

as for how to use the tool, please refer to the demo video and the tutorial text file  


**How to run:**


read the readme_how_to_build text file to run the code. the code can also be deployed on server. 

if use the detection algorithm please download it from the link below and create a /east_path folder，

then put the model in the folder


**Acknowledgement:**


the file manager comes from another project: https://github.com/talented/FileManager

the detection algorithm is from: https://github.com/opencv/opencv/blob/master/samples/dnn/text_detection.py

the links of the detection model: https://www.dropbox.com/s/r2ingd0l3zt8hxs/frozen_east_text_detection.tar.gz?dl=1


**Basic decription of the workflow: **


the user upload images and manage them with file manager，

then select some images and click annotation button，

the images will be loaded in the annotation tool，

the user can use the algorithm first then edit the results，

the tool supports editable polygon annotation for detection results，

the recognition results are put in a rectangle to decide its position and size


**Others:**


I found that github has detected most used programming language as Html, 

that's because I put the javascript code of annotation tool directly on the html file for convience

maybe I'll change it in the future 

 


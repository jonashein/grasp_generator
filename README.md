# Towards Markerless Surgical Tool and Hand Pose Estimation: Synthetic Grasp Generation

- [Project page](http://medicalaugmentedreality.org/handobject.html)
<!-- - [Paper](http://arxiv.org/abs/2004.13449) -->

This codebase is an adaptation of the original [Obman](https://hassony2.github.io/obman.html) pipeline to generate synthetic images of hand-object interactions.
While the original pipeline relies on the Eigengrasp planner that is included in the [GraspIt!](http://graspit-simulator.github.io/) simulator, this fork allows to manually generate grasp templates which are then automatically augmented and verified in the simulator.
The manual creation of grasp templates is useful for objects on which the Eigengrasp planner produces suboptimal or unnatural results, e.g. objects with designated or ergonomically formed handles. 
The generated grasps can be rendered with the [Grasp Renderer](https://github.com/jonashein/grasp_renderer).

## Table of Content

- [Setup](#setup)
- [Demo](#demo)
- [Generate grasp templates](#generate-grasp-templates)
- [Generate grasps](#generate-grasps)
- [Citations](#citations)

## Setup

### Prerequisites

This package uses a ROS [interface](https://github.com/graspit-simulator/graspit_commander) for the GraspIt! simulator.
To install and setup this interface follow the instructions at https://github.com/graspit-simulator/graspit_interface.

### Download and install code

```
git clone https://github.com/jonashein/grasp_generator.git
cd grasp_generator
python setup.py install --user --graspit_dir=$GRASPIT
```

The MANO hand model will be automatically copied to `$GRASPIT` directory during the installation. 
To copy a model without the code installation use the command:
```
python setup.py --copy_model_only --graspit_dir=$GRASPIT
```

## Demo
For your convenience, we have included exemplary grasp templates for our drill model in [examples/drill_grasp_templates.txt](examples/drill_grasp_templates.txt).
<!-- as well as 
[exemplary grasps](examples/drill_grasps.txt) which were generated using this grasp generator.
These grasps where generated for the drill model which we used in our synthetic and real datasets. 

TODO download link for drill model
-->

## Generate grasp templates

Start the [GraspIt!](http://graspit-simulator.github.io/) simulator and load the 3D model you wish to generate grasps for:
```File -> Import Object...```.

Load the MANO hand model: ```File -> Import Robot...```. 

To generate a grasp template, manually the hand with the object such that they resemble a natural grasp.

Use the ```Grasp -> Auto Open``` and ```Grasp -> Auto Grasp``` 
functions to automatically open and close the hand as needed. 
Also, temporarily disabling the collision system can simplify the alignment.

Capture the grasp via ```Database -> Grasp Capture... -> Capture```.
Repeat these steps until a sufficient number of grasp templates are captured.

Save the recorded grasp templates via ```Save to file...```.

## Generate grasps

Start [ROS master](http://wiki.ros.org/roscore) in one terminal:
```
roscore
```

Then in a second terminal start generator, which will augment the grasp templates and verify their physical plausibility via collision detection:
```
python -m mano_grasp.generate_grasps --models PATH_TO_3D_OBJECT --grasps_file PATH_TO_GRASP_TEMPLATES --path_out PATH_TO_DATASET
```

Use the `-- help` flag to see all available options:
```
python -m mano_grasp.generate_grasps --help
```

## Citations

If you find this code useful for your research, please consider citing:

* the publication that this code was adapted for
```
@inproceedings{hein21_towards,
  title     = {Towards Markerless Surgical Tool and Hand Pose Estimation},
  author    = {Hein, Jonas and Seibold, Matthias and Bogo, Federica and Farshad, Mazda and Pollefeys, Marc and Fürnstahl, Philipp and Navab, Nassir},
  booktitle = {IPCAI},
  year      = {2021}
}
```

* the publication it builds upon and that this code was originally developed for
```
@inproceedings{hasson19_obman,
  title     = {Learning joint reconstruction of hands and manipulated objects},
  author    = {Hasson, Yana and Varol, G{\"u}l and Tzionas, Dimitris and Kalevatykh, Igor and Black, Michael J. and Laptev, Ivan and Schmid, Cordelia},
  booktitle = {CVPR},
  year      = {2019}
}
```
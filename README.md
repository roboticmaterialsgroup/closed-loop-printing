# Closed-loop printing system


This repository contains the source code for our paper:  
[Vision-based FDM Printing for Fabricating Airtight Soft Actuators](https://arxiv.org/abs/2312.01135)

7th IEEE-RAS International Conference on Soft Robotics (Robosoft 2024)  
Yijia Wu,${\dagger}$ Zilin Dai,${\dagger}$ Haotian Liu, Lehong Wang, and Markus P. Nemitz  
(${\dagger}$ These authors contribute equally to this work)

This paper propose a low-cost approach to improve the print quality of desktop fused deposition modeling by adding a webcam to the printer to monitor the printing process and detect and correct defects such as holes or gaps. We demonstrate that our approach improves the air-tightness of printed pneumatic actuators while reducing the need for fine-tuning printing parameters. Our approach presents a new option for robustly fabricating airtight, soft robotic actuators.

<p align="center">
<img src="pictures/robosoft_fig1_v6.png" height="350rm">
</p>
<p align="center">
<img src="pictures/workflow_diagram.png" height="250rm">
</p>

## Hardware setup
**FDM Printer:** Prusa MK3S  
**Enclosure:** Prusa enclosure  
**Camera:** ELP IMX317USB 4K Webcam  
**Lights:** Logitech Litra Glow sources

<p align="center">
  <img src="pictures/robosoft_fig5_v1.png" height="200rm">
</p>


1. Properly setup the FDM printer. At least it should be able to print parts with TPE filament. Then this system can help with improving the airtightness.
2. If the same camera and light sources are used, print `camera_holder`, and two `led_light_mount` in the `CAD` folder. Otherwise, prepare your own mounts for camera and lights
3. Mount camera on the printer, and lights on the z-axis slider as shown in the image
4. Put the printer inside a fully blackout enclosure
5. Connect camera and printer to a computer


## Software setup
1. Clone this repository and [Printrun](https://github.com/kliment/Printrun)
2. Clone the `printrun` folder, `printcore.py`, and `setup.py` from the Printrun repository into this repository
3. Install required libraries
    * python 3.11
    * pyserial 3.5
    * opencv 4.7.0

## How to use

1. Camera instrinsic and extrinsic calibration
2. Put parsed G-code files into a self-contained directory named "gcode"
    * Two gcode files are required for running this code, one parsed with z-wipping pattern, one without
3. Create directories for storing layerwise parsed g_code files, images, and log files
4. Change the camera matrix, path, parameters in `iron_detect_and_correct.py`
5. Run `iron_detect_and_correct.py`
# Wing Propeller Interaction
This is the python project  for my master thesis @ Bauhaus Luftfahrt <**Wing Propeller Interaction for Novel Aircraft Concepts**>

**Time**: Jul. 2023 - Jan. 2024

**Author**: Chang Xu[^1].

With Special Thanks to my Supervisors during my thesis

**Supervisor**: Prof. Dr. Mirko Hornung[^1][^2], Dr. Yiyuan Ma[^2], Alexandros Lessis[^2], Fanglin Yu[^1]
[^1]: TUM.
[^2]: Bauhaus Luftfahrt e.V.

![alt text](https://img.airliners.de/2021/02/do328eco-ynO4D9__wide__970)

## Instructions on Installation of Python Module needed by this project
In order to succesfully run this project, several modules should be installed at first.

**Anaconda** is recommended for managing all the modules.
* OpenVSP API 3.26.1 [DownLoad Link](https://openvsp.org/download_old.php)
  1. After download, Navigate to ***./OpenVSP-3.26.1-win64/python/*** folder. Install **utilities, degen_geom, openvsp, CHARM, AvlPy** one by one.
  Take utilities for example, first navigate to the **utilities** folder using Anaconda Prompt, then excute:
  ```bash
  python setup.py build
  ```
  After building the package, install the package by:
  ```bash
  python setup.py install
  ```
  2. After succussfully installed these five packages, navigate to the anaconda environment folder, locate **site-packages** folder. Copy **utilities, utilities.egg-info, openvsp,
     openvsp.egg-info... etc.** in TOTAL 10 folders to **site-packages** folder.
  3. Delete two folders called **charm-0.1.0-py3.6.egg & openvsp-3.26.1-py3.6.egg**, two files called **degen_geom-0.0.1-py3.6.egg & utilities-0.1.0-py3.6.egg** in **site-packages** folder
  4. Finally copy three exe files called **vspaero.exe, vspslicer.exe, vspviewer.exe** under OpenVSP download folder to Anaconda env folder.
  5. Check all installed packages in Pycharm :)
  ```Python
  Import openvsp as vsp
  vsp.VSPCheckSetup()
  ```
  > **Note:** Only OpenVSP 3.26.1 is tested for this project. Other Versions of OpenVSP maybe cause conflicts!
* GMSH Api [Module Homepage](https://pypi.org/project/gmsh/)
  ```bash
  pip install --upgrade gmsh
  ```
* xmltodict [Module Homepage](https://pypi.org/project/xmltodict/)
  ```bash
  pip install xmltodict
  ```
* XRotor Api [Module Homepage](https://pypi.org/project/xrotor/)
  Since I have altered the XRotor API source code to get the far-field slip-stream induced speed output. The XRotor API is already compiled and ready for use.
  Just copy the **XRotor_API** folder in this GITHUB project to Anaconda environment **site-packages** folder in your computer.

  
## Task Lists
 - [x] Development of CPACS & OpenVSP interface
 - [x] OpenVSP - Gmsh - SU<sup>2</sup>
 - [ ] XFoil - XRotor - LiftingLine
 - [ ] Wing Optimization
 - [ ] Integration to the pre-existing aircraft design loop @ Bauhaus Luftfahrt e.V
 - [ ] Thesis Writing
 - [ ] :tada:

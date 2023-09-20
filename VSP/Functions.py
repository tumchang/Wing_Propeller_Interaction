"""
============================================================================
This script consists of all the functions which are going
to be used when using OpenVSP API
(adding geometries & plot results)
-------------
Author: Chang Xu   TUM   03739064  July.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""

import openvsp as vsp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import shutil
import subprocess
import gmsh
import time

"""
============================================================================
Geometry Setting section
============================================================================
"""


# ==================================
#    Fuselage Geometry Setting
# ==================================
def set_xsec_skin_left(fuse_id, position, index,
                       Angle=0.0, Strength=1.0,
                       CurveSet=1, Curve=0.0):
    if position == 'Bottom':
        vsp.SetParmVal(fuse_id, 'TBSym', 'XSec_' + index, 0)
    vsp.SetParmVal(fuse_id, position + 'LAngle', 'XSec_' + index, Angle)
    vsp.SetParmVal(fuse_id, position + 'LStrength', 'XSec_' + index, Strength)
    vsp.SetParmVal(fuse_id, position + 'LCurveSet', 'XSec_' + index, CurveSet)
    vsp.SetParmVal(fuse_id, position + 'LCurve', 'XSec_' + index, Curve)


def set_xsec_skin_right(fuse_id, position, index,
                        Angle=0.0, Strength=1.0,
                        CurveSet=1, Curve=0.0):
    if position == 'Bottom':
        vsp.SetParmVal(fuse_id, 'TBSym', 'XSec_' + index, 0)
    vsp.SetParmVal(fuse_id, position + 'RAngle', 'XSec_' + index, Angle)
    vsp.SetParmVal(fuse_id, position + 'RStrength', 'XSec_' + index, Strength)
    vsp.SetParmVal(fuse_id, position + 'RCurveSet', 'XSec_' + index, CurveSet)
    vsp.SetParmVal(fuse_id, position + 'RCurve', 'XSec_' + index, Curve)


def add_fuse():
    print("--> Creating Fuselage")
    # Add Fuselage
    fuse_id = vsp.AddGeom("FUSELAGE")

    # Set number of Tess in W direction
    vsp.SetParmVal(fuse_id, "Tess_W", "Shape", 25)

    # Set length of the Whole fuselage
    vsp.SetParmVal(fuse_id, 'Length', 'Design', 21.23)

    # Insert X-section (type2 = ellipse)
    vsp.InsertXSec(fuse_id, 1, 2)
    vsp.InsertXSec(fuse_id, 1, 2)
    vsp.InsertXSec(fuse_id, 1, 2)
    vsp.CutXSec(fuse_id, 4)
    vsp.Update()

    # Section 0 X-Section Skinning------------------------------------------
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '0',
                       Angle=90, Strength=1.0,
                       CurveSet=1, Curve=-12.61)
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '0',
                       Angle=90, Strength=1,
                       CurveSet=1, Curve=-12.17)
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '0',
                       Angle=90, Strength=0.39,
                       CurveSet=1, Curve=-10.00)

    # Section 1 X-Section Skinning------------------------------------------
    group = 'XSec_1'
    vsp.SetParmVal(fuse_id, 'SectTess_U', group, 21)
    vsp.SetParmVal(fuse_id, 'XLocPercent', group, 0.1015)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', group, 0.0302)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_1', 2.230)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_1', 2.194)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '1',
                       Angle=34.35, Strength=1.0,
                       CurveSet=1, Curve=0)
    set_xsec_skin_right(fuse_id, 'Top', '1',
                        Angle=34.35, Strength=0.54,
                        CurveSet=1, Curve=-0.22)
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '1',
                       Angle=7.83, Strength=1,
                       CurveSet=1, Curve=-0.43)
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '1',
                       Angle=0, Strength=1,
                       CurveSet=1, Curve=0)

    # Section 2 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_2', 11)
    vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_2', 0.2146)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_2', 0.0428)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_2', 2.446)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_2', 2.696)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '2',
                       Angle=0, Strength=1.0,
                       CurveSet=1, Curve=0)
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '2',
                       Angle=0, Strength=1,
                       CurveSet=1, Curve=0)
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '2',
                       Angle=0, Strength=1,
                       CurveSet=1, Curve=0)

    # Section 3 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_3', 11)
    vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_3', 0.5611)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_3', 0.0417)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_3', 2.5)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_3', 2.63)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '3',
                       Angle=0, Strength=1.0,
                       CurveSet=0)
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '3',
                       Angle=0, Strength=1,
                       CurveSet=0)
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '3',
                       Angle=0, Strength=1,
                       CurveSet=0)

    # Section 4 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_4', 8)
    vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_4', 0.6446)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_4', 0.0417)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_4', 2.42)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_4', 2.6)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '4',
                       Angle=0, Strength=1.0,
                       CurveSet=0)
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '4',
                       Angle=-7.83, Strength=1,
                       CurveSet=0)
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '4',
                       Angle=0, Strength=1,
                       CurveSet=0)

    # Section 5 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_5', 16)
    vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_5', 0.98841)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_5', 0.077)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_5', 0.2027)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_5', 0.35)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '5',
                       Angle=-5.0, Strength=1.0,
                       CurveSet=1, Curve=0)
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '5',
                       Angle=-11.74, Strength=1,
                       CurveSet=0)
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '5',
                       Angle=-19.57, Strength=1,
                       CurveSet=0)

    # Section 6 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_6', 9)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_6', 0.077)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '6',
                       Angle=-90, Strength=1.0,
                       CurveSet=1, Curve=0)
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '6',
                       Angle=-90, Strength=1,
                       CurveSet=1, Curve=-5.0)
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '6',
                       Angle=-90, Strength=0.57,
                       CurveSet=1, Curve=0)

    return


# ==================================
#    VT Geometry Setting
# ==================================
def add_vt():
    print("--> Creating Vertical Tail")
    # Add Wing
    wing_id = vsp.AddGeom('WING')
    vsp.SetGeomName(wing_id, 'Vertical Tail')

    # Insert Sections
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)

    # Cut The Original Section
    vsp.CutXSec(wing_id, 1)

    # Change Driver
    vsp.SetDriverGroup(wing_id, 1, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
    vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)

    # Change Parameters in 1st Section
    vsp.SetParmVal(wing_id, "Span", 'XSec_1', 1.0)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_1', 6)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_1', 3.65)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_1', 70)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_1', 4)

    # Update
    vsp.Update()

    # Change Parameters in 2nd Section
    vsp.SetParmVal(wing_id, "Span", 'XSec_2', 2.9)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_2', 3.65)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_2', 2.35)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_2', 40)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_2', 6)

    # Update
    vsp.Update()

    # Change Parameters in 3rd Section
    vsp.SetParmVal(wing_id, "Span", 'XSec_3', 0.6)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_3', 2.35)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_3', 1.65)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_3', 55)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_3', 2)

    # Update
    vsp.Update()

    # Change the position and rotation angle of the VT
    vsp.SetParmVal(wing_id, 'X_Rel_Location', 'XForm', 13.6)
    vsp.SetParmVal(wing_id, 'Z_Rel_Location', 'XForm', 1.8)
    vsp.SetParmVal(wing_id, 'X_Rel_Rotation', 'XForm', 90)
    vsp.SetParmVal(vsp.FindParm(wing_id, "Sym_Planar_Flag", "Sym"), 0.0)

    print("--> Vertical Tail Created")

    return


# ==================================
#    HT Geometry Setting
# ==================================
def add_ht():
    print("--> Creating Horizontal Tail")
    # Add Wing
    wing_id = vsp.AddGeom('WING')
    vsp.SetGeomName(wing_id, 'Horizontal Tail')

    # Change Driver
    vsp.SetDriverGroup(wing_id, 1, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
    vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)

    # Change Parameters in 1st Section
    vsp.SetParmVal(wing_id, "Span", 'XSec_1', 3.3)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_1', 1.75)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_1', 1.00)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_1', 10)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_1', 21)

    # Update
    vsp.Update()

    # Change the position and rotation angle of the VT
    vsp.SetParmVal(wing_id, 'X_Rel_Location', 'XForm', 18.9)
    vsp.SetParmVal(wing_id, 'Z_Rel_Location', 'XForm', 5.5)

    print("--> Horizontal Tail Created")

    return


# ==================================
#    Wing Geometry Setting
# ==================================
def add_wing():
    print("--> Creating Main Wing")
    # Add Wing
    wing_id = vsp.AddGeom('WING')
    vsp.SetGeomName(wing_id, 'Wing')

    # Insert Sections
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)

    # Cut The Original Section
    vsp.CutXSec(wing_id, 1)

    # Change Driver
    vsp.SetDriverGroup(wing_id, 1, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
    vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)

    # Change Parameters in 1st Section
    vsp.SetParmVal(wing_id, "Span", 'XSec_1', 1.18750)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_1', 2.65)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_1', 2.65)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_1', 0)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_1', 5)

    # Update
    vsp.Update()

    # Change Parameters in 2nd Section
    vsp.SetParmVal(wing_id, "Span", 'XSec_2', 0.34375)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_2', 2.65)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_2', 2.33)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_2', 40)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_2', 4)

    # Update
    vsp.Update()

    # Change Parameters in 3rd Section
    vsp.SetParmVal(wing_id, "Span", 'XSec_3', 2.40)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_3', 2.33)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_3', 2.33)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_3', 0)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_3', 16)

    # Update
    vsp.Update()

    # Change Parameters in 4th Section
    vsp.SetParmVal(wing_id, "Span", 'XSec_4', 5.5)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_4', 2.33)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_4', 1.49)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_4', 6)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_4', 26)

    # Update
    vsp.Update()

    # Change Parameters in 5th Section
    vsp.SetParmVal(wing_id, "Span", 'XSec_5', 1.09)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_5', 1.49)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_5', 0.17)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_5', 50)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_5', 15)

    # Update
    vsp.Update()

    # Move the Position of the Wing
    vsp.SetParmVal(wing_id, 'X_Rel_Location', 'XForm', 7.29)
    vsp.SetParmVal(wing_id, 'Z_Rel_Location', 'XForm', 2.5)

    # Update
    vsp.Update()

    # Change Airfoil in Each Section
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_0', 0.15)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_1', 0.15)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_2', 0.15)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_3', 0.15)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_4', 0.15)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_5', 0.15)
    # Camber
    vsp.SetParmVal(wing_id, 'Camber', 'XSecCurve_0', 0.02)
    vsp.SetParmVal(wing_id, 'Camber', 'XSecCurve_1', 0.02)
    vsp.SetParmVal(wing_id, 'Camber', 'XSecCurve_2', 0.02)
    vsp.SetParmVal(wing_id, 'Camber', 'XSecCurve_3', 0.02)
    vsp.SetParmVal(wing_id, 'Camber', 'XSecCurve_4', 0.02)
    vsp.SetParmVal(wing_id, 'Camber', 'XSecCurve_5', 0.02)

    print("--> Main Wing Created")

    return


# ==================================
#    Propeller Geometry Setting
# ==================================

# Default input of the parameters are zero
def add_prop(x_position=0, y_position=0, z_position=0, diameter=0, unsteady=0, rev_flag=0):
    # Add Prop Geometry and return its ID
    prop_id = vsp.AddGeom("PROP")

    # Get the diameter of the Prop and change it
    diameter_id = vsp.GetParm(prop_id, "Diameter", "Design")
    vsp.SetParmVal(diameter_id, diameter)

    # Get the number of blades and change it to 5 blades
    nblade_id = vsp.GetParm(prop_id, "NumBlade", "Design")
    vsp.SetParmVal(nblade_id, 5)

    # Change PropMode to Disk to enable Actuator disk solver
    if unsteady == 1:
        vsp.SetParmVal(prop_id, 'PropMode', 'Design', 0)  # Blade
    else:
        vsp.SetParmVal(prop_id, 'PropMode', 'Design', 2)  # Actuator Disk

    if rev_flag == 1:
        vsp.SetParmVal(prop_id, "ReverseFlag", "Design", 1)
    else:
        pass

    # Get mesh density and change to u = 50 and w = 25
    u_id = vsp.GetParm(prop_id, "Tess_U", "Shape")
    vsp.SetParmVal(u_id, 50)
    w_id = vsp.GetParm(prop_id, "Tess_W", "Shape")
    vsp.SetParmVal(w_id, 25)

    # Insert new cross-section(Don't forget to delete the last section)
    vsp.InsertXSec(prop_id, 1, vsp.XS_FILE_AIRFOIL)
    vsp.InsertXSec(prop_id, 2, vsp.XS_FILE_AIRFOIL)
    vsp.InsertXSec(prop_id, 3, vsp.XS_FILE_AIRFOIL)
    vsp.InsertXSec(prop_id, 4, vsp.XS_FILE_AIRFOIL)
    vsp.InsertXSec(prop_id, 5, vsp.XS_FILE_AIRFOIL)
    vsp.CutXSec(prop_id, 7)

    # Change cross-section surface
    xsec_surf_0 = vsp.GetXSecSurf(prop_id, 0)
    vsp.ChangeXSecShape(xsec_surf_id=xsec_surf_0, xsec_index=0, type=vsp.XS_CIRCLE)

    xsec_surf_1 = vsp.GetXSecSurf(prop_id, 1)
    vsp.ChangeXSecShape(xsec_surf_id=xsec_surf_1, xsec_index=1, type=vsp.XS_FILE_AIRFOIL)

    # XYZ relative position of the propeller
    vsp.SetParmVal(prop_id, 'X_Rel_Location', 'XForm', x_position)
    vsp.SetParmVal(prop_id, 'Y_Rel_Location', 'XForm', y_position)
    vsp.SetParmVal(prop_id, 'Z_Rel_Location', 'XForm', z_position)

    # Reverse Propeller
    # vsp.SetParmVal(prop_id, "Reverse_Flag", "PropGeom", 1.0)

    # Get the cross-section surface of
    xsec_surf_2 = vsp.GetXSecSurf(prop_id, 2)
    xsec_surf_3 = vsp.GetXSecSurf(prop_id, 3)
    xsec_surf_4 = vsp.GetXSecSurf(prop_id, 4)
    xsec_surf_5 = vsp.GetXSecSurf(prop_id, 5)
    xsec_surf_6 = vsp.GetXSecSurf(prop_id, 6)

    xsec_0 = vsp.GetXSec(xsec_surf_id=xsec_surf_0, xsec_index=0)
    xsec_1 = vsp.GetXSec(xsec_surf_id=xsec_surf_1, xsec_index=1)
    xsec_2 = vsp.GetXSec(xsec_surf_2, 2)
    xsec_3 = vsp.GetXSec(xsec_surf_3, 3)
    xsec_4 = vsp.GetXSec(xsec_surf_4, 4)
    xsec_5 = vsp.GetXSec(xsec_surf_5, 5)
    xsec_6 = vsp.GetXSec(xsec_surf_6, 6)

    # Definition of Cross-section position(using radius fraction r/R)
    xsec_radiusfrac_1 = vsp.GetXSecParm(xsec_id=xsec_1, name="RadiusFrac")
    vsp.SetParmVal(xsec_radiusfrac_1, 0.3)
    xsec_radiusfrac_2 = vsp.GetXSecParm(xsec_2, "RadiusFrac")
    vsp.SetParmVal(xsec_radiusfrac_2, 0.5)
    xsec_radiusfrac_3 = vsp.GetXSecParm(xsec_3, "RadiusFrac")
    vsp.SetParmVal(xsec_radiusfrac_3, 0.7)
    xsec_radiusfrac_4 = vsp.GetXSecParm(xsec_4, "RadiusFrac")
    vsp.SetParmVal(xsec_radiusfrac_4, 0.9)
    xsec_radiusfrac_5 = vsp.GetXSecParm(xsec_5, "RadiusFrac")
    vsp.SetParmVal(xsec_radiusfrac_5, 0.95)

    # Define the airfoil in each cross-section
    vsp.ReadFileAirfoil(xsec_id=xsec_1, file_name="D:/OpenVSP-3.26.1-win64/airfoil/N0012_VSP.af")
    vsp.ReadFileAirfoil(xsec_id=xsec_2, file_name="D:/OpenVSP-3.26.1-win64/airfoil/N0012_VSP.af")
    vsp.ReadFileAirfoil(xsec_id=xsec_3, file_name="D:/OpenVSP-3.26.1-win64/airfoil/N0012_VSP.af")
    vsp.ReadFileAirfoil(xsec_id=xsec_4, file_name="D:/OpenVSP-3.26.1-win64/airfoil/N0012_VSP.af")
    vsp.ReadFileAirfoil(xsec_id=xsec_5, file_name="D:/OpenVSP-3.26.1-win64/airfoil/N0012_VSP.af")
    vsp.ReadFileAirfoil(xsec_id=xsec_6, file_name="D:/OpenVSP-3.26.1-win64/airfoil/N0012_VSP.af")

    # Setting Chord Curve of the Propeller
    vsp.SetPCurve(geom_id=prop_id, pcurveid=0,
                  tvec=(
                      0.2, 0.25, 0.3, 0.35, 0.39999999999999997, 0.45, 0.5, 0.55, 0.6, 0.65,
                      0.7000000000000001, 0.75, 0.8, 0.8666666666666667, 0.9333333333333333, 1.0
                  ),
                  valvec=(
                      0.08, 0.094, 0.10719999999999999, 0.12, 0.13058461538461535, 0.1409230769230769,
                      0.1493263541192535, 0.1577296313154301, 0.16419772416932177, 0.1676816021847974,
                      0.17116548020027306, 0.1716651433773327, 0.16813156121984524, 0.16,
                      0.15153846153846157, 0.13
                  ),
                  newtype=vsp.CEDIT)

    # Split of control points
    vsp.PCurveSplit(geom_id=prop_id, pcurveid=1, tsplit=0.3)
    vsp.PCurveSplit(geom_id=prop_id, pcurveid=1, tsplit=0.5)
    vsp.PCurveSplit(geom_id=prop_id, pcurveid=1, tsplit=0.6)
    vsp.PCurveSplit(geom_id=prop_id, pcurveid=1, tsplit=0.7)
    vsp.PCurveSplit(geom_id=prop_id, pcurveid=1, tsplit=0.9)
    vsp.PCurveDeletePt(geom_id=prop_id, pcurveid=1, indx=5)

    # Setting twist angle of the Propeller in each control points(section）
    tw_0 = vsp.GetParm(geom_id=prop_id, name="tw_0", group="Twist")
    tw_1 = vsp.GetParm(geom_id=prop_id, name="tw_1", group="Twist")
    tw_2 = vsp.GetParm(geom_id=prop_id, name="tw_2", group="Twist")
    tw_3 = vsp.GetParm(geom_id=prop_id, name="tw_3", group="Twist")
    tw_4 = vsp.GetParm(geom_id=prop_id, name="tw_4", group="Twist")
    tw_5 = vsp.GetParm(geom_id=prop_id, name="tw_5", group="Twist")
    tw_6 = vsp.GetParm(geom_id=prop_id, name="tw_6", group="Twist")
    vsp.SetParmVal(tw_0, 40)
    vsp.SetParmVal(tw_1, 38)
    vsp.SetParmVal(tw_2, 35)
    vsp.SetParmVal(tw_3, 31)
    vsp.SetParmVal(tw_4, 25)
    vsp.SetParmVal(tw_5, 23)
    vsp.SetParmVal(tw_6, 20)

    # aop = vsp.PCurveGetTVec(prop_id, 1)
    # aov = vsp.PCurveGetValVec(prop_id, 1)

    vsp.Update()

    return


def add_fuse_new():
    print("--> Creating Fuselage")
    # Add Fuselage
    fuse_id = vsp.AddGeom("FUSELAGE")

    # Set number of Tess in W direction
    vsp.SetParmVal(fuse_id, "Tess_W", "Shape", 33)

    # Set length of the Whole fuselage
    vsp.SetParmVal(fuse_id, 'Length', 'Design', 23.31)

    # Insert X-section (type2 = ellipse, type4 = rounded_Rectangle)
    vsp.InsertXSec(fuse_id, 1, 2)
    vsp.InsertXSec(fuse_id, 1, 2)
    vsp.InsertXSec(fuse_id, 1, 2)
    vsp.InsertXSec(fuse_id, 1, 2)
    vsp.InsertXSec(fuse_id, 7, 2)
    vsp.CutXSec(fuse_id, 5)
    vsp.Update()

    # Section 0 X-Section Skinning------------------------------------------
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '0',
                       Angle=90, Strength=0.15,
                       )
    set_xsec_skin_right(fuse_id, 'Top', '0',
                        Angle=90, Strength=1,
                        )
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '0',
                       Angle=90, Strength=0.5,
                       )
    set_xsec_skin_right(fuse_id, 'Right', '0',
                        Angle=90, Strength=1,
                        )
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '0',
                       Angle=90, Strength=0.5,
                       )
    set_xsec_skin_right(fuse_id, 'Bottom', '0',
                        Angle=90, Strength=1.0,
                        )

    # Section 1 X-Section Skinning------------------------------------------
    group = 'XSec_1'
    vsp.SetParmVal(fuse_id, 'SectTess_U', group, 17)
    vsp.SetParmVal(fuse_id, 'XLocPercent', group, 0.14)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', group, 0.03218)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_1', 2.6)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_1', 2.5)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '1',
                       Angle=0, Strength=1.17,
                       )
    set_xsec_skin_right(fuse_id, 'Top', '1',
                        Angle=34.35, Strength=1.0,
                        )
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '1',
                       Angle=0, Strength=1.0,
                       )
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '1',
                       Angle=0, Strength=1,
                       )

    # Section 2 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_2', 11)
    vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_2', 0.25)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_2', 0.03218)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_2', 2.6)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_2', 2.5)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '2',
                       Angle=0, Strength=1.0,
                       )
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '2',
                       Angle=0, Strength=1,
                       )

    # Section 3 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_3', 9)
    vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_3', 0.375)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_3', 0.03218)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_3', 2.6)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_3', 2.5)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '3',
                       Angle=0, Strength=1.0,
                       CurveSet=0)
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '3',
                       Angle=0, Strength=1,
                       CurveSet=0)

    # Section 4 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_4', 17)
    vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_4', 0.5)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_4', 0.03218)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_4', 2.6)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_4', 2.5)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '4',
                       Angle=0, Strength=1.0,
                       CurveSet=0)
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '4',
                       Angle=0, Strength=1.0,
                       CurveSet=0)

    # Section 5 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_5', 17)
    vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_5', 0.62205)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_5', 0.03218)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_5', 2.6)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_5', 2.5)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '5',
                       Angle=0, Strength=1.0,
                       )
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '5',
                       Angle=0, Strength=1,
                       CurveSet=0)
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '5',
                       Angle=0, Strength=1,
                       CurveSet=0)

    # Section 6 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_6', 17)
    vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_6', 0.80867)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_6', 0.04290)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_6', 1.45459)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_6', 1.7)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '6',
                       Angle=-4, Strength=1.0,
                       )
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '6',
                       Angle=-7.83, Strength=1,
                       )
    # Bottom
    set_xsec_skin_left(fuse_id, 'Bottom', '6',
                       Angle=-11.74, Strength=1.0,
                       )

    # Section 7 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_7', 18)
    vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_7', 0.99528)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_7', 0.06156)
    # vsp.SetParmVal(fuse_id, 'RoundedRect_Width', 'XSecCurve_7', 0.15)
    # vsp.SetParmVal(fuse_id, 'RoundedRect_Height', 'XSecCurve_7', 0.25)
    vsp.SetParmVal(fuse_id, 'Ellipse_Width', 'XSecCurve_7', 0.15)
    vsp.SetParmVal(fuse_id, 'Ellipse_Height', 'XSecCurve_7', 0.25)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '7',
                       Angle=-45, Strength=0.75,
                       )
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '7',
                       Angle=-45, Strength=0.75,
                       )

    # Section 8 X-Section Skinning------------------------------------------
    vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_8', 8)
    vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_8', 0.06349)
    # Top
    set_xsec_skin_left(fuse_id, 'Top', '8',
                       Angle=-45, Strength=0.75,
                       )
    # Right
    set_xsec_skin_left(fuse_id, 'Right', '8',
                       Angle=-45, Strength=0.75,
                       )
    return


def add_wing_new():
    print("--> Creating Main Wing")
    # Add Wing
    wing_id = vsp.AddGeom('WING')
    vsp.SetGeomName(wing_id, 'Wing')

    # Insert Sections
    vsp.InsertXSec(wing_id, 1, vsp.XS_SIX_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_SIX_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_SIX_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_SIX_SERIES)

    # Cut The Original Section
    vsp.CutXSec(wing_id, 1)
    vsp.SetParmVal(wing_id, "Tess_W", "Shape", 45)

    # Change Driver
    vsp.SetDriverGroup(wing_id, 1, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
    vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)

    # Change Parameters in 1st Section
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_1', 8)
    vsp.SetParmVal(wing_id, "Span", 'XSec_1', 1.45)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_1', 2.6)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_1', 2.35)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_1', 6.21307)
    vsp.SetParmVal(wing_id, "Sweep_Location", 'XSec_1', 0.25)

    # Update
    vsp.Update()

    # Change Parameters in 2nd Section
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_2', 21)
    vsp.SetParmVal(wing_id, "Span", 'XSec_2', 2.0)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_2', 2.35)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_2', 2.20)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_2', 0)
    vsp.SetParmVal(wing_id, "Sweep_Location", 'XSec_2', 0.25)

    # Update
    vsp.Update()

    # Change Parameters in 3rd Section
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_3', 31)
    # vsp.SetParmVal(wing_id, "InCluster", 'XSec_3', 0.4)
    vsp.SetParmVal(wing_id, "Span", 'XSec_3', 5.9)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_3', 2.2)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_3', 1.4)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_3', 6)
    vsp.SetParmVal(wing_id, "Sweep_Location", 'XSec_3', 0)

    # Update
    vsp.Update()

    # Change Parameters in 4th Section
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_4', 16)
    vsp.SetParmVal(wing_id, "Span", 'XSec_4', 1.14)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_4', 1.4)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_4', 0.40376)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_4', 32)
    vsp.SetParmVal(wing_id, "Sweep_Location", 'XSec_4', 0.25)

    # Update
    vsp.Update()

    # Move the Position of the Wing
    vsp.SetParmVal(wing_id, 'X_Rel_Location', 'XForm', 8.2)
    vsp.SetParmVal(wing_id, 'Z_Rel_Location', 'XForm', 2.35)

    # Update
    vsp.Update()

    # Change Airfoil in Each Section
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_0', 0.12)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_1', 0.12)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_2', 0.10)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_3', 0.10)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_4', 0.08)

    # IdealCl
    vsp.SetParmVal(wing_id, 'IdealCl', 'XSecCurve_0', 0.2)
    vsp.SetParmVal(wing_id, 'IdealCl', 'XSecCurve_1', 0.2)
    vsp.SetParmVal(wing_id, 'IdealCl', 'XSecCurve_2', 0.2)
    vsp.SetParmVal(wing_id, 'IdealCl', 'XSecCurve_3', 0.2)
    vsp.SetParmVal(wing_id, 'IdealCl', 'XSecCurve_4', 0.2)

    print("--> Main Wing Created")

    return


def add_vt_new():
    print("--> Creating Vertical Tail")
    # Add Wing
    wing_id = vsp.AddGeom('WING')
    vsp.SetGeomName(wing_id, 'Vertical Tail')

    # Insert Sections
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)

    # Cut The Original Section
    vsp.CutXSec(wing_id, 1)
    vsp.Update()

    # Change the position and rotation angle of the VT
    vsp.SetParmVal(wing_id, 'X_Rel_Location', 'XForm', 13.4)
    vsp.SetParmVal(wing_id, 'Z_Rel_Location', 'XForm', 2.1)
    vsp.SetParmVal(wing_id, 'X_Rel_Rotation', 'XForm', 90)
    vsp.SetParmVal(wing_id, 'Z_Rel_Rotation', 'XForm', -5.435)
    vsp.SetParmVal(vsp.FindParm(wing_id, "Sym_Planar_Flag", "Sym"), 0.0)

    # Change Driver
    for i in range(1, 5):
        vsp.SetDriverGroup(wing_id, i, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.SECSWEEP_WSECT_DRIVER)
    vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)

    # Change Parameters in 1st Section
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_1', 9)
    vsp.SetParmVal(wing_id, "Span", 'XSec_1', 1.2)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_1', 8.7)
    vsp.SetParmVal(wing_id, "Sec_Sweep", 'XSec_1', 14)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_1', 77)
    vsp.Update()

    # Change Parameters in 2nd Section
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_2', 6)
    vsp.SetParmVal(wing_id, "Span", 'XSec_2', 0.93333)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_2', 3.80142)
    vsp.SetParmVal(wing_id, "Sec_Sweep", 'XSec_2', 14)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_2', 50.68182)
    vsp.Update()

    # Change Parameters in 3rd Section
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_3', 13)
    vsp.SetParmVal(wing_id, "Span", 'XSec_3', 2.4)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_3', 2.89456)
    vsp.SetParmVal(wing_id, "Sec_Sweep", 'XSec_3', 13.50105)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_3', 34.72727)
    vsp.Update()

    # Change Parameters in 4th Section
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_4', 6)
    vsp.SetParmVal(wing_id, "Span", 'XSec_4', 0.3)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_4', 1.80726)
    vsp.SetParmVal(wing_id, "Sec_Sweep", 'XSec_4', 14)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_4', 59.88636)
    vsp.Update()

    # Change Airfoil in Each Section
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_0', 0.03)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_1', 0.10)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_2', 0.10)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_3', 0.10)
    vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_4', 0.10)
    vsp.Update()

    # Change the Blending of the VT
    vsp.SetParmVal(wing_id, 'InLEMode', 'XSec_1', vsp.BLEND_MATCH_OUT_LE_TRAP)
    vsp.SetParmVal(wing_id, 'InLEStrength', 'XSec_1', 0.3)
    vsp.SetParmVal(wing_id, 'InLEMode', 'XSec_2', vsp.BLEND_MATCH_OUT_LE_TRAP)
    vsp.SetParmVal(wing_id, 'InLEStrength', 'XSec_2', 0.9)
    vsp.SetParmVal(wing_id, 'OutLEMode', 'XSec_3', vsp.BLEND_MATCH_IN_LE_TRAP)
    vsp.SetParmVal(wing_id, 'InLEStrength', 'XSec_3', 1.0)

    print("--> Vertical Tail Created")

    return


def add_ht_new():
    print("--> Creating Horizontal Tail")
    # Add Wing
    wing_id = vsp.AddGeom('WING')
    vsp.SetGeomName(wing_id, 'Horizontal Tail')

    # Add X-Sections
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)
    vsp.InsertXSec(wing_id, 1, vsp.XS_FOUR_SERIES)

    # Cut The Original Section
    vsp.CutXSec(wing_id, 1)
    vsp.Update()

    # Change Driver 1st XSec
    vsp.SetDriverGroup(wing_id, 1, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.SECSWEEP_WSECT_DRIVER)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_1', 4)
    vsp.SetParmVal(wing_id, "Span", 'XSec_1', 0.3)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_1', 1.95)
    vsp.SetParmVal(wing_id, "Sec_Sweep", 'XSec_1', 54.4929)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_1', 8.61932)

    vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)
    vsp.Update()

    # Change Driver 2nd XSec
    vsp.SetDriverGroup(wing_id, 2, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_2', 14)
    vsp.SetParmVal(wing_id, "Span", 'XSec_2', 2.7)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_2', 1.875)
    vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_2', 1.1)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_2', 8.61932)
    vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)
    vsp.Update()

    # Change Driver 3rd XSec
    vsp.SetDriverGroup(wing_id, 3, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.SECSWEEP_WSECT_DRIVER)
    vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_3', 13)
    vsp.SetParmVal(wing_id, "Span", 'XSec_3', 0.4)
    vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_3', 1.1)
    vsp.SetParmVal(wing_id, "Sec_Sweep", 'XSec_3', -5.62)
    vsp.SetParmVal(wing_id, "Sweep", 'XSec_3', 25.87784)
    vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)
    vsp.Update()

    # Change the position and rotation angle of the VT
    vsp.SetParmVal(wing_id, 'X_Rel_Location', 'XForm', 21.5)
    vsp.SetParmVal(wing_id, 'Z_Rel_Location', 'XForm', 5.4)

    # Blending
    vsp.SetParmVal(wing_id, 'OutLEMode', 'XSec_2', vsp.BLEND_MATCH_IN_LE_TRAP)
    vsp.SetParmVal(wing_id, 'OutTEMode', 'XSec_2', vsp.BLEND_MATCH_IN_TE_TRAP)

    print("--> Horizontal Tail Created")

    return


"""
============================================================================
Functional functions
============================================================================
"""


def save_vsp3_file(test_flag, Unsteady_Flag, vsp_model, RPM):
    # Save the model to vsp3 file
    if test_flag == 0:
        current_folder = os.getcwd()
        if Unsteady_Flag == 0:
            vsp_output_case_dir = os.path.join(current_folder, f"Steady/{vsp_model.name}/" + str(RPM))
        else:
            vsp_output_case_dir = os.path.join(current_folder, f"UnSteady/{vsp_model.name}/" + str(RPM))
        if os.path.exists(vsp_output_case_dir):
            print("Directory already exists!")
            shutil.rmtree(vsp_output_case_dir)
            print("Old directory would be removed!")
            os.makedirs(vsp_output_case_dir)
            print("New directory created!")
        else:
            os.makedirs(vsp_output_case_dir)
            print("New directory would be created!")

        print("--> Saving vehicle file to .vsp3 file")
        vsp.WriteVSPFile(vsp_output_case_dir + f'/{vsp_model.name}.vsp3', vsp.SET_ALL)
        print("--> vps3 file saving Completed")
        vsp.Update()

        # TODO: to be deleted
        # # Important (change MultiSolid)
        # tree = ET.parse(vsp_output_case_dir + f'/{vsp_model.name}.vsp3')
        # multi_solids = tree.findall('.//MultiSolid')
        #
        # for multi_solid in multi_solids:
        #     # Modify the Value attribute
        #     multi_solid.set('Value', '1.000000000000000000e+00')
        #
        # tree.write(vsp_output_case_dir + f'/{vsp_model.name}.vsp3')

        # Open vsp3 file with VSP.exe and wait until close (For checking Geometry)
        vsp_exe = subprocess.Popen(
            [
                r"P:\OpenVSP\vsp.exe",
                vsp_output_case_dir + f'/{vsp_model.name}.vsp3'
            ]
        )
        vsp_exe.wait()

    else:
        vsp_output_case_dir = None
        vsp.WriteVSPFile('test.vsp3', vsp.SET_ALL)
        vsp_exe = subprocess.Popen(
            [
                r"P:\OpenVSP\vsp.exe",
                r'C:\Users\chang.xu\wing_propeller_interaction\VSP\test.vsp3'
            ]
        )
        vsp_exe.wait()
        quit()

    return vsp_output_case_dir


def save_cfd_mesh(vsp_model, vsp_output_case_dir):
    # Meshing Values
    max_len = 0.2
    min_len = 0.2
    max_gap = 0.5
    n_circ_seg = 16.0
    growth_ratio = 1.5

    # Set Meshing Values
    vsp.SetCFDMeshVal(vsp.CFD_MAX_EDGE_LEN, max_len)
    vsp.SetCFDMeshVal(vsp.CFD_MIN_EDGE_LEN, min_len)
    vsp.SetCFDMeshVal(vsp.CFD_MAX_GAP, max_gap)
    vsp.SetCFDMeshVal(vsp.CFD_NUM_CIRCLE_SEGS, n_circ_seg)
    vsp.SetCFDMeshVal(vsp.CFD_GROWTH_RATIO, growth_ratio)
    vsp.SetCFDMeshVal(vsp.CFD_FAR_FIELD_FLAG, 0)

    cfd_file_dir = f'{vsp_output_case_dir}/{vsp_model.name}.stl'
    print(f"--> Exporting CFD Mesh file for aircraft")
    print("Might take some time, pls be patient")
    time.sleep(10)
    print("Computer is taking off!!!")

    vsp.SetComputationFileName(vsp.CFD_STL_TYPE, cfd_file_dir)
    vsp.ComputeCFDMesh(3, vsp.CFD_STL_TYPE)
    print("--> CFD Mesh file exported")

    cfd_file_dir = f'{vsp_output_case_dir}/{vsp_model.name}_prop.stl'
    print(f"--> Exporting CFD Mesh file for Propeller")
    vsp.SetComputationFileName(vsp.CFD_STL_TYPE, cfd_file_dir)
    vsp.ComputeCFDMesh(4, vsp.CFD_STL_TYPE)
    print("--> CFD Mesh file exported")


def su2_mesh_generation(vsp_model, vsp_output_case_dir):
    # command_prompt_geo()

    gmsh.initialize()

    # Merge STL file
    gmsh.merge(f'{vsp_output_case_dir}/{vsp_model.name}.stl')

    # # 0=point  1=curve 2=surface 3=volume [(2,1)] means surface has a surface named as "1"
    # surfaces = gmsh.model.getEntities(2)
    #
    # # Add Physical surface, and name it as Plane
    # physical_tag = 1
    # # 2=surface, the first surfaces, tag as 1
    # gmsh.model.addPhysicalGroup(2, [surfaces[0][1]], physical_tag)
    # # Set the physical surface name
    # gmsh.model.setPhysicalName(2, physical_tag, "Plane")

    # Define far-field box parameters
    lc = 1.5

    gmsh.model.geo.addPoint(-20, -30, -15, lc, 1)
    gmsh.model.geo.addPoint(45, -30, -15, lc, 2)
    gmsh.model.geo.addPoint(45, 30, -15, lc, 3)
    gmsh.model.geo.addPoint(-20, 30, -15, lc, 4)
    gmsh.model.geo.addPoint(-20, -30, 15, lc, 5)
    gmsh.model.geo.addPoint(45, -30, 15, lc, 6)
    gmsh.model.geo.addPoint(45, 30, 15, lc, 7)
    gmsh.model.geo.addPoint(-20, 30, 15, lc, 8)

    # Synchronize
    gmsh.model.geo.synchronize()

    gmsh.model.geo.addLine(1, 2, 1)
    gmsh.model.geo.addLine(2, 3, 2)
    gmsh.model.geo.addLine(3, 4, 3)
    gmsh.model.geo.addLine(4, 1, 4)
    gmsh.model.geo.addLine(5, 6, 5)
    gmsh.model.geo.addLine(6, 7, 6)
    gmsh.model.geo.addLine(7, 8, 7)
    gmsh.model.geo.addLine(8, 5, 8)
    gmsh.model.geo.addLine(1, 5, 9)
    gmsh.model.geo.addLine(2, 6, 10)
    gmsh.model.geo.addLine(3, 7, 11)
    gmsh.model.geo.addLine(4, 8, 12)

    # Synchronize
    gmsh.model.geo.synchronize()

    gmsh.model.geo.addCurveLoop([1, 2, 3, 4], 1)
    gmsh.model.geo.addCurveLoop([5, 6, 7, 8], 2)
    gmsh.model.geo.addCurveLoop([1, 10, -5, -9], 3)
    gmsh.model.geo.addCurveLoop([2, 11, -6, -10], 4)
    gmsh.model.geo.addCurveLoop([3, 12, -7, -11], 5)
    gmsh.model.geo.addCurveLoop([4, -12, -8, 9], 6)

    # Synchronize
    gmsh.model.geo.synchronize()

    gmsh.model.geo.addPlaneSurface([1], 2)
    gmsh.model.geo.addPlaneSurface([2], 3)
    gmsh.model.geo.addPlaneSurface([3], 4)
    gmsh.model.geo.addPlaneSurface([4], 5)
    gmsh.model.geo.addPlaneSurface([5], 6)
    gmsh.model.geo.addPlaneSurface([6], 7)

    # Synchronize
    gmsh.model.geo.synchronize()

    # Add Surface
    gmsh.model.geo.addSurfaceLoop([1, 2, 3, 4, 5, 6, 7], 1)

    # Add Volume
    gmsh.model.geo.addVolume([1], 1)

    # Add physical group for the whole aircraft
    # TODO: Add propeller for future actuator disk analysis
    gmsh.model.addPhysicalGroup(2, [1], 1)
    gmsh.model.setPhysicalName(2, 1, "Wing")

    # Add physical surface for the FarField
    gmsh.model.addPhysicalGroup(2, [2, 3, 4, 5, 6, 7], 2)
    gmsh.model.setPhysicalName(2, 2, "FarField")

    # Synchronize
    gmsh.model.geo.synchronize()

    # Meshing
    gmsh.model.mesh.generate(3)

    gmsh.fltk.run()
    # Save the mesh as STL file
    gmsh.option.setNumber("Mesh.SaveAll", 1)
    gmsh.write(f"{vsp_output_case_dir}/{vsp_model.name}.su2")
    # gmsh.write(f"{vsp_output_case_dir}/{vsp_model.name}.geo_unrolled")

    gmsh.finalize()
    print("--> SU2 Mesh File Successfully generated :) ")


def su2_analysis(vsp_model, vsp_output_case_dir):
    su2_exe_dir = fr"P:\SU2-v7.5.1-win64\bin\SU2_CFD"
    cfg_dir = fr'./{vsp_model.name}.cfg'

    # Change directory in command prompt
    shutil.copy(cfg_dir, vsp_output_case_dir)
    os.chdir(f"{vsp_output_case_dir}")

    # Execute the command
    os.system(f"{su2_exe_dir} {vsp_model.name}.cfg")


def command_prompt_geo():
    geo_code = """
    Merge "atr72-500_out.stl";
    Physical Surface("Plane", 1) = {1};
    
    lc = 1; // Characteristic length (you can adjust this value for mesh refinement)
    
    // Define the corner points of the far-field box
    Point(1) = {-30, -30, -20, lc};
    Point(2) = {30, -30, -20, lc};
    Point(3) = {30, 30, -20, lc};
    Point(4) = {-30, 30, -20, lc};
    Point(5) = {-30, -30, 20, lc};
    Point(6) = {30, -30, 20, lc};
    Point(7) = {30, 30, 20, lc};
    Point(8) = {-30, 30, 20, lc};
    
    // Create lines connecting the points
    Line(1) = {1, 2};
    Line(2) = {2, 3};
    Line(3) = {3, 4};
    Line(4) = {4, 1};
    Line(5) = {5, 6};
    Line(6) = {6, 7};
    Line(7) = {7, 8};
    Line(8) = {8, 5};
    Line(9) = {1, 5};
    Line(10) = {2, 6};
    Line(11) = {3, 7};
    Line(12) = {4, 8};
    
    // Create line loops for the faces
    Line Loop(1) = {1, 2, 3, 4};
    Line Loop(2) = {5, 6, 7, 8};
    Line Loop(3) = {1, 10, -5, -9};
    Line Loop(4) = {2, 11, -6, -10};
    Line Loop(5) = {3, 12, -7, -11};
    Line Loop(6) = {4, -12, -8, 9};
    
    // Create surfaces from the line loops
    Plane Surface(2) = {1};
    Plane Surface(3) = {2};
    Plane Surface(4) = {3};
    Plane Surface(5) = {4};
    Plane Surface(6) = {5};
    Plane Surface(7) = {6};
    
    // Create surface loops for the volume
    Surface Loop(1) = {2, 3, 4, 5, 6, 7};
    
    // Create volume
    Volume(1) = {1};
    
    // Define the physical surfaces (if needed)
    Physical Surface("FarField") = {2,3,4,5,6,7};
    
    
    // Meshing
    Mesh 3;
    """
    with open('yourfile.geo', 'w') as file:
        file.write(geo_code)

    command = 'gmsh yourfile.geo'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


"""
============================================================================
Results Plot and Data acquisition section
============================================================================
"""


def add_prop_position_line(y_position=3.5659, diameter=3.264, ax=None):
    ax.axvline(x=y_position, color='r', label='Prop Center')
    ax.axvline(x=y_position + (diameter / 2), color='r', ls='--', label='Prop Tip')
    ax.axvline(x=y_position - (diameter / 2), color='r', ls='--')
    ax.axvline(x=-y_position, color='r')
    ax.axvline(x=-y_position - (diameter / 2), color='r', ls='--')
    ax.axvline(x=-y_position + (diameter / 2), color='r', ls='--')
    return


# ==================================
#   lod results distribution plot
# ==================================
def lod_results_plot(cl_plot_flag=0,
                     cd_plot_flag=0,
                     VoVref_plot_flag=0,
                     Clc_cref_plot_flag=0,
                     Cdc_cref_plot_flag=0,
                     save_directory=os.getcwd()
                     ):
    load_results = vsp.FindLatestResultsID('VSPAERO_Load')

    WingId = np.asarray(vsp.GetIntResults(load_results, "WingId", 0))
    lod_Df = pd.DataFrame({'WingID': WingId})
    # wing_1 = lod_Df['WingID'].value_counts()[1]

    # Getting Average Position of XYZ (Flip second half of the position list)---------------------------
    x_avg = np.asarray(vsp.GetDoubleResults(load_results, "Xavg", 0))
    # x_avg = np.concatenate((np.flip(x_avg[wing_1 // 2:]), x_avg[:wing_1 // 2]))
    lod_Df = lod_Df.assign(Xavg=x_avg)

    y_avg = np.asarray(vsp.GetDoubleResults(load_results, "Yavg", 0))
    lod_Df = lod_Df.assign(Yavg=y_avg)

    z_avg = np.asarray(vsp.GetDoubleResults(load_results, "Zavg", 0))
    lod_Df = lod_Df.assign(Zavg=z_avg)

    cl = np.asarray(vsp.GetDoubleResults(load_results, "cl", 0))
    lod_Df = lod_Df.assign(cl=cl)

    cd = np.asarray(vsp.GetDoubleResults(load_results, "cd", 0))
    lod_Df = lod_Df.assign(cd=cd)

    vovref = np.asarray(vsp.GetDoubleResults(load_results, "V/Vref", 0))
    lod_Df = lod_Df.assign(VoVref=vovref)

    clc_cref = np.asarray(vsp.GetDoubleResults(load_results, "cl*c/cref", 0))
    lod_Df = lod_Df.assign(Clc_cref=clc_cref)

    cdc_cref = np.asarray(vsp.GetDoubleResults(load_results, "cd*c/cref", 0))
    lod_Df = lod_Df.assign(Cdc_cref=cdc_cref)

    # ===================
    #    Main Wing
    # ===================
    # Make right wing data as a new dataframe
    right_wing = lod_Df[lod_Df['WingID'] == 1]
    # Make left wing data as a new dataframe
    left_wing = lod_Df[lod_Df['WingID'] == 2]
    # Flip the left wing for plotting
    left_wing = left_wing.iloc[::-1]
    whole_wing = pd.concat([left_wing, right_wing])

    # ===================
    #   Horizontal Tail
    # ===================
    # Make right wing data as a new dataframe
    right_ht = lod_Df[lod_Df['WingID'] == 4]

    # Make left wing data as a new dataframe
    left_ht = lod_Df[lod_Df['WingID'] == 5]
    # Flip the left wing for plotting
    left_ht = left_ht.iloc[::-1]

    whole_ht = pd.concat([left_ht, right_ht])

    # Plotting of list distribution along wing span
    if cl_plot_flag == 1:
        # Start plotting
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        ax1.plot(whole_wing['Yavg'], whole_wing['cl'], linestyle="-", marker="o")
        ax2.plot(whole_ht['Yavg'], whole_ht['cl'], linestyle="-", marker="o")
        add_prop_position_line(ax=ax1)

        ax1.grid(True)
        ax2.grid(True)

        ax1.tick_params(axis="x", direction="in")
        ax1.tick_params(axis="y", direction="in")
        ax1.set_xlabel('Y [m]')
        ax1.set_ylabel('cl')
        ax1.set_title('Main Wing')

        ax2.tick_params(axis="x", direction="in")
        ax2.tick_params(axis="y", direction="in")
        ax2.set_xlabel('Y [m]')
        ax2.set_ylabel('cl')
        ax2.set_title('Horizontal Tail')

        plt.suptitle('Lift distribution across wing span')
        fig.savefig(save_directory + '/cl.png', format='png', dpi=800)

    # Plotting of drag distribution along wing span
    if cd_plot_flag == 1:
        # Start plotting
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        ax1.plot(whole_wing['Yavg'], whole_wing['cd'], linestyle="-", marker="o")
        ax2.plot(whole_ht['Yavg'], whole_ht['cd'], linestyle="-", marker="o")
        add_prop_position_line(ax=ax1)

        ax1.grid(True)
        ax2.grid(True)

        ax1.tick_params(axis="x", direction="in")
        ax1.tick_params(axis="y", direction="in")
        ax1.set_xlabel('Y [m]')
        ax1.set_ylabel('cd')
        ax1.set_title('Main Wing')

        ax2.tick_params(axis="x", direction="in")
        ax2.tick_params(axis="y", direction="in")
        ax2.set_xlabel('Y [m]')
        ax2.set_ylabel('cd')
        ax2.set_title('Horizontal Tail')

        plt.suptitle('Drag distribution across wing span')
        fig.savefig(save_directory + '/cd.png', format='png', dpi=800)

    # Plotting of V/Vref along wing span
    if VoVref_plot_flag == 1:
        # Start plotting
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        ax1.plot(whole_wing['Yavg'], whole_wing['VoVref'], linestyle="-", marker="o")
        ax2.plot(whole_ht['Yavg'], whole_ht['VoVref'], linestyle="-", marker="o")
        add_prop_position_line(ax=ax1)

        ax1.grid(True)
        ax2.grid(True)

        ax1.tick_params(axis="x", direction="in")
        ax1.tick_params(axis="y", direction="in")
        ax1.set_xlabel('Y [m]')
        ax1.set_ylabel('V/Vref')
        ax1.set_title('Main Wing')

        ax2.tick_params(axis="x", direction="in")
        ax2.tick_params(axis="y", direction="in")
        ax2.set_xlabel('Y [m]')
        ax2.set_ylabel('V/Vref')
        ax2.set_title('Horizontal Tail')

        plt.suptitle('Local Velocity Ratio across wing span')
        fig.savefig(save_directory + '/V_Vref.png', format='png', dpi=800)

    # Plotting of Cl*c/Cref along wing span
    if Clc_cref_plot_flag == 1:
        # Start plotting
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        ax1.plot(whole_wing['Yavg'], whole_wing['Clc_cref'], linestyle="-", marker="o")
        ax2.plot(whole_ht['Yavg'], whole_ht['Clc_cref'], linestyle="-", marker="o")
        add_prop_position_line(ax=ax1)

        ax1.grid(True)
        ax2.grid(True)

        ax1.tick_params(axis="x", direction="in")
        ax1.tick_params(axis="y", direction="in")
        ax1.set_xlabel('Y [m]')
        ax1.set_ylabel('Cl*c/Cref')
        ax1.set_title('Main Wing')

        ax2.tick_params(axis="x", direction="in")
        ax2.tick_params(axis="y", direction="in")
        ax2.set_xlabel('Y [m]')
        ax2.set_ylabel('Cl*c/Cref')
        ax2.set_title('Horizontal Tail')

        plt.suptitle('Section Lift scaled load across wing span')
        fig.savefig(save_directory + '/Clc_Cref.png', format='png', dpi=800)

    # Plotting of Cd*c/Cref along wing span
    if Cdc_cref_plot_flag == 1:
        # Start plotting
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        ax1.plot(whole_wing['Yavg'], whole_wing['Cdc_cref'], linestyle="-", marker="o")
        ax2.plot(whole_ht['Yavg'], whole_ht['Cdc_cref'], linestyle="-", marker="o")
        add_prop_position_line(ax=ax1)

        ax1.grid(True)
        ax2.grid(True)

        ax1.tick_params(axis="x", direction="in")
        ax1.tick_params(axis="y", direction="in")
        ax1.set_xlabel('Y [m]')
        ax1.set_ylabel('Cd*c/Cref')
        ax1.set_title('Main Wing')

        ax2.tick_params(axis="x", direction="in")
        ax2.tick_params(axis="y", direction="in")
        ax2.set_xlabel('Y [m]')
        ax2.set_ylabel('Cd*c/Cref')
        ax2.set_title('Horizontal Tail')

        plt.suptitle('Section Drag scaled load across wing span')
        fig.savefig(save_directory + '/Cdc_cref.png', format='png', dpi=800)

    plt.show()
    print("Finished plotting lod File")

    return lod_Df


def history_results():
    history_res = vsp.FindLatestResultsID("VSPAERO_History")

    cl = np.asarray(vsp.GetDoubleResults(history_res, "CL", 0))
    his_df = pd.DataFrame({'CL': cl})

    cd0 = np.asarray(vsp.GetDoubleResults(history_res, "CDo", 0))
    his_df = his_df.assign(CDo=cd0)

    cdi = np.asarray(vsp.GetDoubleResults(history_res, "CDi", 0))
    his_df = his_df.assign(CDi=cdi)

    cdtot = np.asarray(vsp.GetDoubleResults(history_res, "CDtot", 0))
    his_df = his_df.assign(CDtot=cdtot)

    ld = np.asarray(vsp.GetDoubleResults(history_res, "L/D", 0))
    his_df = his_df.assign(L_D=ld)

    return his_df

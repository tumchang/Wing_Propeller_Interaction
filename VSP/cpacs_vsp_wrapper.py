"""
============================================================================
This script is class definition of CPACS and VSP model
-------------
Author: Chang Xu   TUM   03739064  July.2023
Supervisor: Yiyuan Ma & Alexandros Lessis

Copyright @ Bauhaus Luftfahrt e.V
============================================================================
"""

# Module import
# import numpy as np
import xmltodict as xml
# import openvsp as vsp
# import matplotlib.pyplot as plt
# import os
from scipy.interpolate import interp1d
# from scipy.interpolate import CubicSpline
# from scipy.interpolate import Rbf
# from scipy.interpolate import make_interp_spline
from tigl3.tigl3wrapper import *
from tixi3.tixi3wrapper import *
from tixi3.tixi3wrapper import Tixi3Exception
from Functions import *

MODEL = "/cpacs/vehicles/aircraft/model"
REFS = MODEL + "/reference"
separator = "==========================================================================================="
# Sets default precision of real numbers for numpy output
np.set_printoptions(precision=3, threshold=20)
precision_decimal = 4


class CPACS:
    """
    get basic data from CPACS and hold the data
    """

    def __init__(self, cpacs_file):

        with open(cpacs_file, "r") as fp:
            self.cpacs_dict = xml.parse(fp.read())

        self.model = self.cpacs_dict['cpacs']['vehicles']['aircraft']['model']
        self.profile = self.cpacs_dict['cpacs']['vehicles']['profiles']
        self.tixi = Tixi3()
        print("reading cpacs with tixi...")
        self.tixi.open(cpacs_file)
        print("cpacs data are read in with tixi\n" + separator)

        self.tigl = Tigl3()
        print("tigl processing ...")
        self.tigl.open(self.tixi, uid="")
        print("tigl processing finished\n" + separator)

        self.name = self.tixi.getTextAttribute(MODEL, "uID")

        try:
            self.ref_s = self.tixi.getDoubleElement(REFS + "/area")
            self.ref_c = self.tixi.getDoubleElement(REFS + "/length")

            wing_uid = self.tigl.wingGetUID(1)
            self.ref_b = self.tigl.wingGetSpan(wing_uid)

            pnt_x = self.tixi.getDoubleElement(REFS + "/point/x")
            pnt_y = self.tixi.getDoubleElement(REFS + "/point/y")
            pnt_z = self.tixi.getDoubleElement(REFS + "/point/z")

            self.ref_pnt = np.array([pnt_x, pnt_y, pnt_z])
        except Tixi3Exception:
            pass


class VSPFuseSection:
    """
    This Class holds the data for the VSP inputs for all Fuselage sections
    """

    def __init__(self):
        self.element_name = []
        self.length = None
        self.x_loc = []
        self.x_percent = []
        self.y_loc = []
        self.z_loc = []
        self.z_percent = []
        # TODO: fuse_scale 'x' useless??
        self.fuse_scale = None


class VSPWingSection:
    """
    This Class holds the data for the VSP inputs for all wing sections
    """

    # TODO: Add Twist!!! and root incidence  ✔   SPAN related to sweep angle in CPACS??   ✔
    # TODO: Span in VSP = CPACS.length * cos(Sweep) ??? (validated!)      ✔
    def __init__(self):
        self.length = []
        self.sweep = []
        self.dihedral = []
        self.chord = []
        self.airfoil = []
        self.span = []
        self.sec_x = []
        self.sec_y = []
        self.sec_z = []
        self.incidence = []
        self.airfoil_scale = None


wing_directory = "cpacs/vehicles/aircraft/model/wings"
fuselage_directory = "cpacs/vehicles/aircraft/model/fuselages/fuselage"


class VSP:
    """
    Extract the basic data from CPACS model
    Using different methods for generating VSP model
    """

    def __init__(self, CPACS_Model):
        self.name = CPACS_Model.name
        self.fuselage = CPACS_Model.model['fuselages']['fuselage']
        self.fuselage_profile = CPACS_Model.profile['fuselageProfiles']['fuselageProfile']
        self.wings = CPACS_Model.model['wings']['wing']
        self.wings_profile = CPACS_Model.profile['wingAirfoils']['wingAirfoil']
        self.prop = CPACS_Model.cpacs_dict['cpacs']['vehicles']['engines']['engine']

        # Using class to store all the data for VSP model generation
        self.vsp_wing_section = None
        self.vsp_vt_section = VSPWingSection()
        self.vsp_ht_section = VSPWingSection()
        self.vsp_fuse_section = None

        # TIGL and TIXI
        self.tigl = CPACS_Model.tigl
        self.tixi = CPACS_Model.tixi

    def generate_vsp_model(self, test_flag, unsteady_flag=0, rpm=0):
        self.generate_fuselage(fuselage_index=0)
        self.generate_fuselage(fuselage_index=1)

        sub_element_name = "wing"
        n_wings = self.tixi.getNamedChildrenCount(wing_directory, sub_element_name)
        if n_wings == 2:
            self.generate_wing()
            self.generate_ht()
        else:
            pass
            self.generate_wing(wing_index=0, read_mode=1)
            self.generate_wing(wing_index=1, read_mode=1)
            self.generate_wing(wing_index=2, read_mode=1)
            # self.generate_ht()
            # self.generate_vt()
        if test_flag == 1:
            pass
        else:
            self.generate_prop(unsteady=unsteady_flag, rpm=rpm)

    # Read mode 0 == Read data from positionings. Read mode 1 == read data from sections
    def generate_wing(self, wing_index=0, read_mode=0):
        print("--> Creating Main Wing")
        self.vsp_wing_section = VSPWingSection()
        wing = self.wings[wing_index]

        # Add Wing
        wing_id = vsp.AddGeom('WING')
        vsp.SetGeomName(wing_id, wing['name'])

        # Add to Set_0
        vsp.SetSetFlag(wing_id, 3, True)

        # Generate all airfoil in CPACS Model and save as .dat file for future usage
        self.generate_dat_file(wing['name'])
        self.generate_af_file(wing['name'])

        if wing_index == 2:
            # Disable Symmetry
            vsp.SetParmVal(vsp.FindParm(wing_id, "Sym_Planar_Flag", "Sym"), 0.0)
        else:
            pass

        # Move the Position of the Wing
        vsp.SetParmVal(wing_id, 'X_Rel_Location', 'XForm',
                       float(wing['transformation']['translation']['x']))
        vsp.SetParmVal(wing_id, 'Z_Rel_Location', 'XForm',
                       float(wing['transformation']['translation']['z']))
        vsp.SetParmVal(wing_id, 'X_Rel_Rotation', 'XForm',
                       float(wing['transformation']['rotation']['x']))
        vsp.SetParmVal(wing_id, 'Y_Rel_Rotation', 'XForm',
                       float(wing['transformation']['rotation']['y']))
        vsp.SetParmVal(wing_id, 'Z_Rel_Rotation', 'XForm',
                       float(wing['transformation']['rotation']['z']))

        # TODO: Add code to identify the airfoil shape!!!!!!!   ✔
        # Get the number of sections from cpacs model
        section_num = len(wing['sections']['section'])

        section_scale = []
        if read_mode == 0:
            # Get each section's parameters from CPACS model
            for i in range(section_num):
                # section length from CPACS
                self.vsp_wing_section.length.append(float(wing['positionings']['positioning'][i]['length']))

                # section sweep angle
                self.vsp_wing_section.sweep.append(float(wing['positionings']['positioning'][i]['sweepAngle']))

                # section span (corrected)
                span = float(wing['positionings']['positioning'][i]['length']) * np.cos(
                    (float(wing['positionings']['positioning'][i]['sweepAngle'])) * np.pi / 180)
                self.vsp_wing_section.sweep.append(span)

                # section dihedral angle
                self.vsp_wing_section.dihedral.append(
                    float(wing['positionings']['positioning'][i]['dihedralAngle']))

                # section chord length
                self.vsp_wing_section.chord.append(
                    float(wing['sections']['section'][i]['elements']['element']['transformation']['scaling']['x']))

                # section airfoil name
                self.vsp_wing_section.airfoil.append(
                    wing['sections']['section'][i]['elements']['element']['airfoilUID'])

                # section incidence angle
                self.vsp_wing_section.incidence.append(
                    float(wing['sections']['section'][i]['transformation']['rotation']['y']))

                # section airfoil scaling(includes xyz value and saved as matrix)
                scaling = wing['sections']['section'][i]['elements']['element']['transformation'][
                    'scaling']
                x = float(scaling.get('x', 1))
                y = float(scaling.get('y', 1))
                z = float(scaling.get('z', 1))
                section_scale.append([x, y, z])
                scaling_matrix = np.array(section_scale)
                self.vsp_wing_section.airfoil_scale = scaling_matrix
        else:
            # Get each section's parameters from CPACS model
            for i in range(section_num):
                # section chord length
                self.vsp_wing_section.chord.append(
                    float(
                        wing['sections']['section'][i]['transformation']['scaling']['x']))

                # section airfoil name
                self.vsp_wing_section.airfoil.append(
                    wing['sections']['section'][i]['elements']['element']['airfoilUID'])

                # section incidence angle
                self.vsp_wing_section.incidence.append(
                    float(wing['sections']['section'][i]['transformation']['rotation']['y']))

                # section airfoil scaling(includes xyz value and saved as matrix)
                scaling = wing['sections']['section'][i]['transformation']['scaling']
                x = float(scaling.get('x', 1))
                y = float(scaling.get('y', 1))
                z = float(scaling.get('z', 1))
                section_scale.append([x, y, z])
                scaling_matrix = np.array(section_scale)
                self.vsp_wing_section.airfoil_scale = scaling_matrix

                # section x,z position
                section_x = float(wing['sections']['section'][i]['transformation']['translation']['x'])
                section_y = float(wing['sections']['section'][i]['transformation']['translation']['y'])
                section_z = float(wing['sections']['section'][i]['transformation']['translation']['z'])
                self.vsp_wing_section.sec_x.append(section_x)
                self.vsp_wing_section.sec_y.append(section_y)
                self.vsp_wing_section.sec_z.append(section_z)

            self.vsp_wing_section.span.append(0)
            self.vsp_wing_section.sweep.append(0)
            self.vsp_wing_section.dihedral.append(0)

            for i in range(1, section_num):
                # Section Span
                self.vsp_wing_section.span.append(
                    self.vsp_wing_section.sec_y[i] - self.vsp_wing_section.sec_y[i - 1]
                )

            for i in range(1, section_num):
                # Section sweep angle
                self.vsp_wing_section.sweep.append(
                    np.arctan((self.vsp_wing_section.sec_x[i] - self.vsp_wing_section.sec_x[i - 1]) /
                              (self.vsp_wing_section.span[i]))
                    * (180 / np.pi)
                )

                # section dihedral angle
                self.vsp_wing_section.dihedral.append(
                    np.arctan((self.vsp_wing_section.sec_z[i] - self.vsp_wing_section.sec_z[i - 1]) /
                              (self.vsp_wing_section.span[i]))
                    * (180 / np.pi)
                )

        # Insert Sections (Depends on how many sections are defined in CPACS file)
        for i in range(1, section_num):
            vsp.InsertXSec(wing_id, 1, vsp.XS_SIX_SERIES)

        # Cut The Original Section
        vsp.CutXSec(wing_id, 1)

        # Setting of Tess_W numbers
        vsp.SetParmVal(wing_id, "Tess_W", "Shape", 45)

        # Set root incidence angle of the wing
        vsp.SetParmVal(wing_id, "Twist", 'XSec_0', self.vsp_wing_section.incidence[0])

        for i in range(1, section_num):
            # TODO: how to control SectTess_U?
            vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_' + str(i), 30)

            vsp.SetParmVal(wing_id, "Span", 'XSec_' + str(i), self.vsp_wing_section.span[i])
            vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_' + str(i), self.vsp_wing_section.chord[i - 1])
            vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_' + str(i), self.vsp_wing_section.chord[i])
            vsp.SetParmVal(wing_id, "Sweep", 'XSec_' + str(i), self.vsp_wing_section.sweep[i])
            vsp.SetParmVal(wing_id, "Dihedral", 'XSec_' + str(i), self.vsp_wing_section.dihedral[i])
            vsp.SetParmVal(wing_id, "Twist", 'XSec_' + str(i), self.vsp_wing_section.incidence[i])

            # Update
            vsp.Update()

        # Change Driver
        vsp.SetDriverGroup(wing_id, 1, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
        if wing_index == 0:
            vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 0.0)
        else:
            vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)

        # Update
        vsp.Update()

        # Change Airfoil in Each Section
        for i in range(section_num):
            xsec_surf = vsp.GetXSecSurf(wing_id, 0)
            vsp.ChangeXSecShape(xsec_surf, i, vsp.XS_FILE_AIRFOIL)
            xsec = vsp.GetXSec(xsec_surf, i)
            vsp.ReadFileAirfoil(xsec, f"./airfoil/{wing['name']}/" + self.vsp_wing_section.airfoil[i] + ".af")

        # Update
        vsp.Update()

        # Change relative airfoil thickness (scale 'z'/ scale 'x')
        for i in range(section_num):
            t_c = vsp.GetParmVal(wing_id, 'ThickChord', 'XSecCurve_' + str(i))
            t_c_scale = (self.vsp_wing_section.airfoil_scale[i, 2]) / (self.vsp_wing_section.airfoil_scale[i, 0])
            vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_' + str(i), t_c * t_c_scale)

        print("--> Main Wing Created")

    # TODO: Maybe this can combined with generate_wing method to make code more compact
    def generate_ht(self):
        print("--> Creating Horizontal Tail")
        # Add Wing
        wing_id = vsp.AddGeom('WING')
        vsp.SetGeomName(wing_id, self.wings[1]['name'])

        # Move the Position of the Wing
        vsp.SetParmVal(wing_id, 'X_Rel_Location', 'XForm',
                       float(self.wings[1]['transformation']['translation']['x']))
        vsp.SetParmVal(wing_id, 'Z_Rel_Location', 'XForm',
                       float(self.wings[1]['transformation']['translation']['z']))
        vsp.SetParmVal(wing_id, 'X_Rel_Rotation', 'XForm',
                       float(self.wings[1]['transformation']['rotation']['x']))
        vsp.SetParmVal(wing_id, 'Y_Rel_Rotation', 'XForm',
                       float(self.wings[1]['transformation']['rotation']['y']))
        vsp.SetParmVal(wing_id, 'Z_Rel_Rotation', 'XForm',
                       float(self.wings[1]['transformation']['rotation']['z']))

        # Get the number of sections from cpacs model
        section_num = len(self.wings[1]['sections']['section'])

        section_scale = []

        # Get each section's parameters from CPACS model
        for i in range(section_num):
            # section span
            self.vsp_ht_section.length.append(float(self.wings[1]['positionings']['positioning'][i]['length']))

            # section sweep angle
            self.vsp_ht_section.sweep.append(float(self.wings[1]['positionings']['positioning'][i]['sweepAngle']))

            # section span (corrected)
            self.vsp_ht_section.span.append(float(self.wings[1]['positionings']['positioning'][i]['length'])
                                            * np.cos(
                (float(self.wings[1]['positionings']['positioning'][i]['sweepAngle'])) * np.pi / 180))

            # section dihedral angle
            self.vsp_ht_section.dihedral.append(
                float(self.wings[1]['positionings']['positioning'][i]['dihedralAngle']))

            # section chord length
            self.vsp_ht_section.chord.append(
                float(self.wings[1]['sections']['section'][i]['elements']['element']['transformation']['scaling']['x']))

            # section airfoil name
            self.vsp_ht_section.airfoil.append(
                self.wings[1]['sections']['section'][i]['elements']['element']['airfoilUID'])

            # section incidence angle
            self.vsp_ht_section.incidence.append(
                float(self.wings[1]['sections']['section'][i]['transformation']['rotation']['y']))

            # section airfoil scaling(includes xyz value and saved as matrix)
            scaling = self.wings[1]['sections']['section'][i]['elements']['element']['transformation'][
                'scaling']
            x = float(scaling.get('x', 1))
            y = float(scaling.get('y', 1))
            z = float(scaling.get('z', 1))
            section_scale.append([x, y, z])
            scaling_matrix = np.array(section_scale)
            self.vsp_ht_section.airfoil_scale = scaling_matrix

        # Insert Sections (Depends on how many sections are defined in CPACS file)
        for i in range(1, section_num):
            vsp.InsertXSec(wing_id, 1, vsp.XS_SIX_SERIES)

        # Cut The Original Section
        vsp.CutXSec(wing_id, 1)

        # Setting of Tess_W numbers
        vsp.SetParmVal(wing_id, "Tess_W", "Shape", 45)

        # Set root incidence angle of the wing
        vsp.SetParmVal(wing_id, "Twist", 'XSec_0', self.vsp_ht_section.incidence[0])

        for i in range(1, section_num):
            # TODO: how to control SectTess_U?
            vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_' + str(i), 8)

            vsp.SetParmVal(wing_id, "Span", 'XSec_' + str(i), self.vsp_ht_section.span[i])
            vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_' + str(i), self.vsp_ht_section.chord[i - 1])
            vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_' + str(i), self.vsp_ht_section.chord[i])
            vsp.SetParmVal(wing_id, "Sweep", 'XSec_' + str(i), self.vsp_ht_section.sweep[i])
            vsp.SetParmVal(wing_id, "Dihedral", 'XSec_' + str(i), self.vsp_ht_section.dihedral[i])
            vsp.SetParmVal(wing_id, "Twist", 'XSec_' + str(i), self.vsp_ht_section.incidence[i])

            # Update
            vsp.Update()

        # Change Driver
        vsp.SetDriverGroup(wing_id, 1, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
        vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)

        # Update
        vsp.Update()

        # Change Airfoil in Each Section
        for i in range(section_num):
            xsec_surf = vsp.GetXSecSurf(wing_id, 0)
            vsp.ChangeXSecShape(xsec_surf, i, vsp.XS_FILE_AIRFOIL)
            xsec = vsp.GetXSec(xsec_surf, i)
            vsp.ReadFileAirfoil(xsec, f"./airfoil/{self.wings[0]['name']}/" + self.vsp_ht_section.airfoil[i] + ".af")

        # Update
        vsp.Update()

        # Change relative airfoil thickness (scale 'z'/ scale 'x')
        for i in range(section_num):
            t_c = vsp.GetParmVal(wing_id, 'ThickChord', 'XSecCurve_' + str(i))
            t_c_scale = (self.vsp_ht_section.airfoil_scale[i, 2]) / (self.vsp_ht_section.airfoil_scale[i, 0])
            vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_' + str(i), t_c * t_c_scale)

        print("--> Horizontal Tail Created")

    def generate_vt(self):
        print("--> Creating Vertical Tail")
        # Add Wing
        wing_id = vsp.AddGeom('WING')
        vsp.SetGeomName(wing_id, self.wings[2]['name'])

        # Disable Symmetry
        vsp.SetParmVal(vsp.FindParm(wing_id, "Sym_Planar_Flag", "Sym"), 0.0)

        # Move the Position of the Wing
        vsp.SetParmVal(wing_id, 'X_Rel_Location', 'XForm',
                       float(self.wings[2]['transformation']['translation']['x']))
        vsp.SetParmVal(wing_id, 'Z_Rel_Location', 'XForm',
                       float(self.wings[2]['transformation']['translation']['z']))
        vsp.SetParmVal(wing_id, 'X_Rel_Rotation', 'XForm',
                       float(self.wings[2]['transformation']['rotation']['x']))
        vsp.SetParmVal(wing_id, 'Y_Rel_Rotation', 'XForm',
                       float(self.wings[2]['transformation']['rotation']['y']))
        vsp.SetParmVal(wing_id, 'Z_Rel_Rotation', 'XForm',
                       float(self.wings[2]['transformation']['rotation']['z']))

        # Get the number of sections from cpacs model
        section_num = len(self.wings[2]['sections']['section'])

        section_scale = []

        # Get each section's parameters from CPACS model
        for i in range(section_num):
            # section span
            self.vsp_vt_section.length.append(float(self.wings[2]['positionings']['positioning'][i]['length']))

            # section sweep angle
            self.vsp_vt_section.sweep.append(float(self.wings[2]['positionings']['positioning'][i]['sweepAngle']))

            # section span (corrected)
            self.vsp_vt_section.span.append(float(self.wings[2]['positionings']['positioning'][i]['length'])
                                            * np.cos(
                (float(self.wings[2]['positionings']['positioning'][i]['sweepAngle'])) * np.pi / 180))

            # section dihedral angle
            self.vsp_vt_section.dihedral.append(
                float(self.wings[2]['positionings']['positioning'][i]['dihedralAngle']))

            # section chord length
            self.vsp_vt_section.chord.append(
                float(self.wings[2]['sections']['section'][i]['elements']['element']['transformation']['scaling']['x']))

            # section airfoil name
            self.vsp_vt_section.airfoil.append(
                self.wings[2]['sections']['section'][i]['elements']['element']['airfoilUID'])

            # section airfoil scaling(includes xyz value and saved as matrix)
            scaling = self.wings[2]['sections']['section'][i]['elements']['element']['transformation'][
                'scaling']
            x = float(scaling.get('x', 1))
            y = float(scaling.get('y', 1))
            z = float(scaling.get('z', 1))
            section_scale.append([x, y, z])
            scaling_matrix = np.array(section_scale)
            self.vsp_vt_section.airfoil_scale = scaling_matrix

        # Insert Sections (Depends on how many sections are defined in CPACS file)
        for i in range(1, section_num):
            vsp.InsertXSec(wing_id, 1, vsp.XS_SIX_SERIES)

        # Cut The Original Section
        vsp.CutXSec(wing_id, 1)

        # Setting of Tess_W numbers
        vsp.SetParmVal(wing_id, "Tess_W", "Shape", 45)

        for i in range(1, section_num):
            # TODO: how to control SectTess_U?
            vsp.SetParmVal(wing_id, "SectTess_U", 'XSec_' + str(i), 8)

            vsp.SetParmVal(wing_id, "Span", 'XSec_' + str(i), self.vsp_vt_section.span[i])
            vsp.SetParmVal(wing_id, "Root_Chord", 'XSec_' + str(i), self.vsp_vt_section.chord[i - 1])
            vsp.SetParmVal(wing_id, "Tip_Chord", 'XSec_' + str(i), self.vsp_vt_section.chord[i])
            vsp.SetParmVal(wing_id, "Sweep", 'XSec_' + str(i), self.vsp_vt_section.sweep[i])
            vsp.SetParmVal(wing_id, "Dihedral", 'XSec_' + str(i), self.vsp_vt_section.dihedral[i])

            # Update
            vsp.Update()

        # Change Driver
        vsp.SetDriverGroup(wing_id, 1, vsp.SPAN_WSECT_DRIVER, vsp.ROOTC_WSECT_DRIVER, vsp.TIPC_WSECT_DRIVER)
        vsp.SetParmVal(wing_id, "RotateAirfoilMatchDideralFlag", "WingGeom", 1.0)

        # Update
        vsp.Update()

        # Change Airfoil in Each Section
        for i in range(section_num):
            xsec_surf = vsp.GetXSecSurf(wing_id, 0)
            vsp.ChangeXSecShape(xsec_surf, i, vsp.XS_FILE_AIRFOIL)
            xsec = vsp.GetXSec(xsec_surf, i)
            vsp.ReadFileAirfoil(xsec, f"./airfoil/{self.wings[0]['name']}/" + self.vsp_vt_section.airfoil[i] + ".af")

        # Update
        vsp.Update()

        # Change relative airfoil thickness (scale 'z'/ scale 'x')
        for i in range(section_num):
            t_c = vsp.GetParmVal(wing_id, 'ThickChord', 'XSecCurve_' + str(i))
            t_c_scale = (self.vsp_vt_section.airfoil_scale[i, 2]) / (self.vsp_vt_section.airfoil_scale[i, 0])
            vsp.SetParmVal(wing_id, 'ThickChord', 'XSecCurve_' + str(i), t_c * t_c_scale)

        print("--> Vertical Tail Created")

    def generate_fuselage(self, fuselage_index=0):
        # TODO: Length Definition in CPACS??
        print(f"--> Creating Fuselage {fuselage_index}")

        self.vsp_fuse_section = VSPFuseSection()

        fuselage = self.fuselage[fuselage_index]

        # Add Wing
        fuse_id = vsp.AddGeom('FUSELAGE')
        vsp.SetGeomName(fuse_id, fuselage['name'])

        # Add to Set_0
        vsp.SetSetFlag(fuse_id, 3, True)

        # Generate all Fuselage sections in CPACS Model and save as .fxs file for future usage
        self.generate_fxs_file(fuselage['name'])

        # Cut the existing XSec, make plate for new XSec to be added
        vsp.CutXSec(fuse_id, 1)
        vsp.CutXSec(fuse_id, 1)
        vsp.CutXSec(fuse_id, 1)

        vsp.SetParmVal(fuse_id, 'TopLAngle', 'XSec_0', 0)
        vsp.SetParmVal(fuse_id, 'RightLAngle', 'XSec_0', 0)
        vsp.SetParmVal(fuse_id, 'TopLStrength', 'XSec_0', 1.0)
        vsp.SetParmVal(fuse_id, 'RightLStrength', 'XSec_0', 1.0)

        vsp.SetParmVal(fuse_id, 'Tess_W', 'Shape', 36)

        vsp.Update()

        if fuselage_index == 1:
            vsp.SetParmVal(vsp.FindParm(fuse_id, "Sym_Planar_Flag", "Sym"), 2.0)

        # Move the Position of the Wing
        vsp.SetParmVal(fuse_id, 'X_Rel_Location', 'XForm',
                       float(fuselage['transformation']['translation']['x']))
        vsp.SetParmVal(fuse_id, 'Y_Rel_Location', 'XForm',
                       float(fuselage['transformation']['translation']['y']))
        vsp.SetParmVal(fuse_id, 'Z_Rel_Location', 'XForm',
                       float(fuselage['transformation']['translation']['z']))
        vsp.SetParmVal(fuse_id, 'X_Rel_Rotation', 'XForm',
                       float(fuselage['transformation']['rotation']['x']))
        vsp.SetParmVal(fuse_id, 'Y_Rel_Rotation', 'XForm',
                       float(fuselage['transformation']['rotation']['y']))
        vsp.SetParmVal(fuse_id, 'Z_Rel_Rotation', 'XForm',
                       float(fuselage['transformation']['rotation']['z']))

        # Get the number of fuselage sections from cpacs model
        section_count = len(fuselage['sections']['section'])

        section_scale = []
        section_translation = []

        for i in range(section_count):
            try:
                translation = fuselage['positionings']['positioning'][i]['length']
                section_translation.append(float(translation))
                translation_matrix = np.array(section_translation)
                self.vsp_fuse_section.length = translation_matrix

            except KeyError:
                print("Positioning in CPACS doesn't exist, try element translation to find XSec Position")
                translation = fuselage['sections']['section'][i]['elements']['element']['transformation'][
                    'translation']
                x = float(translation.get('x', 1))
                y = float(translation.get('y', 1))
                z = float(translation.get('z', 1))
                section_translation.append([x, y, z])
                translation_matrix = np.array(section_translation)
                self.vsp_fuse_section.length = translation_matrix

        for i in range(section_count):
            self.vsp_fuse_section.element_name.append(
                fuselage['sections']['section'][i]['elements']['element']['profileUID'])

            self.vsp_fuse_section.y_loc.append(
                float(fuselage['sections']['section'][i]['transformation']['translation']['y']))

            # If the translation information in stored under elements section
            self.vsp_fuse_section.z_loc.append(
                float(fuselage['sections']['section'][i]['transformation']['translation']['z']))

            # section fuselage scaling(includes xyz value and saved as matrix)
            if fuselage_index == 0:
                scaling_1 = fuselage['transformation']['scaling']
                scaling_2 = fuselage['sections']['section'][i]['elements']['element']['transformation']['scaling']
            else:
                scaling_1 = fuselage['transformation']['scaling']
                scaling_2 = fuselage['sections']['section'][i]['transformation']['scaling']
            x = float(scaling_1.get('x', 1)) * float(scaling_2.get('x', 1))
            y = float(scaling_1.get('y', 1)) * float(scaling_2.get('y', 1))
            z = float(scaling_1.get('z', 1)) * float(scaling_2.get('z', 1))
            section_scale.append([x, y, z])

        self.vsp_fuse_section.fuse_scale = section_scale

        if all(value == 0 for value in self.vsp_fuse_section.z_loc):
            self.vsp_fuse_section.z_loc = []
            for i in range(section_count):
                self.vsp_fuse_section.z_loc.append(
                    float(fuselage['sections']['section'][i]['elements']['element']['transformation']['translation'][
                              'z']))

        scaling_matrix = np.array(section_scale)
        self.vsp_fuse_section.fuse_scale = scaling_matrix

        fuselage_uid = self.tigl.fuselageGetUID(fuselage_index + 1)
        total_length = self.tigl.fuselageGetCenterLineLength(fuselage_uid)

        vsp.SetParmVal(fuse_id, 'Length', 'Design', total_length)
        for i in range(section_count):
            self.vsp_fuse_section.x_percent.append(np.sum(self.vsp_fuse_section.length[:i + 1]))

        # Get the total length of the fuselage
        if fuselage_index == 0:
            self.vsp_fuse_section.x_percent = []
            if np.ndim(self.vsp_fuse_section.length) == 1:
                # total_length = np.sum(self.vsp_fuse_section.length)
                vsp.SetParmVal(fuse_id, 'Length', 'Design', total_length)
                # Calculate the X position of each section in AbsCoordinate,
                # thus getting XLocPercent for VSP model generation
                for i in range(section_count):
                    self.vsp_fuse_section.x_loc.append(sum(self.vsp_fuse_section.length[0:i + 1]))
                    self.vsp_fuse_section.x_percent.append((self.vsp_fuse_section.x_loc[i]) / total_length)
                    self.vsp_fuse_section.z_percent.append(self.vsp_fuse_section.z_loc[i] / total_length)

            elif np.ndim(self.vsp_fuse_section.length) == 2:
                total_length = self.vsp_fuse_section.length[-1, 0]
                vsp.SetParmVal(fuse_id, 'Length', 'Design', total_length)
                for i in range(section_count):
                    self.vsp_fuse_section.x_percent.append((self.vsp_fuse_section.length[i, 0]) / total_length)
                    self.vsp_fuse_section.z_percent.append((self.vsp_fuse_section.length[i, 2]) / total_length)
        else:
            for i in range(section_count):
                self.vsp_fuse_section.z_percent.append(0)

        for i in range(section_count - 2):
            vsp.InsertXSec(fuse_id, i, 6)

        vsp.Update()

        for i in range(section_count):
            vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_' + str(i), 2)
            vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_' + str(i), self.vsp_fuse_section.x_percent[i])
            vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_' + str(i), self.vsp_fuse_section.z_percent[i])
            vsp.SetParmVal(fuse_id, 'XRotate', 'XSec_' + str(i), 90)

            vsp.Update()

        for i in range(section_count):
            xsec_surf = vsp.GetXSecSurf(fuse_id, 0)
            vsp.ChangeXSecShape(xsec_surf, i, vsp.XS_FILE_FUSE)
            xsec = vsp.GetXSec(xsec_surf, i)
            try:
                vsp.ReadFileXSec(xsec, f"./fuselage/{fuselage['name']}/" + self.vsp_fuse_section.element_name[i][
                    '#text'] + ".fxs")
            except TypeError:
                vsp.ReadFileXSec(xsec,
                                 f"./fuselage/{fuselage['name']}/" + self.vsp_fuse_section.element_name[i] + ".fxs")

            vsp.Update()

            # Get the diameter and Height of the section
            section_width = vsp.GetParmVal(fuse_id, 'Width', 'XSecCurve_' + str(i))
            section_height = vsp.GetParmVal(fuse_id, 'Height', 'XSecCurve_' + str(i))
            vsp.SetParmVal(fuse_id, 'Width', 'XSecCurve_' + str(i),
                           section_width * self.vsp_fuse_section.fuse_scale[i, 2])
            vsp.SetParmVal(fuse_id, 'Height', 'XSecCurve_' + str(i),
                           section_height * self.vsp_fuse_section.fuse_scale[i, 1])

            print("Fuselage Section " + str(i + 1) + " created" + " / " + str(section_count) + " in total")

            # Close the cap
            vsp.SetParmVal(fuse_id, 'CapUMinOption', 'EndCap', vsp.FLAT_END_CAP)
            vsp.SetParmVal(fuse_id, 'CapUMaxOption', 'EndCap', vsp.FLAT_END_CAP)

        print("Fuselage created")

    def generate_prop(self, unsteady=0, rpm=0, ct=0.13864, cp=0.43760, rev_flag=0):
        print("--> Generating Propeller")
        # Add Prop Geometry and return its ID
        prop_id = vsp.AddGeom("PROP")

        # Add to Set_1
        vsp.SetSetFlag(prop_id, 4, True)

        # Get the diameter of the Prop and change it
        diameter_id = vsp.GetParm(prop_id, "Diameter", "Design")
        prop_length = float(self.prop['geometry']['length'])
        vsp.SetParmVal(diameter_id, prop_length)

        # Get the number of blades and change it to 5 blades
        nblade_id = vsp.GetParm(prop_id, "NumBlade", "Design")
        vsp.SetParmVal(nblade_id, 6)

        # generating a pair of props
        vsp.SetParmVal(vsp.FindParm(prop_id, "Sym_Planar_Flag", "Sym"), 2.0)

        # Change PropMode to Disk to enable Actuator disk solver
        if unsteady == 1:
            vsp.SetParmVal(prop_id, 'PropMode', 'Design', 0)  # Blade
        else:
            vsp.SetParmVal(prop_id, 'PropMode', 'Design', 2)  # Actuator Disk

        vsp.Update()

        # Reverse setting
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
        for i in range(1, 6):
            vsp.InsertXSec(prop_id, i, vsp.XS_FILE_AIRFOIL)
            print(f"Propeller XSec {i} created")
        vsp.CutXSec(prop_id, 7)

        # Change cross-section surface
        xsec_surf_0 = vsp.GetXSecSurf(prop_id, 0)
        vsp.ChangeXSecShape(xsec_surf_id=xsec_surf_0, xsec_index=0, type=vsp.XS_CIRCLE)

        xsec_surf_1 = vsp.GetXSecSurf(prop_id, 1)
        vsp.ChangeXSecShape(xsec_surf_id=xsec_surf_1, xsec_index=1, type=vsp.XS_FILE_AIRFOIL)

        prop_position = self.prop['geometry']['engineMounts']['engineMount']['position']

        x_rel_loc = float(prop_position.get('x', 1))
        y_rel_loc = float(prop_position.get('y', 1))
        z_rel_loc = float(prop_position.get('z', 1))

        # XYZ relative position of the propeller
        vsp.SetParmVal(prop_id, 'X_Rel_Location', 'XForm', x_rel_loc)
        vsp.SetParmVal(prop_id, 'Y_Rel_Location', 'XForm', y_rel_loc)
        vsp.SetParmVal(prop_id, 'Z_Rel_Location', 'XForm', z_rel_loc)

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
        r_R = float(self.prop['geometry']['diameter']) / float(self.prop['geometry']['length'])
        scale = r_R/0.2

        xsec_radiusfrac_0 = vsp.GetXSecParm(xsec_id=xsec_0, name="RadiusFrac")
        vsp.SetParmVal(xsec_radiusfrac_0, r_R)

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
        vsp.ReadFileAirfoil(xsec_id=xsec_1, file_name="P:/OpenVSP/airfoil/N0012_VSP.af")
        vsp.ReadFileAirfoil(xsec_id=xsec_2, file_name="P:/OpenVSP/airfoil/N0012_VSP.af")
        vsp.ReadFileAirfoil(xsec_id=xsec_3, file_name="P:/OpenVSP/airfoil/N0012_VSP.af")
        vsp.ReadFileAirfoil(xsec_id=xsec_4, file_name="P:/OpenVSP/airfoil/N0012_VSP.af")
        vsp.ReadFileAirfoil(xsec_id=xsec_5, file_name="P:/OpenVSP/airfoil/N0012_VSP.af")
        vsp.ReadFileAirfoil(xsec_id=xsec_6, file_name="P:/OpenVSP/airfoil/N0012_VSP.af")

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

        if unsteady == 1:
            vsp.SetParmVal(vsp.FindParm(vsp.FindContainer("VSPAEROSettings", 0), "UniformPropRPMFlag", "VSPAERO"), 0)
            blade_id = vsp.FindUnsteadyGroup(1)
            vsp.SetParmVal(vsp.FindParm(blade_id, "RPM", "UnsteadyGroup"), rpm)
            blade_id = vsp.FindUnsteadyGroup(2)
            vsp.SetParmVal(vsp.FindParm(blade_id, "RPM", "UnsteadyGroup"), rpm)
        else:
            disk_id = vsp.FindActuatorDisk(0)
            vsp.SetParmVal(vsp.FindParm(disk_id, "RotorRPM", "Rotor"), rpm)
            vsp.SetParmVal(vsp.FindParm(disk_id, "RotorCT", "Rotor"), ct)
            vsp.SetParmVal(vsp.FindParm(disk_id, "RotorCP", "Rotor"), cp)
            disk_id = vsp.FindActuatorDisk(1)
            vsp.SetParmVal(vsp.FindParm(disk_id, "RotorRPM", "Rotor"), rpm)
            vsp.SetParmVal(vsp.FindParm(disk_id, "RotorCT", "Rotor"), ct)
            vsp.SetParmVal(vsp.FindParm(disk_id, "RotorCP", "Rotor"), cp)

        print("--> Propeller created")

        return y_rel_loc, prop_length

    def generate_fuselage_d150(self):
        # TODO: Length Definition in CPACS???
        # Generate all Fuselage sections in CPACS Model and save as .fxs file for future usage
        # self.generate_fxs_file()

        print("--> Creating Fuselage")
        # Add Wing
        fuse_id = vsp.AddGeom('FUSELAGE')
        vsp.SetGeomName(fuse_id, self.fuselage['name'])

        # Cut the existing XSec, make plate for new XSec to be added
        vsp.CutXSec(fuse_id, 1)
        vsp.CutXSec(fuse_id, 1)
        vsp.CutXSec(fuse_id, 1)

        vsp.SetParmVal(fuse_id, 'TopLAngle', 'XSec_0', 0)
        vsp.SetParmVal(fuse_id, 'RightLAngle', 'XSec_0', 0)
        vsp.SetParmVal(fuse_id, 'TopLStrength', 'XSec_0', 1.0)
        vsp.SetParmVal(fuse_id, 'RightLStrength', 'XSec_0', 1.0)

        vsp.SetParmVal(fuse_id, 'Tess_W', 'Shape', 36)

        vsp.Update()

        # Move the Position of the Wing
        vsp.SetParmVal(fuse_id, 'X_Rel_Location', 'XForm',
                       float(self.fuselage['transformation']['translation']['x']))
        vsp.SetParmVal(fuse_id, 'Y_Rel_Location', 'XForm',
                       float(self.fuselage['transformation']['translation']['y']))
        vsp.SetParmVal(fuse_id, 'Z_Rel_Location', 'XForm',
                       float(self.fuselage['transformation']['translation']['z']))
        vsp.SetParmVal(fuse_id, 'X_Rel_Rotation', 'XForm',
                       float(self.fuselage['transformation']['rotation']['x']))
        vsp.SetParmVal(fuse_id, 'Y_Rel_Rotation', 'XForm',
                       float(self.fuselage['transformation']['rotation']['y']))
        vsp.SetParmVal(fuse_id, 'Z_Rel_Rotation', 'XForm',
                       float(self.fuselage['transformation']['rotation']['z']))

        # Get the number of fuselage sections from cpacs model
        section_count = len(self.fuselage['sections']['section'])

        section_scale = []
        section_translation = []

        for i in range(section_count):
            translation = self.fuselage['positionings']['positioning'][i]['length']
            section_translation.append(float(translation))
            translation_matrix = np.array(section_translation)
            self.vsp_fuse_section.length = translation_matrix

        for i in range(section_count):
            self.vsp_fuse_section.element_name.append(
                self.fuselage['sections']['section'][i]['elements']['element']['profileUID'])

            self.vsp_fuse_section.y_loc.append(
                float(self.fuselage['sections']['section'][i]['transformation']['translation']['y']))
            self.vsp_fuse_section.z_loc.append(
                float(self.fuselage['sections']['section'][i]['transformation']['translation']['z']))

            # section fuselage scaling(includes xyz value and saved as matrix)
            scaling = self.fuselage['sections']['section'][i]['elements']['element']['transformation']['scaling']
            x = float(scaling.get('x', 1))
            y = float(scaling.get('y', 1))
            z = float(scaling.get('z', 1))
            section_scale.append([x, y, z])
            scaling_matrix = np.array(section_scale)
            self.vsp_fuse_section.fuse_scale = scaling_matrix

        # Get the total length of the fuselage
        total_length = np.sum(self.vsp_fuse_section.length)
        vsp.SetParmVal(fuse_id, 'Length', 'Design', total_length)
        # Calculate the X position of each section in AbsCoordinate, thus getting XLocPercent for VSP model generation
        for i in range(section_count):
            self.vsp_fuse_section.x_loc.append(sum(self.vsp_fuse_section.length[0:i + 1]))
            self.vsp_fuse_section.x_percent.append((self.vsp_fuse_section.x_loc[i]) / total_length)
            self.vsp_fuse_section.z_percent.append(self.vsp_fuse_section.z_loc[i] / total_length)

        for i in range(section_count - 2):
            vsp.InsertXSec(fuse_id, i, 6)

        vsp.Update()

        for i in range(section_count):
            vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_' + str(i), 2)
            vsp.SetParmVal(fuse_id, 'XLocPercent', 'XSec_' + str(i), self.vsp_fuse_section.x_percent[i])
            vsp.SetParmVal(fuse_id, 'ZLocPercent', 'XSec_' + str(i), self.vsp_fuse_section.z_percent[i])
            vsp.SetParmVal(fuse_id, 'XRotate', 'XSec_' + str(i), 90)

            vsp.Update()

        for i in range(section_count):
            xsec_surf = vsp.GetXSecSurf(fuse_id, 0)
            vsp.ChangeXSecShape(xsec_surf, i, vsp.XS_FILE_FUSE)
            xsec = vsp.GetXSec(xsec_surf, i)
            vsp.ReadFileXSec(xsec, "./fuselage/" + self.vsp_fuse_section.element_name[i] + ".fxs")

            vsp.Update()

            # Get the diameter and Height of the section
            section_width = vsp.GetParmVal(fuse_id, 'Width', 'XSecCurve_' + str(i))
            section_height = vsp.GetParmVal(fuse_id, 'Height', 'XSecCurve_' + str(i))
            vsp.SetParmVal(fuse_id, 'Width', 'XSecCurve_' + str(i),
                           section_width * self.vsp_fuse_section.fuse_scale[i, 2])
            vsp.SetParmVal(fuse_id, 'Height', 'XSecCurve_' + str(i),
                           section_height * self.vsp_fuse_section.fuse_scale[i, 1])

            print("Fuselage Section " + str(i + 1) + " created" + " / " + str(section_count) + " in total")

    # TODO: COMPARE THIS WITH FUSELAGE GEOMETRY
    def generate_fuselage_stack(self):
        # TODO: Length Definition in CPACS???
        # Generate all Fuselage sections in CPACS Model and save as .fxs file for future usage
        # self.generate_fxs_file()

        print("--> Creating Fuselage")
        # Add Wing
        fuse_id = vsp.AddGeom('STACK')
        vsp.SetGeomName(fuse_id, self.fuselage['name'])

        # Cut the existing XSec, make plate for new XSec to be added
        vsp.CutXSec(fuse_id, 1)
        vsp.CutXSec(fuse_id, 1)
        vsp.CutXSec(fuse_id, 1)

        vsp.SetParmVal(fuse_id, 'Tess_W', 'Shape', 36)

        vsp.Update()

        # Move the Position of the Wing
        vsp.SetParmVal(fuse_id, 'X_Rel_Location', 'XForm',
                       float(self.fuselage['transformation']['translation']['x']))
        vsp.SetParmVal(fuse_id, 'Y_Rel_Location', 'XForm',
                       float(self.fuselage['transformation']['translation']['y']))
        vsp.SetParmVal(fuse_id, 'Z_Rel_Location', 'XForm',
                       float(self.fuselage['transformation']['translation']['z']))
        vsp.SetParmVal(fuse_id, 'X_Rel_Rotation', 'XForm',
                       float(self.fuselage['transformation']['rotation']['x']))
        vsp.SetParmVal(fuse_id, 'Y_Rel_Rotation', 'XForm',
                       float(self.fuselage['transformation']['rotation']['y']))
        vsp.SetParmVal(fuse_id, 'Z_Rel_Rotation', 'XForm',
                       float(self.fuselage['transformation']['rotation']['z']))

        # Get the number of fuselage sections from cpacs model
        section_count = len(self.fuselage['sections']['section'])

        section_scale = []
        section_translation = []

        for i in range(section_count):
            try:
                translation = self.fuselage['positionings']['positioning'][i]['length']
                section_translation.append(float(translation))
                translation_matrix = np.array(section_translation)
                self.vsp_fuse_section.length = translation_matrix

            except KeyError:
                print("Positioning in CPACS doesn't exist, try element translation to find XSec Position")
                translation = self.fuselage['sections']['section'][i]['elements']['element']['transformation'][
                    'translation']
                x = float(translation.get('x', 1))
                y = float(translation.get('y', 1))
                z = float(translation.get('z', 1))
                section_translation.append([x, y, z])
                translation_matrix = np.array(section_translation)
                self.vsp_fuse_section.length = translation_matrix

        for i in range(section_count):
            self.vsp_fuse_section.element_name.append(
                self.fuselage['sections']['section'][i]['elements']['element']['profileUID'])

            self.vsp_fuse_section.y_loc.append(
                float(self.fuselage['sections']['section'][i]['transformation']['translation']['y']))
            self.vsp_fuse_section.z_loc.append(
                float(self.fuselage['sections']['section'][i]['transformation']['translation']['z']))

            # section fuselage scaling(includes xyz value and saved as matrix)
            scaling = self.fuselage['sections']['section'][i]['elements']['element']['transformation']['scaling']
            x = float(scaling.get('x', 1))
            y = float(scaling.get('y', 1))
            z = float(scaling.get('z', 1))
            section_scale.append([x, y, z])
            scaling_matrix = np.array(section_scale)
            self.vsp_fuse_section.fuse_scale = scaling_matrix

        # Get the total length of the fuselage
        if np.ndim(self.vsp_fuse_section.length) == 1:
            # Calculate the X position of each section in AbsCoordinate,
            # thus getting XLocPercent for VSP model generation
            x_delta = [0]
            z_delta = [self.vsp_fuse_section.z_loc[0]]
            for i in range(1, section_count):
                x_delta.append(self.vsp_fuse_section.length[i])
            for i in range(section_count - 1):
                z_delta.append(self.vsp_fuse_section.z_loc[i + 1] - self.vsp_fuse_section.z_loc[i])

        if np.ndim(self.vsp_fuse_section.length) == 2:
            x_delta = [0]
            z_delta = [0]
            for i in range(section_count - 1):
                x_delta.append(self.vsp_fuse_section.length[i + 1, 0] - self.vsp_fuse_section.length[i, 0])
                z_delta.append(self.vsp_fuse_section.length[i + 1, 2] - self.vsp_fuse_section.length[i, 2])

        # Insert Xsec
        for i in range(section_count - 2):
            vsp.InsertXSec(fuse_id, i, 6)

        vsp.Update()

        for i in range(1, section_count):
            vsp.SetParmVal(fuse_id, 'SectTess_U', 'XSec_' + str(i), 2)
            vsp.SetParmVal(fuse_id, 'XDelta', 'XSec_' + str(i), x_delta[i])
            vsp.SetParmVal(fuse_id, 'ZDelta', 'XSec_' + str(i), z_delta[i])

            vsp.Update()

        for i in range(section_count):
            xsec_surf = vsp.GetXSecSurf(fuse_id, 0)
            vsp.ChangeXSecShape(xsec_surf, i, vsp.XS_FILE_FUSE)
            xsec = vsp.GetXSec(xsec_surf, i)
            vsp.ReadFileXSec(xsec, "./fuselage/" + self.vsp_fuse_section.element_name[i] + ".fxs")

            vsp.Update()

            # Get the diameter and Height of the section
            section_width = vsp.GetParmVal(fuse_id, 'Width', 'XSecCurve_' + str(i))
            section_height = vsp.GetParmVal(fuse_id, 'Height', 'XSecCurve_' + str(i))
            vsp.SetParmVal(fuse_id, 'Width', 'XSecCurve_' + str(i),
                           section_width * self.vsp_fuse_section.fuse_scale[i, 2])
            vsp.SetParmVal(fuse_id, 'Height', 'XSecCurve_' + str(i),
                           section_height * self.vsp_fuse_section.fuse_scale[i, 1])

            print("Fuselage Section " + str(i + 1) + " created" + " / " + str(section_count) + " in total")

    def generate_dat_file(self, name):
        af_count = len(self.wings_profile)

        for i in range(af_count):
            af_name = self.wings_profile[i]['@uID']
            try:
                x = self.wings_profile[i]['pointList']['x']['#text']
                z = self.wings_profile[i]['pointList']['z']['#text']
            except TypeError:
                x = self.wings_profile[i]['pointList']['x']
                z = self.wings_profile[i]['pointList']['z']

            # Split the string into a list using ';' as separator
            x_str = x.split(";")
            z_str = z.split(";")

            # Convert each string in the list to a float
            x_list = [float(num_str) for num_str in x_str]
            z_list = [float(num_str) for num_str in z_str]

            os.makedirs(f'./airfoil/{name}', exist_ok=True)

            # Open file to write data
            with open(f'./airfoil/{name}/' + af_name + '.dat', 'w') as f:
                # Write the coordinates into the file
                for xi, zi in zip(x_list, z_list):
                    f.write(f"{xi} {zi}\n")

            # Plot the profile and save as png
            plt.figure(figsize=(10, 5))
            plt.plot(x_list, z_list)
            plt.title(f'Airfoil Profile: {af_name}')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.xlim(0, 1)
            plt.ylim(-0.5, 0.5)
            plt.grid(True)
            plt.savefig(f'./airfoil/{name}/{af_name}.png', dpi=500)  # save as png with high resolution
            plt.close()  # close the figure

    def generate_af_file(self, name):
        af_count = len(self.wings_profile)

        for i in range(af_count):
            af_name = self.wings_profile[i]['@uID']

            try:
                x = self.wings_profile[i]['pointList']['x']['#text']
                z = self.wings_profile[i]['pointList']['z']['#text']
            except TypeError:
                x = self.wings_profile[i]['pointList']['x']
                z = self.wings_profile[i]['pointList']['z']

            # Split the string into a list using ';' as separator
            x_str = x.split(";")
            z_str = z.split(";")

            # Convert each string in the list to a float
            x_list = [float(num_str) for num_str in x_str]
            z_list = [float(num_str) for num_str in z_str]

            # convert to array
            x_array = np.asarray(x_list)
            z_array = np.asarray(z_list)
            af_array = np.column_stack((x_array, z_array))

            # Get half the length
            array_half_length = int(len(af_array) / 2) + 1

            # Get half the array
            af_array_first_half = af_array[:array_half_length]
            af_array_second_half = af_array[array_half_length:]

            # Add points to make af points closed
            af_array_first_half = np.vstack(([1, 0], af_array_first_half))
            af_array_second_half = np.vstack(([0, 0], af_array_second_half))

            af_array_second_half = np.unique(af_array_second_half, axis=0)

            # Flip the first array to match .af file
            af_array_first_half_flipped = np.flipud(af_array_first_half)
            af_array_first_half_flipped = np.unique(af_array_first_half_flipped, axis=0)

            if not np.array_equal(af_array_first_half_flipped[0], [0, 0]):
                af_array_first_half_flipped[0] = [0, 0]
            if not np.array_equal(af_array_first_half_flipped[-1], [1, 0]):
                af_array_first_half_flipped[-1] = [1, 0]
            if not np.array_equal(af_array_second_half[0], [0, 0]):
                af_array_second_half[0] = [0, 0]
            if not np.array_equal(af_array_second_half[-1], [1, 0]):
                af_array_second_half[-1] = [1, 0]

            first_has_negative = np.any(af_array_first_half_flipped < 0)

            if np.all(af_array_first_half_flipped[:, 1] == -af_array_second_half[:, 1]):
                sym_flag = 1
            else:
                sym_flag = 0

            first_array_length = len(af_array_first_half_flipped)
            second_array_length = len(af_array_second_half)

            os.makedirs(f'./airfoil/{name}', exist_ok=True)

            # Open file to write data
            with open(f'./airfoil/{name}/' + af_name + '.af', 'w') as f:
                f.write(f"DEMO GEOM AIRFOIL FILE\n")
                f.write(af_name + f"\n")
                if sym_flag == 1:
                    f.write(str(0) + " Sym Flag (0 - No, 1 - Yes)\n")
                else:
                    f.write(str(0) + " Sym Flag (0 - No, 1 - Yes)\n")

                # Write the coordinates into the file
                if first_has_negative == 1:
                    f.write(str(second_array_length) + " Num Pnts Upper\n")
                    f.write(str(first_array_length) + " Num Pnts Lower\n")
                    for row_1 in af_array_second_half:
                        f.write(f"{row_1[0]} {row_1[1]}\n")
                    f.write("\n")
                    for row_2 in af_array_first_half_flipped:
                        f.write(f"{row_2[0]} {row_2[1]}\n")
                else:
                    f.write(str(first_array_length) + " Num Pnts Upper\n")
                    f.write(str(second_array_length) + " Num Pnts Lower\n")
                    for row_1 in af_array_first_half_flipped:
                        f.write(f"{row_1[0]} {row_1[1]}\n")
                    f.write("\n")
                    for row_2 in af_array_second_half:
                        f.write(f"{row_2[0]} {row_2[1]}\n")

    def generate_fxs_file(self, name):
        fuse_count = len(self.fuselage_profile)

        for i in range(fuse_count):
            fuse_name = self.fuselage_profile[i]['@uID']
            try:
                y = self.fuselage_profile[i]['pointList']['y']['#text']
                z = self.fuselage_profile[i]['pointList']['z']['#text']
            except TypeError:
                y = self.fuselage_profile[i]['pointList']['y']
                z = self.fuselage_profile[i]['pointList']['z']

            # Split the string into a list using ';' as separator
            y_str = y.split(";")
            z_str = z.split(";")

            # Convert each string in the list to a float
            y_list = np.array([float(num_str) for num_str in y_str])
            z_list = np.array([float(num_str) for num_str in z_str])

            # In order to make feature line in VSPModel exactly in 0 90 180 270 degree
            # The y,z list should be fitted and interpolated to achieve a symmetrical
            # y,z coordinates

            # Convert to polar coordinates
            r_old = np.hypot(y_list, z_list)
            theta_old = np.arctan2(z_list, y_list)

            # Make theta increase clockwise
            theta_old = -theta_old

            # Shift theta so it starts from 0
            theta_old -= theta_old[0]

            # Make theta values between 0 and 2*pi
            theta_old %= 2 * np.pi

            # Sort theta_old and r_old
            sort_index = np.argsort(theta_old)
            theta_old = theta_old[sort_index]
            r_old = r_old[sort_index]

            # Remove duplicates based on theta_old
            theta_old, unique_indices = np.unique(theta_old, return_index=True)
            r_old = r_old[unique_indices]

            # Interpolate r using Rbf
            # tck = interpolate.splrep(theta_old, r_old, per=True)
            # rbf_interpolator = Rbf(theta_old, r_old, function='cubic')
            # cubic_spline_interpolator = CubicSpline(theta_old, r_old)
            interp_r = interp1d(theta_old, r_old, kind='linear', fill_value='extrapolate')

            # Generate new theta values
            theta_new = np.linspace(0, 2 * np.pi, 61)

            # Generate new r values
            # r_new = interpolate.splev(theta_new, tck)
            # r_new = rbf_interpolator(theta_new)
            # r_new = cubic_spline_interpolator(theta_new)
            r_new = interp_r(theta_new)

            # Convert back to Cartesian coordinates
            y_new = r_new * np.cos(-theta_new)
            z_new = r_new * np.sin(-theta_new)

            points_new = list(zip(y_new, z_new))

            rotated_points = [(x, y) for x, y in points_new]

            os.makedirs('./fuselage/' + name, exist_ok=True)

            # Open file to write data
            with open('.\\fuselage\\' + name + '\\' + fuse_name + '.fxs', 'w') as f:
                # The first line should always be this in order to let VSP recognize the file
                f.write(f"OPENVSP_XSEC_FILE_V1\n")
                # Write the coordinates into the file
                for xi, zi in rotated_points:
                    f.write(f"{xi:.3f}\t{zi:.3f}\n")

            y_points, z_points = zip(*rotated_points)

            # Plot the profile and save as png
            plt.figure(figsize=(10, 10))
            plt.plot(y_list, z_list, '-x')
            plt.plot(z_points, y_points, 'o-')
            plt.title(f'Fuselage Profile: {fuse_name}')
            plt.xlabel('y')
            plt.ylabel('z')

            # Set the x,y lim the same
            max_limit = max(max(y_new), max(z_new))
            min_limit = min(min(y_new), min(z_new))
            plt.xlim(min_limit, max_limit)
            plt.ylim(min_limit, max_limit)

            plt.grid(True)
            plt.savefig(f'./fuselage/{name}/{fuse_name}.png', dpi=500)  # save as png with high resolution
            plt.close()  # close the figure


# cpacs = CPACS(fr"C:\Users\chang.xu\wing_propeller_interaction\atr72-500_out.xml")
# cpacs = CPACS(fr"C:\Users\chang.xu\wing_propeller_interaction\Do328_out.xml")
# cpacs = CPACS(fr"C:\Users\chang.xu\wing_propeller_interaction\FLIPASED01.xml")
# vsp_model = VSP(cpacs)
# su2_analysis()

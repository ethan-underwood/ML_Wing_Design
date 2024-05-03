import openvsp as vsp
from utility_functions import get_data_from_vsp_file, get_data_from_vlm_output
import numpy as np

### Calculates the area and distance reference values from the parsed geometry file ###
def get_Xref_and_Sref(vspInputFile:str) -> tuple[float]:
    vsp.VSPRenew()

    # Assigns the wing component from the geometry to a variable
    vsp.ReadVSPFile(vspInputFile)
    geoms = vsp.FindGeoms()
    print(geoms)
    wing = geoms[0]

    # Assigns the chord geometry to a variable
    c_id = vsp.GetParm(wing, "Root_Chord", "XSec_1")
    # Recieves the root chord value from the geometry file
    rootChord = vsp.GetParmVal(c_id)
    # Calculates Xref as a quarter of the root chord
    Xref = rootChord/4

    # Calculates Sref
    areaID = vsp.GetParm(wing, "Area", "XSec_1")
    area = vsp.GetParmVal(areaID)
    Sref = area*2
    
    return Xref, Sref

def analyse_VLM(
        AoAStart, 
        AoAEnd,
        AlphaNpts,
        Xref,
        Sref
    ):
    # calculates geom
    analysisName = "VSPAEROComputeGeometry"
    vsp.SetAnalysisInputDefaults(analysisName)
    analysisMethod = list(vsp.GetIntAnalysisInput(analysisName, "AnalysisMethod" ))
    analysisMethod[0] = vsp.VORTEX_LATTICE
    vsp.SetIntAnalysisInput(analysisName, "AnalysisMethod", analysisMethod)
    vsp.ExecAnalysis(analysisName)
    
    # calculate sweep
    analysisName = "VSPAEROSweep"
    vsp.SetAnalysisInputDefaults(analysisName)
    vsp.SetDoubleAnalysisInput(analysisName, "AlphaStart", (AoAStart,), 0)
    vsp.SetDoubleAnalysisInput(analysisName, "AlphaEnd", (AoAEnd,), 0)
    vsp.SetIntAnalysisInput(analysisName, "AlphaNpts", (AlphaNpts,), 0)
    vsp.SetIntAnalysisInput(analysisName, "NCPU", (16,), 0)
    vsp.SetDoubleAnalysisInput(analysisName, "Xcg", (Xref,), 0)
    vsp.SetDoubleAnalysisInput(analysisName, "MachStart", (0.5,), 0)
    vsp.SetDoubleAnalysisInput(analysisName, "MachEnd", (0.5,), 0)
    vsp.SetIntAnalysisInput(analysisName, "MachNpts", (1,), 0)
    vsp.SetDoubleAnalysisInput(analysisName, "ReCref", (45e06,), 0 )
    vsp.SetIntAnalysisInput(analysisName, "ReCrefNpts", (1,), 0)
    vsp.SetDoubleAnalysisInput(analysisName, "Sref", (Sref,), 0)
    vsp.Update()
    vsp.DeleteAllResults()
    vsp.ExecAnalysis(analysisName)

def calculate_weight(
        vspFile:str,
        ultimateLoadFactor:float=2.5,
        mtow:float=1020
        ):
    aspectRatio = get_data_from_vsp_file(vspFile, "Aspect", "XSec_1")
    wingArea = get_data_from_vsp_file(vspFile, "Area", "XSec_1")
    taperRatio = get_data_from_vsp_file(vspFile, "Taper", "XSec_1")
    thickChordRatio = get_data_from_vsp_file(vspFile, "ThickChord", "XSecCurve_0")
    weight = 0.0038 * (ultimateLoadFactor * mtow)**1.06 * aspectRatio**0.38 * wingArea**0.25 * (1 + taperRatio)**0.21 * thickChordRatio**-0.14
    print(weight)
    return weight

# print(calculate_weight("IP_Data/Test_Folder/Predator/predator.vsp3", 2.5, 1020))
# print(calculate_weight("GAN/test/interpolate_test.vsp3", 2.5, 1020))

def calculate_range(
        LDRatio:float,
        vspFile:str,
        emptyWeightMinusWing:float=382, #kg
        grossWeight:float=1020, #kg
        sfc:float = 15e-7, #kg/W/s
        propEfficiency:float = 0.7,
        g:float=9.81 #m/s^2
        ):
    emptyWeight = emptyWeightMinusWing + calculate_weight(vspFile, mtow=grossWeight)
    print(LDRatio)
    return ((propEfficiency/(sfc * g)) * LDRatio * np.log(grossWeight/emptyWeight))/1000 # range in km

def calculate_range_from_files(
        vlmFile:str,
        vspFile:str,
        emptyWeightMinusWing:float=382, #kg
        grossWeight:float=1020, #kg
        sfc:float = 15e-7, #kg/W/s
        propEfficiency:float = 0.7,
        g:float=9.81 #m/s^2
        ):
    emptyWeight = emptyWeightMinusWing + calculate_weight(vspFile, mtow=grossWeight)
    LDRatio = get_data_from_vlm_output(vlmFile, "L/D")
    print(LDRatio)
    return ((propEfficiency/(sfc * g)) * LDRatio * np.log(grossWeight/emptyWeight))/1000 # range in km

predatorRange = calculate_range_from_files("IP_Data/Test_Folder/Predator/predator_DegenGeom.polar", "IP_Data/Test_Folder/Predator/predator.vsp3")
print(predatorRange)

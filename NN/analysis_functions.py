import openvsp as vsp

### Calculates the area and distance reference values from the parsed geometry file ###
def get_Xref_and_Sref(vspInputFile:str) -> tuple[float]:
    vsp.VSPRenew()

    # Assigns the wing component from the geometry to a variable
    vsp.ReadVSPFile(vspInputFile)
    geoms = vsp.FindGeoms()
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

from generation_functions import create_wing
from analysis_functions import get_Xref_and_Sref, analyse_VLM
from plotting_functions import plot_analysis
from utility_functions import get_data_from_vlm_output
import os
import numpy as np

create_wing("IP_Data/Test_Folder/Predator/predator.vsp3", 19/2, 14.8, 0.5, 2, 0.054, 0.022, 0.442)

def create_wings_from_iterated_parameter(iterableValues, parameter):
    print(np.linspace(iterableValues[0], iterableValues[1], iterableValues[2]))
    xValues = []
    yValues = []
    match parameter:
        case "aspectRatio":
            for aspectRatio in np.linspace(iterableValues[0], iterableValues[1], iterableValues[2]):
                vspFile = os.path.join("IP_Data/Test_Folder/AR_Folder/", f"ARx10-{round(aspectRatio*10)}.vsp3")
                if not os.path.exists(vspFile):
                    create_wing(vspFile, aspectRatio, 14.8, 0.5, 2, 0.054, 0.022, 0.442)
                    Xref, Sref = get_Xref_and_Sref(vspFile)
                    analyse_VLM(2, 2, 1, Xref, Sref)
                xValues.append(aspectRatio)
                yValues.append(get_data_from_vlm_output(os.path.join("IP_Data/Test_Folder/AR_Folder/", f"ARx10-{round(aspectRatio*10)}_DegenGeom.polar"), 'L/D'))
        case "span":
            for span in np.linspace(iterableValues[0], iterableValues[1], iterableValues[2]):
                vspFile = os.path.join("IP_Data/Test_Folder/Span_Folder/", f"Spanx10-{round(span*10)}.vsp3")
                if not os.path.exists(vspFile):
                    create_wing(vspFile, 19/2, span, 0.5, 2, 0.054, 0.022, 0.442)
                    Xref, Sref = get_Xref_and_Sref(vspFile)
                    analyse_VLM(2, 2, 1, Xref, Sref)
                xValues.append(span)
                yValues.append(get_data_from_vlm_output(os.path.join("IP_Data/Test_Folder/Span_Folder/", f"Spanx10-{round(span*10)}_DegenGeom.polar"), 'L/D'))
        case "taper":
            for taper in np.linspace(iterableValues[0], iterableValues[1], iterableValues[2]):
                vspFile = os.path.join("IP_Data/Test_Folder/Taper_Folder/", f"Taperx10-{round(taper*10)}.vsp3")
                if not os.path.exists(vspFile):
                    create_wing(vspFile, 19/2, 14.8, taper , 2, 0.054, 0.022, 0.442)
                    Xref, Sref = get_Xref_and_Sref(vspFile)
                    analyse_VLM(2, 2, 1, Xref, Sref)
                xValues.append(taper)
                yValues.append(get_data_from_vlm_output(os.path.join("IP_Data/Test_Folder/Taper_Folder/", f"Taperx10-{round(taper*10)}_DegenGeom.polar"), 'L/D'))
        case "sweep":
            for sweep in np.linspace(iterableValues[0], iterableValues[1], iterableValues[2]):
                vspFile = os.path.join("IP_Data/Test_Folder/Sweep_Folder/", f"Sweepx10-{round(sweep*10)}.vsp3")
                if not os.path.exists(vspFile):
                    create_wing(vspFile, 19/2, 14.8, 0.5 , sweep, 0.054, 0.022, 0.442)
                    Xref, Sref = get_Xref_and_Sref(vspFile)
                    analyse_VLM(2, 2, 1, Xref, Sref)
                xValues.append(sweep)
                yValues.append(get_data_from_vlm_output(os.path.join("IP_Data/Test_Folder/Sweep_Folder/", f"Sweepx10-{round(sweep*10)}_DegenGeom.polar"), 'L/D'))
        case "thickChord":
            for thickChord in np.linspace(iterableValues[0], iterableValues[1], iterableValues[2]):
                vspFile = os.path.join("IP_Data/Test_Folder/TC_Folder/", f"TCx100-{round(thickChord*100)}.vsp3")
                if not os.path.exists(vspFile):
                    create_wing(vspFile, 19/2, 14.8, 0.5 , 2, thickChord, 0.022, 0.442)
                    Xref, Sref = get_Xref_and_Sref(vspFile)
                    analyse_VLM(2, 2, 1, Xref, Sref)
                xValues.append(thickChord)
                yValues.append(get_data_from_vlm_output(os.path.join("IP_Data/Test_Folder/TC_Folder/", f"TCx100-{round(thickChord*100)}_DegenGeom.polar"), 'L/D'))
        case "camber":
            for camber in np.linspace(iterableValues[0], iterableValues[1], iterableValues[2]):
                vspFile = os.path.join("IP_Data/Test_Folder/Camber_Folder/", f"Camberx100-{round(camber*100)}.vsp3")
                if not os.path.exists(vspFile):
                    create_wing(vspFile, 19/2, 14.8, 0.5 , 2, 0.054, camber, 0.442)
                    Xref, Sref = get_Xref_and_Sref(vspFile)
                    analyse_VLM(2, 2, 1, Xref, Sref)
                xValues.append(camber)
                yValues.append(get_data_from_vlm_output(os.path.join("IP_Data/Test_Folder/Camber_Folder/", f"Camberx100-{round(camber*100)}_DegenGeom.polar"), 'L/D'))
        case "camberLoc":
            for camberLoc in np.linspace(iterableValues[0], iterableValues[1], iterableValues[2]):
                vspFile = os.path.join("IP_Data/Test_Folder/CamberLoc_Folder/", f"CamberLocx100-{round(camberLoc*100)}.vsp3")
                if not os.path.exists(vspFile):
                    create_wing(vspFile, 19/2, 14.8, 0.5 , 2, 0.054, 0.022, camberLoc)
                    Xref, Sref = get_Xref_and_Sref(vspFile)
                    analyse_VLM(2, 2, 1, Xref, Sref)
                xValues.append(camberLoc)
                yValues.append(get_data_from_vlm_output(os.path.join("IP_Data/Test_Folder/CamberLoc_Folder/", f"CamberLocx100-{round(camberLoc*100)}_DegenGeom.polar"), 'L/D'))
        case "AoA":
            for AoA in np.linspace(iterableValues[0], iterableValues[1], iterableValues[2]):
                vspFile = os.path.join("IP_Data/Test_Folder/AoA_Folder/", f"AoAx10-{round(AoA*10)}.vsp3")
                if not os.path.exists(vspFile):
                    create_wing(vspFile, 19/2, 14.8, 0.5 , 2, 0.054, 0.022, 0.442)
                    Xref, Sref = get_Xref_and_Sref(vspFile)
                    analyse_VLM(AoA, AoA, 1, Xref, Sref)
                xValues.append(AoA)
                yValues.append(get_data_from_vlm_output(os.path.join("IP_Data/Test_Folder/AoA_Folder/", f"AoAx10-{round(AoA*10)}_DegenGeom.polar"), 'L/D'))
    return xValues, yValues

def delete_files():
    for parameter in ["AR", "Span", "Taper", "Sweep", "TC", "Camber", "CamberLoc", "AoA"]:
        try:
            directoryPath = f"IP_Data/Test_Folder/{parameter}_Folder/"
            files = os.listdir(directoryPath)
            for file in files:
                filePath = os.path.join(directoryPath, file)
                if os.path.isfile(filePath):
                    print(filePath)
                    os.remove(filePath)
                    print("removed")
            print("All files deleted successfully.")
        except OSError:
            print("Error occurred while deleting files.")

noWings = 10
lowerBounds = [8/2, 13.4, 0, 0, 0.05, 0, 0.25, 0]
upperBounds = [20/2, 26.4, 1, 5, 0.2, 0.089, 0.7, 8]

#lowerBounds = [15/2, 7, 0, 0, 0.05, -0.1, 0.25, 0]
#upperBounds = [35/2, 32, 3, 10, 0.5, 0.1, 0.7, 8]


for parameter, lowerBound, upperBound in zip(["aspectRatio", "span", "taper", "sweep", "thickChord", "camber", "camberLoc", "AoA"], lowerBounds, upperBounds):
    print(parameter, lowerBound, upperBound)
    xValues, yValues = create_wings_from_iterated_parameter([lowerBound, upperBound, noWings], parameter)
    #define fixed y-axis range for L/D
    plot_analysis(
        xValues = xValues,
        yValues = yValues,
        pointLabels = [],
        output_file = os.path.join(os.getcwd(), f"IP_Data/Test_Folder/Test_{parameter}_vs_LD.png"),
        plotTitle = f"{parameter} vs the Lift Drag Ratio for the Iterated Test Sample",
        xLabel = parameter,
        yLabel = "Lift Drag Ratio"
    )

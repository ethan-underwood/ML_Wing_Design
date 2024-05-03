from generation_functions import create_random_input_params, create_wing, bucket_data
from analysis_functions import get_Xref_and_Sref, analyse_VLM
from plotting_functions import calculate_data_for_plotting, plot_analysis
import openvsp as vsp
import tempfile
import os
import pickle

numSamples = 8000
AoAStart = 5
AoAEnd = 5
AlphaNpts = 1
numEpochs = 500
batchSize = 25

### Generates 2 2D arrays, one scaled, another with values between 0 and 1, containing the random input wing parameters ###
multipleSampleParams, scaledMultipleSampleParams = create_random_input_params(numSamples)

### Defines plotting variables and parent directory ###
xValues = []
yValues = []
pointLabels = []
outputParentDir = "IP_Data/sample_set_timed"

### Machine learning data variables ###
MLInputData = []
MLOutputData = []

### Creates and analyses wings from generated scaled 2D array ###
for index, scaledSampleParams in enumerate(scaledMultipleSampleParams):
    vsp.VSPRenew()

    # Creates sample directory in either the parent directory if it exists, or a temporary if it does not 
    if outputParentDir:
        sampleOutputDir = os.path.join(outputParentDir, f'sample_{index}')
        os.makedirs(sampleOutputDir, exist_ok=True)
    else:
        sampleOutputDir = tempfile.TemporaryDirectory()
    vspFile = os.path.join(sampleOutputDir, 'wing_geom.vsp3')

    # Creates the wing in a .vsp file if it does not exist
    if not os.path.exists(vspFile):
        print(f'Creating wing {index}')
        create_wing(
            outputFile = vspFile,
            aspectRatio = scaledSampleParams[0],
            span = scaledSampleParams[1],
            taper = scaledSampleParams[2],
            sweep = scaledSampleParams[3],
            thickChord = scaledSampleParams[4],
            camber = scaledSampleParams[5],
            camberLoc = scaledSampleParams[6]
        )
    # Calculates the area and distance reference values
    Xref, Sref = get_Xref_and_Sref(vspFile)
    
    # Defines the file name for the polar file
    vlmAnalysisOutputFile = os.path.join(sampleOutputDir, 'wing_geom_DegenGeom.polar')
    # Runs the analysis on the wing previously created if the analysis has not already been completed
    if not os.path.exists(vlmAnalysisOutputFile):
        print(f'Running analysis {index}')
        analyse_VLM(scaledSampleParams[7], scaledSampleParams[7], AlphaNpts, Xref, Sref)
    else:
        print(f'Skipping analysis {index}')
    
    ### Gets L/D and Aspect Ratio values from the wing and its analysis for plotting later ###
    xValue, yValue = calculate_data_for_plotting(
        inputVSPFile = vspFile,
        inputVariable = "Aspect",
        inputXSecName = "XSec_1",
        outputPolarFile = vlmAnalysisOutputFile,
        outputVariable = "L/D"
    )
    # Appends values and labels to arrays
    xValues.append(xValue)
    yValues.append(yValue)
    pointLabels.append(str(index))

plot_analysis(
    xValues = xValues,
    yValues = yValues,
    pointLabels = pointLabels,
    output_file = os.path.join(os.getcwd(), 'Aspect_Ratio_vs_LD.png'),
    plotTitle = "Aspect Ratio vs the Lift Drag Ratio for the Generated Sample Set",
    xLabel = "Half Wing Aspect Ratio",
    yLabel = "Lift Drag Ratio"
)

sampleSetDictionary = bucket_data(5000, "IP_Data/sample_set_timed")
pickle.dump(sampleSetDictionary, open("rangesSampleSetDictionary.p", "wb"))

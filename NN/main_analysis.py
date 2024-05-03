import numpy as np

from generation_functions import create_random_input_params, create_wing
from analysis_functions import get_Xref_and_Sref, analyse_VLM
from plotting_functions import calculate_data_for_plotting, plot_analysis
from utility_functions import get_data_from_vlm_output, calculate_rmse, scale_sample
from model_functions import split_data_for_model, create_neural_network, train_neural_network, plot_loss
from scipy.stats import qmc
import openvsp as vsp
import tempfile
import os
import numpy as np

numSamples = 300
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
outputParentDir = "IP_Data/sample_set"

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
    
    ### Creates input data for ML model ###
    sampleInputVariables = []

    # Recieves and appends the L/D value from analysis
    sampleInputVariables.append(get_data_from_vlm_output(vlmAnalysisOutputFile, 'L/D'))

    # Creates a random array in an attempt to introduce randomness to the prediction of wing parameters
    randomSampler = qmc.LatinHypercube(d=8)
    randomArray = randomSampler.random(n=1)

    # Iterates through the 2D array and append the value to the input data
    for i in randomArray:
        for j in i:
            sampleInputVariables.append(j)
    MLInputData.append(sampleInputVariables)

    # Clean up if a temporary directory was used
    if not outputParentDir:
        sampleOutputDir.cleanup()

### Creates the output data set from the unscaled wing parameters ###
for index, sampleParams in enumerate(multipleSampleParams):
    MLOutputData.append(sampleParams)

plot_analysis(
    xValues = xValues,
    yValues = yValues,
    pointLabels = pointLabels,
    output_file = os.path.join(os.getcwd(), 'Aspect_Ratio_vs_LD.png'),
    plotTitle = "Aspect Ratio vs the Lift Drag Ratio for the Generated Sample Set",
    xLabel = "Half Wing Aspect Ratio",
    yLabel = "Lift Drag Ratio"
)

# ML training
MLInputDataNp = np.array(MLInputData)
MLOutputDataNp = np.array(MLOutputData)
trainInput, valInput, testInput, trainOutput, valOutput, testOutput = split_data_for_model(MLInputDataNp, MLOutputDataNp)

# Define output ranges
output_ranges = [(17.1/2, 38.7/2), (13.4, 26.4), (0, 1), (0, 5), (0.05, 0.2), (0, 0.089), (0.25, 0.7)]
model = create_neural_network(len(trainOutput[1]), output_ranges)

hist = train_neural_network(model, trainInput, trainOutput, valInput, valOutput, testInput, numEpochs)
plot_loss(hist)

# predict outputs
predictedOutputs = model.predict(testInput)
for predictedOutput in predictedOutputs:
    print(list(predictedOutput))
# calculate L/D for testOutput values
    
# scale outputs
scaledPredictedOutputs = scale_sample(predictedOutputs)
calculatedLDs = []
for index, sample_params in enumerate(scaledPredictedOutputs):
    vsp.VSPRenew()
    sample_params_list = list(sample_params)
    sample_params_list = [float(f) for f in sample_params_list]
    sample_output_dir = os.path.join(outputParentDir, f'model_test_sample_{index}')
    os.makedirs(sample_output_dir, exist_ok=True)
    vsp_file = os.path.join(sample_output_dir, 'wing_geom.vsp3')

    create_wing(
            outputFile = vsp_file,
            aspectRatio = sample_params_list[0],
            span = sample_params_list[1],
            taper = sample_params_list[2],
            sweep = sample_params_list[3],
            thickChord = sample_params_list[4],
            camber = sample_params_list[5],
            camberLoc = sample_params_list[6]
    )
    Xref, Sref = get_Xref_and_Sref(vsp_file)
    print(Sref)
    print(sample_params_list)
    
    vlm_analysis_output_file = os.path.join(sample_output_dir, 'wing_geom_DegenGeom.polar')
    analyse_VLM(AoAStart, AoAEnd, AlphaNpts, Xref, Sref)
    vlm_ld = get_data_from_vlm_output(vlm_analysis_output_file, 'L/D')
    calculatedLDs.append(vlm_ld)

testInputLDs = []
for i in testInput:
    testInputLDs.append(i[0])

print(list(testInputLDs), calculatedLDs)
print(f'RMSE = {calculate_rmse(list(testInputLDs), calculatedLDs)}')
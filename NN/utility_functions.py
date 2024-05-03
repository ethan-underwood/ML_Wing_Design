import openvsp as vsp
from scipy.stats import qmc

def get_data_from_vsp_file(
        inputVSPFile:str,
        inputVariable:str,
        inputXSecName:str,
    ) -> float:
    vsp.VSPRenew()
    vsp.ReadVSPFile(inputVSPFile)
    geoms = vsp.FindGeoms()
    wing = geoms[0]
    id = vsp.GetParm(wing, inputVariable, inputXSecName)
    value = vsp.GetParmVal(id)
    return value

def get_data_from_vlm_output(
        vlmOutputFile:str,
        variable:str
    
    ) -> float:
    with open(vlmOutputFile, 'r') as file:
        lines = file.readlines()
    data_line = lines[1]

    # Split the data line into individual values
    values = data_line.split()

    # Find the index of the 'L/D' column in the header
    header_line = lines[0]
    header_values = header_line.split()
    index = header_values.index(variable)
        # Extract the L/D value using the index
    value = float(values[index])
    return value

def calculate_rmse(list1, list2):
    sum_of_squares = 0
    for i in range(len(list1)):
        sum_of_squares += (list1[i] - list2[i]) ** 2

    mean_of_squares = sum_of_squares / len(list1)
    rmse = mean_of_squares ** 0.5

    return rmse

def getFirstValues(list):
    return [item[0] for item in list]

def scale_sample(sample):
    sampleLowerBounds = [17.1/2, 13.4, 0, 0, 0.05, 0, 0.25, 0]
    sampleUpperBounds = [38.7/2, 26.4, 1, 5, 0.2, 0.089, 0.7, 15]
    scaledSample = qmc.scale(sample, sampleLowerBounds, sampleUpperBounds)
    return scaledSample

#def bucketData():
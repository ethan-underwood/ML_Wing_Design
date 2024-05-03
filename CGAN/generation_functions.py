from scipy.stats import qmc
from utility_functions import scale_sample_without_LD
from analysis_functions import get_data_from_vlm_output, get_data_from_vsp_file, calculate_range_from_files
from numpy.random import rand
from numpy import ones, hstack
import openvsp as vsp
import numpy as np
import random
import os

def create_random_input_params(numSamples:int) -> list[list[float]]:
    # Creates random distribution
    # Also used to generate the fake samples
    sampler = qmc.LatinHypercube(d=8)
    sample = sampler.random(n=numSamples)
    scaledSample = scale_sample_without_LD(sample)
    return sample, scaledSample

def generate_fake_samples(numSamples):
    # create random 'inputs' (i.e. L/D)
    inputs = rand(numSamples)
    # create random 'outputs' (i.e. wing parameters)
    outputs = rand(numSamples, 8)
    # stack arrays
    inputs = inputs.reshape(numSamples, 1)
    outputs = outputs.reshape(numSamples, 1)
    samples = hstack((inputs, outputs))
    # create class labels
    labels = ones((numSamples, 1))
    return

def bucket_data(
        numSamples:int,
        fileDirectory:str,
        bucketStart:int=500, #km range
        bucketStop:int=2000 #km range
        ):
    #get bucket values and create nested dictionary, each bucket value is an open dictionary that will then include parameters
    bucketDictionary = {}
    if numSamples < 100:
        numBuckets = np.round(numSamples/100)
    else:
        numBuckets = 30 #i.e. every 50 km
    stepSize = (bucketStop - bucketStart)/numBuckets
    for bucket in list(np.arange(bucketStart, bucketStop + 1, stepSize)):
        bucketDictionary[bucket] = []
        print("bucket = ", bucket)
    #analyse each file, get L/D, round and sort parameters into dictionary
    directoryPath = fileDirectory
    files = os.listdir(directoryPath)
    for file in files:
        filePath = os.path.join(directoryPath, file)
        #print(filePath)

        rangeValue = calculate_range_from_files(os.path.join(filePath, "wing_geom_DegenGeom.polar"), os.path.join(filePath, "wing_geom.vsp3"))
        #LDValue = get_data_from_vlm_output(os.path.join(filePath, "wing_geom_DegenGeom.polar"), 'L/D')
        parameters = []
        for parameter, XSecName in zip(["Aspect", "Span", "Taper", "Sweep", "ThickChord", "Camber", "CamberLoc"], ["XSec_1", "XSec_1", "XSec_1", "XSec_1", "XSecCurve_0", "XSecCurve_0", "XSecCurve_0"]):
            parameters.append(get_data_from_vsp_file(os.path.join(filePath, "wing_geom.vsp3"), parameter, XSecName))
        parameters.append(get_data_from_vlm_output(os.path.join(filePath, "wing_geom_DegenGeom.polar"), 'AoA'))
        #parameters.append(LDValue)
        #print(parameters)
        closestKey = min(bucketDictionary.keys(), key=lambda x:abs(x-rangeValue))
        #print(bucketDictionary[closestKey])
        bucketDictionary[closestKey].append(parameters)
    print("Ranges assigned successfully")
    #print(bucketDictionary)
    return bucketDictionary

def collect_real_samples(
        numSamples:int, 
        sampleDirectory:str, 
        batchSize:int, 
        seqLength:int, 
        startBucket:int = 0, 
        endBucket:int = 50
        ):
    # get dictionary
    sampleDictionary = bucket_data(startBucket, endBucket, numSamples, sampleDirectory)
    
    labels = list(sampleDictionary.keys())
    numClasses = len(labels)

    # create empty arrays
    realData = np.zeros((batchSize, seqLength))
    #print("realData: ", realData)
    realLabels = np.zeros((batchSize, numClasses))
    
    # sample data points and labels
    for i in range(batchSize):
        # choose random label
        labelIndex = random.randint(0, numClasses - 1)
        label = labels[labelIndex]
        #print("label: ", label)

        # get the bucket for that label
        dataBucket = sampleDictionary[label]
        #print(dataBucket, "\n", len(sampleDictionary[label]))

        if len(dataBucket) != 0:
            # randomly sample a wing from the bucket
            dataIndex = random.randint(0, len(dataBucket) - 1)
            #print("dataBucket[dataIndex]: ", dataBucket[dataIndex])
            realData[i] = dataBucket[dataIndex]
            # create one-hot encoded label for the chosen label
            realLabels[i, labelIndex] = 1
        else:
            i = i - 1
    #realData = np.tile(realData[:, :, np.newaxis], (1, 1, 8))  # Repeat 8 times along the last axis
    return realData, realLabels


def create_wing(
        outputFile:str,
        aspectRatio:float = 20.0,
        span:float = 20.0,
        taper:float = 0.5,
        sweep:float = 2.0,
        thickChord:float = 0.1,
        camber:float = 0.05,
        camberLoc:float = 0.5
    ):
    stdout = vsp.cvar.cstdout
    errorMgr = vsp.ErrorMgrSingleton.getInstance()

    vsp.VSPCheckSetup()
    errorMgr.PopErrorAndPrint(stdout)

    vsp.VSPRenew()
    vsp.ClearVSPModel()
    #vsp.DeleteAllResults()

    #add wing component
    wing = vsp.AddGeom("WING", "")
    vsp.SetGeomName(wing, "Wing");

    vsp.SetDriverGroup(wing, 1, vsp.AR_WSECT_DRIVER, vsp.SPAN_WSECT_DRIVER, vsp.TAPER_WSECT_DRIVER)

    #define parameters
    vsp.SetParmVal(wing, "SectTess_U", "XSec_1", 25)
    vsp.SetParmVal(wing, "Aspect", "XSec_1", aspectRatio)
    vsp.SetParmVal(wing, "Span", "XSec_1", span)
    vsp.SetParmVal(wing, "Taper", "XSec_1", taper)
    vsp.SetParmVal(wing, "Sweep", "XSec_1", sweep)
    vsp.InsertXSec(wing, 0, vsp.XS_FOUR_SERIES)
    vsp.SetParmVal(wing, "ThickChord", "XSecCurve_0", thickChord)
    vsp.SetParmVal(wing, "Camber", "XSecCurve_0", camber)
    vsp.SetParmVal(wing, "CamberLoc", "XSecCurve_0", camberLoc)
    vsp.SetParmVal(wing, "ThickChord", "XSecCurve_1", thickChord)
    vsp.SetParmVal(wing, "Camber", "XSecCurve_1", camber)
    vsp.SetParmVal(wing, "CamberLoc", "XSecCurve_1", camberLoc)
    vsp.Update()
    vsp.SetVSP3FileName(outputFile)
    vsp.WriteVSPFile(vsp.GetVSPFileName())

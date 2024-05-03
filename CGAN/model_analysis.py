from utility_functions import create_one_hot_encoder_label, scale_sample
from analysis_functions import get_Xref_and_Sref, analyse_VLM
from generation_functions import create_wing, calculate_range_from_files
from plotting_functions import plot_size_of_buckets

from keras.models import load_model
import numpy as np
from sklearn.metrics import mean_squared_error
from math import sqrt
from matplotlib import pyplot as plt
from statistics import mean
import pickle

NOISE_DIM = 100
NUM_CLASSES = 31

# sampleSetDictionary = pickle.load(open("../rangesSampleSetDictionary.p", "rb"))
# plot_size_of_buckets(sampleSetDictionary)

generator = load_model("cGAN_Generator.h5")
# Generate instances for a given class
def generate_data(
        generator, 
        dataClass:list, 
        numInstances:int=1
        ):
    noise = np.random.normal(0, 1, (numInstances, NOISE_DIM))
    generatedData = generator.predict([noise, dataClass])
    print(generatedData)
    return generatedData

def find_range_of_predicted_wing(
        desiredRange:int, 
        fileID:str
        ):
    generatedDataOneHotEncodedLabel = create_one_hot_encoder_label(500, 2000, NUM_CLASSES, desiredRange)
    generatedData = scale_sample(generate_data(generator, np.asarray([generatedDataOneHotEncodedLabel])))
    generatedDataList = generatedData[0]
    print(generatedDataList)
    create_wing(f"GAN/test/rangeTest{fileID}.vsp3", generatedDataList[0].item(), generatedDataList[1].item(), generatedDataList[2].item(), generatedDataList[3].item(), generatedDataList[4].item(), generatedDataList[5].item(), generatedDataList[6].item())
    Xref, Sref = get_Xref_and_Sref(f"GAN/test/rangeTest{fileID}.vsp3")
    analyse_VLM(generatedDataList[7].item(), generatedDataList[7].item(), 1, Xref, Sref)
    generatedRangeFromFiles = calculate_range_from_files(f"GAN/test/rangeTest{fileID}_DegenGeom.polar", f"GAN/test/rangeTest{fileID}.vsp3")
    return generatedRangeFromFiles

# print(find_range_of_predicted_wing(1600, "Timed"))

# numberPredictedWingsPerBucket = 10
# rmseValues = []

# for desiredRange in list(np.arange(2000, 2050, 50)):
#     predictedRangeValues = []
#     actualRangeValue = np.full(numberPredictedWingsPerBucket, desiredRange)
#     for i in range(numberPredictedWingsPerBucket):
#         print(f"desiredRange: {desiredRange}")
#         print(f"iteration: {i}")
#         predictedRangeValues.append(find_range_of_predicted_wing(desiredRange, f"{desiredRange}_{i}"))
#     rmseValues.append(sqrt(mean_squared_error(actualRangeValue, predictedRangeValues)) )

# print(rmseValues)

sampleSetDictionary = pickle.load(open("rangesSampleSetDictionary.p", "rb"))

labels = list(sampleSetDictionary.keys())
# numberWings = []
# for values in list(sampleSetDictionary.values()):
#     numberWings.append(len(values))
# print(labels, numberWings)

# rmseValues = [518.3586859269416, 32.68493686655566, 66.3774500859612, 65.63183408587157, 64.47602591821244, 89.52676615767852, 118.3333873243037, 86.08022344743891, 85.16568138435339, 59.33584515834695, 71.22682178450687, 78.82064246801201, 88.41950373253252, 122.20994698554495, 133.92214300005497, 133.55154651016883, 155.45666101422444, 246.97019178689555, 197.84342360220975, 142.1474649272481, 125.09056910455963, 80.76925217951381, 244.5383160794446, 98.79134545426716, 183.07927674862057, 70.41397633195109, 102.9900301443438, 16.147279842053102, 134.96070285991505, 417.45756078730847, 134.3592497233013]
# buckets = list(np.arange(500, 2050, 50))

# plt.bar(buckets, rmseValues, color ='blue', width = 20)
# plt.title("The RMSE of the Range of 10 Predicted Wings for Each Bucket")
# plt.xlabel("Range (km)")
# plt.ylabel("RMSE (km)")
# #plt.savefig(os.path.join(os.getcwd(), "bucket_size.png"))
# plt.show()

# buckets = list(np.arange(525, 2075, 50))
# data1 = [518.3586859269416, 32.68493686655566, 66.3774500859612, 65.63183408587157, 64.47602591821244, 89.52676615767852, 118.3333873243037, 86.08022344743891, 85.16568138435339, 59.33584515834695, 71.22682178450687, 78.82064246801201, 88.41950373253252, 122.20994698554495, 133.92214300005497, 133.55154651016883, 155.45666101422444, 246.97019178689555, 197.84342360220975, 142.1474649272481, 125.09056910455963, 80.76925217951381, 244.5383160794446, 98.79134545426716, 183.07927674862057, 70.41397633195109, 102.9900301443438, 16.147279842053102, 134.96070285991505, 417.45756078730847, 134.3592497233013]
# data2 = numberWings

# fig, ax1 = plt.subplots()

# color = 'tab:red'
# ax1.set_xlabel('Range (km)')
# ax1.set_ylabel('RMSE (km)')
# ax1.bar(buckets, data1, color=color, width = 20, label="RMSE")

# ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

# color = 'tab:blue'
# ax2.set_ylabel('Number of wings in range bucket')  # we already handled the x-label with ax1
# ax2.bar(labels, data2, color=color,  width = 20, label="No. Wings")

# plt.title("RMSE Plotted Alongside the Number of Wings for Each Range Bucket")
# fig.legend(loc=1, bbox_to_anchor=(0.9, 0.88))
# plt.show()

# print(mean(rmseValues))

# rmseValuesWithoutOutliers = [32.68493686655566, 66.3774500859612, 65.63183408587157, 64.47602591821244, 89.52676615767852, 118.3333873243037, 86.08022344743891, 85.16568138435339, 59.33584515834695, 71.22682178450687, 78.82064246801201, 88.41950373253252, 122.20994698554495, 133.92214300005497, 133.55154651016883, 155.45666101422444, 246.97019178689555, 197.84342360220975, 142.1474649272481, 125.09056910455963, 80.76925217951381, 244.5383160794446, 98.79134545426716, 183.07927674862057, 70.41397633195109, 102.9900301443438, 16.147279842053102, 134.96070285991505]
# print(mean(rmseValuesWithoutOutliers))

import pandas as pd
data = pd.DataFrame(sampleSetDictionary)

import seaborn as sns

print(sampleSetDictionary)

# Create a FacetGrid
g = sns.FacetGrid(data, col="500", col_wrap=4, height=3)
g.map(plt.hist, "Range", bins=10, color='b')

plt.show()
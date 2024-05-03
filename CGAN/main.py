import numpy as np
import pickle
import random
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Concatenate, LeakyReLU
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

from generation_functions import create_wing
from analysis_functions import get_Xref_and_Sref, analyse_VLM, calculate_range_from_files, calculate_range
from utility_functions import scale_sample, scale_sample_between_01, get_data_from_vlm_output, create_one_hot_encoder_label, find_closest_bucket, scale_value

# Disable progress bar
tf.keras.utils.disable_interactive_logging()

# Constants
NOISE_DIM = 100
NUM_CLASSES = 31
NUM_FEATURES = 8
BATCH_SIZE = 32
TRAINING_STEPS = 3500

def collect_real_samples(
        sampleDictionary:dict,
        batchSize:int,
        seqLength:int,
        ):
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
        #print(sampleDictionary[label])

        # get the bucket for that label
        dataBucket = sampleDictionary[label]
        #print(dataBucket, "\n", len(sampleDictionary[label]))

        if len(dataBucket) != 0:
            # randomly sample a wing from the bucket
            dataIndex = random.randint(0, len(dataBucket) - 1)
            #print("dataBucket[dataIndex]: ", dataBucket[dataIndex])
            realData[i] = scale_sample_between_01(dataBucket[dataIndex])
            # create one-hot encoded label for the chosen label
            realLabels[i, labelIndex] = 1
        else:
            i = i - 1
    #realData = np.tile(realData[:, :, np.newaxis], (1, 1, 8))  # Repeat 8 times along the last axis
    return realData, realLabels

# Load dictionary
sampleSetDictionary = pickle.load(open("rangesSampleSetDictionary.p", "rb"))
print(sampleSetDictionary)

# Generator
def create_generator():
    noise_input = Input(shape=(NOISE_DIM,))
    class_input = Input(shape=(NUM_CLASSES,))
    merged_input = Concatenate()([noise_input, class_input])
    hidden1 = Dense(256, activation='relu')(merged_input)
    hidden2 = Dense(256, activation='relu')(hidden1)
    hidden3 = Dense(256, activation='relu')(hidden2)
    output = Dense(NUM_FEATURES, activation='sigmoid')(hidden3)
    model = Model(inputs=[noise_input, class_input], outputs=output)
    return model

# Discriminator
def create_discriminator():
    data_input = Input(shape=(NUM_FEATURES,))
    class_input = Input(shape=(NUM_CLASSES,))
    merged_input = Concatenate()([data_input, class_input])
    hidden1 = Dense(256)(merged_input)
    # activation1 = LeakyReLU(alpha=0.1)(hidden1) 
    # hidden2 = Dense(128)(activation1)
    activation2 = LeakyReLU(alpha=0.1)(hidden1)  # LeakyReLU activation
    output = Dense(1, activation='sigmoid')(activation2)
    model = Model(inputs=[data_input, class_input], outputs=output)
    return model

# cGAN
def create_cgan(generator, discriminator):
    noise_input = Input(shape=(NOISE_DIM,))
    class_input = Input(shape=(NUM_CLASSES,))
    generated_data = generator([noise_input, class_input])
    validity = discriminator([generated_data, class_input])
    model = Model(inputs=[noise_input, class_input], outputs=validity)
    return model

# Create and compile the Discriminator
discriminator = create_discriminator()
discriminator.compile(loss='mean_squared_error', optimizer=Adam())

# Create the Generator
generator = create_generator()

# Create the GAN
gan = create_cgan(generator, discriminator)

# Ensure that only the generator is trained
discriminator.trainable = False

gan.compile(loss='binary_crossentropy', optimizer=Adam())

# Train GAN
# dictionary to capture losses
losses = {
    'step': [],
    'discriminator_loss': [],
    'generator_loss': [],
}

for step in range(TRAINING_STEPS):
    # Select a random batch of real data with labels
    realBatch, labelsBatch = collect_real_samples(sampleSetDictionary, BATCH_SIZE, NUM_FEATURES)

    # Generate a batch of new data
    noise = np.random.normal(0, 1, (BATCH_SIZE, NOISE_DIM))
    generated_batch = generator.predict([noise, labelsBatch])

    # Train the discriminator
    real_loss = discriminator.train_on_batch([realBatch, labelsBatch], np.ones((BATCH_SIZE, 1)))
    fake_loss = discriminator.train_on_batch([generated_batch, labelsBatch], np.zeros((BATCH_SIZE, 1)))
    discriminator_loss = 0.5 * np.add(real_loss, fake_loss)

    # Train the generator
    generator_loss = gan.train_on_batch([noise, labelsBatch], np.ones((BATCH_SIZE, 1)))

    if step % 100 == 0:
        print(f'Training step {step}')
    losses['step'].append(step)
    losses['discriminator_loss'].append(discriminator_loss)
    losses['generator_loss'].append(generator_loss)

generator.save("cGAN_Generator2.h5")

import matplotlib.pyplot as plt
# Plot discriminator_loss against step
plt.plot(losses['step'], losses['discriminator_loss'], label='Discriminator Loss')

# Plot generator_loss against step
plt.plot(losses['step'], losses['generator_loss'], label='Generator Loss')

# Add labels and title
plt.xlabel('Step')
plt.ylabel('Loss')
plt.title('Discriminator and Generator Losses over Steps')

# Add legend
plt.legend()

plt.savefig("test.png")
# Show plot
#plt.show()

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

generatedData1OneHotEncodedLabel = create_one_hot_encoder_label(500, 2000, NUM_CLASSES, 1600)
generatedData1 = scale_sample(generate_data(generator, np.asarray([generatedData1OneHotEncodedLabel])))
generatedData1List = generatedData1[0]
print(generatedData1List)
create_wing("GAN/test/rangeTest1.vsp3", generatedData1List[0].item(), generatedData1List[1].item(), generatedData1List[2].item(), generatedData1List[3].item(), generatedData1List[4].item(), generatedData1List[5].item(), generatedData1List[6].item())
Xref, Sref = get_Xref_and_Sref("GAN/test/rangeTest1.vsp3")
analyse_VLM(generatedData1List[7].item(), generatedData1List[7].item(), 1, Xref, Sref)
generatedRangeFromFiles1 = calculate_range_from_files("GAN/test/rangeTest1_DegenGeom.polar", "GAN/test/rangeTest1.vsp3")

generatedData2OneHotEncodedLabel = create_one_hot_encoder_label(500, 2000, NUM_CLASSES, 800)
generatedData2 = scale_sample(generate_data(generator, np.asarray([generatedData2OneHotEncodedLabel])))
generatedData2List = generatedData2[0]
print(generatedData2List)
create_wing("GAN/test/rangeTest2.vsp3", generatedData2List[0].item(), generatedData2List[1].item(), generatedData2List[2].item(), generatedData2List[3].item(), generatedData2List[4].item(), generatedData2List[5].item(), generatedData2List[6].item())
Xref, Sref = get_Xref_and_Sref("GAN/test/rangeTest2.vsp3")
analyse_VLM(generatedData2List[7].item(), generatedData1List[7].item(), 1, Xref, Sref)
generatedRangeFromFiles2 = calculate_range_from_files("GAN/test/rangeTest2_DegenGeom.polar", "GAN/test/rangeTest2.vsp3")

generatedData3OneHotEncodedLabel = create_one_hot_encoder_label(500, 2000, NUM_CLASSES, 1200)
generatedData3 = scale_sample(generate_data(generator, np.asarray([generatedData3OneHotEncodedLabel])))
generatedData3List = generatedData3[0]
print(generatedData3List)
create_wing("GAN/test/rangeTest3.vsp3", generatedData3List[0].item(), generatedData3List[1].item(), generatedData3List[2].item(), generatedData3List[3].item(), generatedData3List[4].item(), generatedData3List[5].item(), generatedData3List[6].item())
Xref, Sref = get_Xref_and_Sref("GAN/test/rangeTest3.vsp3")
analyse_VLM(generatedData3List[7].item(), generatedData3List[7].item(), 1, Xref, Sref)
generatedRangeFromFiles3 = calculate_range_from_files("GAN/test/rangeTest3_DegenGeom.polar", "GAN/test/rangeTest3.vsp3")

print("1 - vlm L/D: ", get_data_from_vlm_output("GAN/test/rangeTest1_DegenGeom.polar", "L/D"))
print("1 - desired range: 1600 km")
print("1 - range from vlm: ", generatedRangeFromFiles1, "\n")

print("2 - vlm L/D: ", get_data_from_vlm_output("GAN/test/rangeTest2_DegenGeom.polar", "L/D"))
print("2 - desired range: 800 km")
print("2 - range from vlm: ", generatedRangeFromFiles2, "\n")

print("3 - vlm L/D: ", get_data_from_vlm_output("GAN/test/rangeTest3_DegenGeom.polar", "L/D"))
print("3 - desired range: 1200 km")
print("3 - range from vlm: ", generatedRangeFromFiles3, "\n")

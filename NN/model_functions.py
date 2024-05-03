import numpy as np
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import Callback
from keras import ops
import matplotlib.pyplot as plt

def split_data_for_model(
        inputData:list[float],
        outputData:list[list[float]]
    ):
    sampleSize = len(inputData)
    #split data into 3 groups so the model doesn't overfit
    trainSize = int(sampleSize*.6) #60% of the data is used for training
    valSize = int(sampleSize*.2) #20% is used to validate/improve the model as it is being trained
    testSize = int(sampleSize*.2) + 1 #20% is used to test the model with data never seen before

    trainInput, valInput, testInput = np.split(inputData, [trainSize, trainSize + valSize])
    trainOutput, valOutput, testOutput = np.split(outputData, [trainSize, trainSize + valSize])
    
    return trainInput, valInput, testInput, trainOutput, valOutput, testOutput


# Define the custom activation function
def custom_activation_for_outputs(x, min_values, max_values):
    """Normalizes each output node between its corresponding min and max values."""
    min_values = tf.constant(min_values)  # Convert lists to tensors
    max_values = tf.constant(max_values)

    normalized = (x - tf.math.reduce_min(x, axis=-1, keepdims=True)) / (tf.math.reduce_max(x, axis=-1, keepdims=True) - tf.math.reduce_min(x, axis=-1, keepdims=True))
    return normalized * (max_values - min_values) + min_values

def custom_loss_function(y_true, y_pred):
    squareDifference = ops.square(y_true - y_pred)
    variance = tf.math.reduce_variance([y_true, y_pred])
    return squareDifference + variance

def create_neural_network(
        numOutputValues:int,
        output_ranges
    ):
    min_values = [ min_max[0] for min_max in output_ranges]
    max_values = [ min_max[1] for min_max in output_ranges]

    print("min_values = ", min_values)
    print("max_values = ", max_values)
    
    model = Sequential([
        Dense(18, input_shape=(9,), activation='sigmoid'),
        Dense(18, activation='sigmoid', kernel_regularizer='l2'),
        Dense(18, activation='sigmoid'),
        Dense(numOutputValues, activation='sigmoid'),  # Output layer without activation
#        Lambda(
#            custom_activation_for_outputs,
#            arguments={
#                'min_values': min_values,
#                'max_values': max_values
#            }
#        )
    ])

    model.compile(loss=custom_loss_function, optimizer='adam')
    return model

# Custom callback 
class OutputMonitor(Callback):
    def __init__(self, training_data, test_data):
        self.training_data = training_data
        self.test_data = test_data
    
    def on_epoch_end(self, epoch, logs=None):
        train_predictions = self.model.predict(self.training_data)
        test_predictions = self.model.predict(self.test_data)

        # Analyze output values, print or log them
        print(f"Epoch {epoch + 1}:")
        print("Training outputs:", train_predictions)
        print("Test outputs:", test_predictions)

def train_neural_network(model, trainInput, trainOutput, valInput, valOutput, testInput, numEpochs):
    logdir='logs'

    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir)
    monitor = OutputMonitor(trainInput, testInput)
    
    print(len(trainInput))
    print(len(trainOutput))
    print(len(valInput))
    print(len(valOutput))

    hist = model.fit(
        trainInput,
        trainOutput,
        validation_data=(valInput, valOutput),
        epochs=numEpochs,
        callbacks=[tensorboard_callback, monitor],
        batch_size=25,
    )    
    return hist

def plot_loss(hist):
    fig = plt.figure()
    plt.plot(hist.history['loss'], color='blue', label='loss')
    plt.plot(hist.history['val_loss'], color='pink', label='val_loss')
    fig.suptitle('Loss', fontsize=20)
    plt.legend(loc="upper left")
    plt.savefig("Loss Curve.png")
    plt.show()
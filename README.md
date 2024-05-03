# A Machine Learning Approach to Conceptual Wing Design
This repository contains the code for the dissertation of [Ethan Underwood](https://www.linkedin.com/in/ethan-underwood-833426204/) for the individual project for the third year of Aeronautics and Astronautics at the University of Southampton.
## Abstract
By nature, aircraft design is iterative. If iteration could be removed from the process, countless person hours, and a large sum of money could be saved. The novelty of this project is to look at using machine learning models to solve the problem. At first Neural Networks were trialled due to their simplicity. Due to their shortcomings, the investigation was pivoted to Conditional Generative Adversarial Networks. As a proof of concept, the focus was centred on generating wings for a Medium Altitude Low Endurance Unmanned Aerial Vehicle (e.g., the MQ-1 Predator) based on range as a top-level requirement. It was found that, even after a relatively small amount of time spent optimising the model with the low computing power available, the model could be trained to give a wing that came within an average of 134 km of the desired range. By adapting the model architecture proposed here, a company could generate a new wing for a range in just ten minutes once the model has been trained. This report demonstrates that machine learning has significant potential as a viable method for design, especially with further optimisation outside the scope of this project.

## Neural Network Code
This folder contains the code files for the adapted Neural Network including sample set generation, and model trainig code.  
[code](NN)

## Conditional GAN Code
Contains the code files and the requirements.txt file necessary to generate a sample set, train the CGAN, and analyse the results.
If you want to train the model use the following instructions:   
```
pip install -r CGAN/requirements.txt
python CGAN/main.py
```
[code](CGAN)

## Dissertation Images
Both loss curves for the NN and CGAN can be found here, as well as two python files which plot the sizes of each bucket and the distribution of the parameters in each bucket.  
[code](Dissertation_Images)

## Input Data and Models 
This folder contains input data used to construct model and the saved models themselves  
- Input dictionaries are in pickle format:  `*.p`
- Models are in `*.h5` format  

[code](Input_Data_and_Models)
import pandas as pd
import pickle
import seaborn as sns
import matplotlib.pyplot as plt

with open('rangesSampleSetDictionary.p', 'rb') as infile:
    d = pickle.load(infile)
    

range_dict = {
    'bucket': [],
    'attribute_num': [],
    'value': []
}

for bucket in d:
    for instance in d[bucket]:
        for index, val in enumerate(instance):
            range_dict['bucket'].append(bucket)
            range_dict['attribute_num'].append(index+1)
            range_dict['value'].append(val)


df = pd.DataFrame().from_dict(range_dict)


for attribute_num in range(1,9):
    data_to_plot = df.query('attribute_num == @attribute_num')
    g = sns.FacetGrid(data_to_plot, col="bucket", col_wrap=4, height=3)
    g.map_dataframe(sns.histplot, x="value")
    plt.savefig(f'range_attribute_plots/range_attribute_{attribute_num}.png')
    

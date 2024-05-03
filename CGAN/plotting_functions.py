from matplotlib import pyplot as plt
from utility_functions import get_data_from_vsp_file, get_data_from_vlm_output
from analysis_functions import get_data_from_vlm_output


def calculate_data_for_plotting(
        inputVSPFile:str,
        inputVariable:str,
        inputXSecName:str,
        outputPolarFile:str,
        outputVariable:str = None
    ):
    xValue = get_data_from_vsp_file(
        inputVSPFile,
        inputVariable,
        inputXSecName,
    )

    yValue = get_data_from_vlm_output(
        outputPolarFile,
        outputVariable
    )

    return xValue, yValue

def plot_analysis(
            xValues:list[float],
            yValues:list[float],
            pointLabels:list[str],
            output_file: str,
            plotTitle:str = '', 
            xLabel:str = '',
            yLabel:str = '',
    ):
    plt.scatter(xValues, yValues)
    plt.title(plotTitle)
    for label, x, y in zip(pointLabels, xValues, yValues):
        plt.annotate(label, (x, y), textcoords="offset points", xytext=(0,10), ha='center')
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.legend()
    plt.savefig(output_file)
    plt.close()

def plot_size_of_buckets(
        dictionary:dict
    ):
    labels = list(dictionary.keys())
    numberWings = []
    for values in list(dictionary.values()):
        numberWings.append(len(values))
    print(labels, numberWings)
    #fig = plt.figure(figsize = (10, 5))
    plt.bar(labels, numberWings, color ='blue', width = 20)
    plt.title("The Number of Wings in Each Range Bucket")
    plt.xlabel("Range")
    plt.ylabel("Number of wings in range bucket")
    #plt.savefig(os.path.join(os.getcwd(), "bucket_size.png"))
    plt.show()

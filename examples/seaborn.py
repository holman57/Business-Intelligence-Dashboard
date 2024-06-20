import pandas as pd
import seaborn as sns


df = pd.read_csv("../data/PovStatsData.csv")

mpg = sns.load_dataset('mpg')
mpg.describe()
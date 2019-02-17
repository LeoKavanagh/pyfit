import pickle
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import mean_squared_error
import seaborn as sns
import matplotlib.pyplot as plt

def main():


    seed=42

    full_df = pd.read_csv('data/fitbit/processed_fitbit_df_r.csv')

    with open('models/mlruns/0/b72c2bd575704eefa564737c1c97ccfd/artifacts/gbr_model/model.pkl', 'rb') as f:
        model = pickle.load(f)

    X = full_df[['steps', 'mean_rate', 'sd_rate']]
    y = full_df['deep_sleep_prop']

    preds = model.predict(X)
    sns.regplot(y, preds)
    plt.show()

if __name__ == '__main__':
    main()

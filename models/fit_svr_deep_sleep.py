
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import mean_squared_error
import seaborn as sns
import matplotlib.pyplot as plt

def main():


    seed=314159

    full_df = pd \
        .read_csv('../datasets/processed_fitbit_df_r.csv') \
        .dropna()

    X = full_df[['steps', 'mean_rate', 'sd_rate', 'dsp_lag']]
    y = full_df['deep_sleep_prop']

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.66, random_state=seed)

    scaler = StandardScaler(with_mean=True, with_std=True)
    model = SVR()

    pipeline = Pipeline(steps=[('scaler', scaler),
                               ('model', model)])

    param_grid={"model__C": [1e0, 1e1, 1e2, 1e3],
                "model__gamma": np.logspace(-2, 2, 5),
                "model__kernel": ['rbf', 'linear']}

    grid_search = GridSearchCV(pipeline, param_grid=param_grid)

    with mlflow.start_run():

        grid_search.fit(X_train, y_train) 
        best_estimator = grid_search.best_estimator_
        preds = best_estimator.predict(X_test)

        mse = mean_squared_error(preds, y_test)
        rmse = np.sqrt(mse)
        mlflow.log_metric('mse', mse)
        mlflow.log_metric('rmse', rmse)

        mlflow.log_param('seed', seed)
        mlflow.log_param('C', best_estimator.steps[1][1].__dict__['C'])
        mlflow.log_param('gamma', best_estimator.steps[1][1].__dict__['gamma'])
        mlflow.log_param('kernel', best_estimator.steps[1][1].__dict__['kernel'])

        mlflow.sklearn.log_model(best_estimator, 'svr_model')

        plot_save_location = 'deep_sleep_regplot.png'
        plot = sns.regplot(y_test, preds).get_figure()
        plot.savefig(plot_save_location)
        mlflow.log_artifact(plot_save_location)


if __name__ == '__main__':
    main()

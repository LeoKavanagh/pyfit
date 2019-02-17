import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
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

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.75, random_state=seed)

    model = LinearRegression()


    with mlflow.start_run():

        # cv_model.fit(X_train, y_train) 
        best_estimator = model.fit(X, y) 
        preds = best_estimator.predict(X_test)

        mse = mean_squared_error(preds, y_test)
        rmse = np.sqrt(mse)
        mlflow.log_metric('mse', mse)
        mlflow.log_metric('rmse', rmse)

        for key, value in best_estimator.get_params().items():
            mlflow.log_param(key, value)

        mlflow.log_param('seed', seed)
        mlflow.sklearn.log_model(best_estimator, 'lr_model')

        plot_save_location = 'lr_deep_sleep_distplot.png'
        plt.close()
        plot = sns.distplot(y_test).get_figure()
        plot.savefig(plot_save_location)
        mlflow.log_artifact(plot_save_location)

        plot_save_location = 'lr_deep_sleep_regplot.png'
        plt.close()
        plot = sns.regplot(y_test, preds).get_figure()
        plot.savefig(plot_save_location)
        mlflow.log_artifact(plot_save_location)


if __name__ == '__main__':
    main()

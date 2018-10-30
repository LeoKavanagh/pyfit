# Sleep analysis

Register secret keys and all that for both Fitbit and Google Fit.

Download heart rate, steps/activity and sleep data from Fitbit and from Google Fit (the former is much better than the latter in my experience).

Process the historical data (some in R with dplyr, some with Pandas, mostly so I don't forget how to use either setup), 
pull daily stats into a dataset (whether this is a csv, sqlite database table or whatever is mostly irrelevant).

Fit a model on historical data to try to predict how well I will sleep tonight based on various heart rate and activity related stats. 

For now, I'm defining "sleep well" sleep well to mean "maximise the time spent in the 'deep sleep' state relative to total time spent asleep".

Use mlflow to track and model and data experimentation, and also to run existing models on unseen datasets.


## Authorise

### Fitbit
Run the `download_fitbit_data.py` script. Authorisation is taken care of with with functions from the `fitbit` package.

### Google
Turn on the flask server with `python flask_app.py`
Import the `authorise()` function and run it. It will give you a url to visit, which will return an alphanumeric string.
Enter this alphanumeric string into the terminal when prompted. I might try to make this a bit smoother. Maybe.


## Process

Turn the mostly raw API output into clean datasets with `process_fitbit_data.r` and `process_google_data.py`.
Mash these together into one unified dataset.

## Fit

Start the mlflow server by running `mlflow serve` in the terminal. It will start a localhost Flask app.
Make sure that the port it wants to run on is free.

In the `models/` directory there are scripts for fitting a load a different models via cross validation and logging the results
with mlflow.

## Predict

mlflow will give a run\_id - a hash to each model that has been logged. To use this model to predict from a csv input, run
```
mlflow pyfunc predict -m svr_model -r 3351dc69051240fe86d2bb02412e3069 -i ../datasets/test_input.csv
```

You can print to console or optionally save the results to a file using the `-o output_file_name.csv` flag.

## Prediction REST API

Get a prediction from the REST API with 
```
mlflow sklearn serve -m mlruns/0/b72c2bd575704eefa564737c1c97ccfd/artifacts/gbr_model/
```
Then in a different terminal send json inputs to the `predict` method of the sklearn model.
```
data=$(cat datsets/test_data.json)
curl -d $data -H 'Content-Type: application/json' -X POST localhost:5000/invocations
```

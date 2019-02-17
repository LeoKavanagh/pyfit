library(forecast)
library(tseries)
library(dplyr)
library(tidyr)

df = read.csv('datasets/combined_data.csv', header=TRUE) %>%
    select(date, mean_rate, 
           rate_range, deep_sleep_prop, dsp_lag) %>%
    filter(complete.cases(.))


count_ma = ts(na.omit(df$deep_sleep_prop), frequency=7)
decomp = stl(count_ma, s.window="periodic")
deseasonal_cnt <- seasadj(decomp)
plot(decomp)

# test for stationarity
adf.test(count_ma, alternative = "stationary")


model = auto.arima(count_ma)
fcast <- forecast(model, h=7)
plot(fcast)


model2 = auto.arima(count_ma, seasonal=TRUE)
fcast2 <- forecast(model2, h=7)
plot(fcast2)
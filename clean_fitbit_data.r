library(tidyr)
library(dplyr)


all_heart = read.csv('data/fitbit/heart/all_heart.csv')
all_steps = read.csv('data/fitbit/steps/fitbit_step_all.csv')
all_sleep = read.csv('data/fitbit/sleep/all_sleep.csv')

sleep = all_sleep %>%
	select(date, minutesAwake, 
	       minutesAsleep, minutesDeepSleep, minutesLightSleep,
	       minutesREMSleep) %>%
	filter(minutesDeepSleep > 0) %>%
	mutate(deep_sleep_prop = minutesDeepSleep/minutesLightSleep) %>%
	mutate(dsp_lag = lag(deep_sleep_prop))
	# mutate(deep_sleep_prop = minutesDeepSleep/(minutesAsleep + minutesAwake))

# drop zero values
steps = all_steps %>%
	select(date, steps) %>%
	filter(steps > 0)

heart = all_heart %>%
	arrange(date) %>%
	group_by(date) %>%
	mutate(mean_rate = mean(heart_rate)) %>%
	mutate(sd_rate = sd(heart_rate)) %>%
	select(date, mean_rate, sd_rate) %>%
	distinct()

# join
full_df = heart %>%
	left_join(steps, by='date') %>%
	left_join(sleep, by='date') %>%
	drop_na() %>%
	tbl_df() %>%
	mutate(date = as.Date(date))

full_df$dow = weekdays(as.Date(df$date))
full_df$weekend_night = 1.0 * full_df$dow %in% c('Friday', 'Saturday')

# save
write.csv(full_df, 'datasets/processed_fitbit_df.csv',
	  row.names=FALSE)

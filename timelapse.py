#!/usr/bin/python
import time
import yaml
import subprocess
from datetime import datetime, timedelta
import json
import os

SUNRISE_OFFSET_MINUTES = -60  # Start transition 1 hour before actual sunrise

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def load_sun_data():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    sun_data_file = os.path.join(current_dir, 'data', 'sun_data_2023.json')
    with open(sun_data_file, 'r') as file:
        return json.load(file)

def get_sun_times(date, sun_data):
    date_str = date.strftime('%m-%d')
    return sun_data.get(date_str, {}).get('sunrise'), sun_data.get(date_str, {}).get('sunset')

def is_within_transition_period(sunrise_time, sunset_time):
    sunrise = datetime.strptime(sunrise_time, '%H:%M') + timedelta(minutes=SUNRISE_OFFSET_MINUTES)
    sunset = datetime.strptime(sunset_time, '%H:%M')
    now = datetime.now()
    return sunset <= now <= sunset + timedelta(hours=2) or sunrise <= now <= datetime.strptime(sunrise_time, '%H:%M')

def is_nighttime(sunrise_time, sunset_time):
    sunset_end_transition = datetime.strptime(sunset_time, '%H:%M') + timedelta(hours=2)  # end of transition after sunset
    sunrise_start_transition = datetime.strptime(sunrise_time, '%H:%M') + timedelta(minutes=SUNRISE_OFFSET_MINUTES)  # start of transition before sunrise
    now = datetime.now().time()

    # Check if the time is after sunset's transition and before midnight
    if sunset_end_transition.time() <= now:
        return True
    # Check if the time is after midnight and before sunrise's transition
    elif now <= sunrise_start_transition.time():
        return True
    return False

def timelapse(config):
    sun_data = load_sun_data()
    interval = config['interval']
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    while True:
        today = datetime.now().date()
        sunrise_time, sunset_time = get_sun_times(today, sun_data)
        
        # If there's "never_sets", just run the daytime script
        if sunrise_time == "never_sets" or sunset_time == "never_sets":
            print("Running daytime script 1")
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image.py')])
        # If it's within the transition period, run the nighttime script
        elif is_within_transition_period(sunrise_time, sunset_time):
            print("Running nighttime script (transition)")
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image_night.py')])
        # If it's nighttime, run the nighttime script
        elif is_nighttime(sunrise_time, sunset_time):
            print("Running nighttime script")
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image_night.py')])
        # Otherwise, run the daytime script
        else:
            print("Running daytime script 2")
            subprocess.run(['python3', os.path.join(current_dir, 'capture_image.py')])

        time.sleep(interval)

if __name__ == "__main__":
    config = load_config(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml'))
    timelapse(config)

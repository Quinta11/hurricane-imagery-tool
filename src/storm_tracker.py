import numpy as np
import pandas as pd

class StormTracker:
    def __init__(self, data):
        self.data = data

    def get_center(self, target_time):
        t = pd.to_datetime(target_time)
        self.data['time'] = pd.to_datetime(self.data['time'])
        t_sec = self.data['time'].astype(np.int64) / 1e9  # convert to seconds
        lat = np.interp(t.timestamp(), t_sec, self.data['LAT'])
        lon = np.interp(t.timestamp(), t_sec, self.data['LON'])
        return lat, lon
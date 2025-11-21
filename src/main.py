from satellite_fetcher import SatelliteFetcher as SatFetcher
from satellite_processor import SatelliteProcessor as SatProcessor
from satellite_plotter import SatellitePlotter as SatPlotter
from storm_fetcher import StormFetcher
import pandas as pd
import numpy as np

def convert_band_input(input):
    if input == "ir":
        return "C13"
    elif input == "wv":
        return "C09"

def get_satellite(lon, year):
    if lon <= -106:
        satellite = "goes18"
    else:
        if year < 2025:
            satellite = "goes16"
        else:
            satellite = "goes19"
    
    return satellite

def convert_satellite(satellite):
    if satellite[0:4] == 'goes':
        converted_string = satellite[0:4] + '-' + satellite[4:6]

    return converted_string

def get_peak_frame(data, band="ir"):
    peak_row = data['WIND'].idxmax()
    date = peak_row
    year = date.year
    month = date.month
    day = date.day
    time = str(date.hour).zfill(2) + str(date.minute).zfill(2)


    satellite = get_satellite(float(data.loc[peak_row]['LON']), int(year))
    # print(storm.data.loc[peak_row])

    # year = int(data.loc[peak_row]['YEAR'])
    # month = int(data.loc[peak_row]['MONTH'])
    # day = int(data.loc[peak_row]['DAY'])
    # time = data.loc[peak_row]['TIME']
    
    

    # Initialize and fetch data
    goes = SatFetcher(year, month, day, time, convert_band_input(band), satellite)
    file = goes.fetch()

    # Process the fetched data
    processor = SatProcessor(goes.dataset, file)
    file_dict = processor.process()

    # Plot the processed data
    satellite = convert_satellite(satellite)
    plotter = SatPlotter(file_dict, data.loc[[peak_row]], satellite)
    plotter.plot()

def animate_dataframe(data, band = 'ir'):
    for index, row in data.iterrows():
        satellite = get_satellite(float(row['LON']), int(row['YEAR']))
        time = str(index.hour).zfill(2) + str(index.minute).zfill(2)
        # # print(row.YEAR, row.MONTH, row.DAY, time)
        goes = SatFetcher(int(row['YEAR']), int(row['MONTH']), int(row['DAY']), time, convert_band_input(band), satellite)
        file = goes.fetch()

        processor = SatProcessor(goes.dataset, file)
        file_dict = processor.process()

        satellite = convert_satellite(satellite)
        plotter = SatPlotter(file_dict, row, satellite)
        plotter.plot()

def get_max_eye_temp(data):
    for index, row in data.iterrows():
        if row['WIND'] < 125:
            continue
        satellite = get_satellite(float(row['LON']), int(row['YEAR']))
        time = str(index.hour).zfill(2) + str(index.minute).zfill(2)
        year, month, day = int(row['YEAR']), int(row['MONTH']), int(row['DAY'])

        goes = SatFetcher(year, month, day, time, convert_band_input(band), satellite)
        file = goes.fetch()

        processor = SatProcessor(goes.dataset, file)
        file_dict = processor.process()

        dist = (file_dict['lats'] - row['LAT'])**2 + (file_dict['lons'] - row['LON'])**2
        i, j = np.unravel_index(np.argmin(dist), dist.shape)

        search_deg = 0.3
        mask = (
            (file_dict['lats'] >= row['LAT'] - search_deg) &
            (file_dict['lats'] <= row['LAT'] + search_deg) &
            (file_dict['lons'] >= row['LON'] - search_deg) &
            (file_dict['lons'] <= row['LON'] + search_deg)
        )

        neighbors = file_dict['cmi_data'][mask]
        method2 = round(neighbors.max(), 2)

        # window = file_dict['cmi_data'][i-50:i+50, j-50:j+50]
        # method3 = window.max()


        # print(method3)
        print(f"{year}/{month}/{day} {time}z: {method2} @ ({row['LAT']}, {row['LON']}). Intensity = {row['WIND']}kts, {row['PRESSURE']}mb")


if __name__ == "__main__":
    band = "wv"
    atcf_id = "al142018"
    storm = StormFetcher(atcf_id)
    data = storm.interpolate_dataframe(storm.data)
    # get_max_eye_temp(data)

    # animate_dataframe(data)
    get_peak_frame(data)
import datetime as dt
import requests
import gzip
import shutil
import csv
import pandas as pd
from storm_tracker import StormTracker

pd.set_option('display.max_columns', None)

class StormFetcher:
    def __init__(self, atcf_id):
        self.atcf_id = atcf_id
        self.year = atcf_id[-4:]
        self.column_names = ["ATCF_ID", "YEAR", "MONTH", "DAY", "TIME", "NAME", "WIND", "PRESSURE", "LAT", "LON"]
        self.data = None

        self.fetch()
        self._create_dataframe()

    def _convert_coords(self, lat, lon):
        if lat[-1] == 'S':
            lat = '-' + lat.replace('S', '')
        else:
            lat = lat.replace('N', '')
        if lon[-1] == 'W':
            lon = '-' + lon.replace('W', '')
        else:
            lon = lon.replace('E', '')

        lat = lat[:-1] + '.' + lat[-1]
        lon = lon[:-1] + '.' + lon[-1]

        return float(lat), float(lon)

    def _get_row_data(self, row):
        date = row[2].strip()
        lat, lon = row[6].strip(), row[7].strip()
        lat, lon = self._convert_coords(lat, lon)

        row_dict = {
            "ATCF_ID": row[0] + row[1].strip(),
            "NAME": row[27].strip(),
            "YEAR": date[:4],
            "MONTH": date[4:6],
            "DAY": date[6:8],
            "TIME": date[8:10] + '00',
            "LAT": lat,
            "LON": lon,
            "WIND": row[8].strip(),
            "PRESSURE": row[9].strip(),
            "CLASSIFICATION": row[10].strip()
        }

        return row_dict

    def _convert_index_to_datetime(self):
        self.data['DATETIME'] = pd.to_datetime(self.data['YEAR'].astype(str) + '-' +
                                self.data['MONTH'].astype(str) + '-' +
                                self.data['DAY'].astype(str) + ' ' +
                                self.data['TIME'])
        
        self.data = self.data.set_index('DATETIME')   
        self.data = self.data.drop(columns=["YEAR", "MONTH", "DAY", "TIME"])

    def _create_dataframe(self):
        with open('storm_atcf.dat', 'r') as file:
            reader = csv.reader(file, delimiter=',')
            all_dicts = []
            for row in reader:
                # atcf_id, year, month, day, time, name, classification, wind, pressure, lat, lon = self._get_row_data(row)
                retrieved_dict = self._get_row_data(row)

                if retrieved_dict['CLASSIFICATION'] not in ['SS', 'TS', 'TD', 'HU']:
                    continue

                all_dicts.append(retrieved_dict)

            df = pd.DataFrame(all_dicts)
            df = df.drop_duplicates().reset_index(drop=True)
            self.data = df

        for column in ["WIND", "PRESSURE", "LAT", "LON"]:
            self.data[column] = pd.to_numeric(self.data[column])
        self._convert_index_to_datetime()

    def interpolate_dataframe(self, df, frequency = '10min'):
        new_time_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq=frequency)
        df = df.reindex(df.index.union(new_time_index))

        # Interpolate NaN values for LAT and LON
        df[['LAT', 'LON']] = df[['LAT', 'LON']].interpolate(method='linear')
        df = df.ffill()
        return df


    def fetch(self):
        if int(self.year) == dt.datetime.now().year:
            url = f"https://ftp.nhc.noaa.gov/atcf/btk/b{self.atcf_id}.dat"
            filename = f"storm_atcf.dat"
        else:
            url = f"https://ftp.nhc.noaa.gov/atcf/archive/{self.year}/b{self.atcf_id}.dat.gz"
            filename = f"storm_atcf.dat.gz"        

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            if filename.endswith('.gz'):
                uncompressed_filename = filename[:-3]
                with gzip.open(filename, 'rb') as f_in:
                    with open(uncompressed_filename, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                filename = uncompressed_filename
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
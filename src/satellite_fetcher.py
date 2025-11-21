import s3fs
import numpy as np
import netCDF4 as nc
import datetime as dt
from colormaps import cmaps
from satellite_processor import SatelliteProcessor
from satellite_plotter import SatellitePlotter

class SatelliteFetcher:
    def __init__(self, year, month, day, time, band, sat):
        self.year = year
        self.month = month
        self.day = day
        self.time = str(time).zfill(4)
        self.band = band
        self.sat = sat
        self.fs = s3fs.S3FileSystem(anon=True)
        self.dataset = None
    
    def _get_file(self, folderpath):
        return [self.fs.open(file, mode="rb") for file in folderpath]
    
    def _calc_julian_day(self):
        date = dt.date(self.year, self.month, self.day)
        return str(date.timetuple().tm_yday).zfill(3)

    def fetch(self):
        julian_day = self._calc_julian_day()
        folderpath = self.fs.glob(
            f's3://noaa-{self.sat}/ABI-L2-CMIPF/{self.year}/{julian_day}/*/*{self.band}_G*s{self.year}{julian_day}{self.time}*.nc'
        )
        file = self._get_file(folderpath)
        self.dataset = nc.Dataset(f"{self.band}_dataset", memory=file[0].read())
        return file
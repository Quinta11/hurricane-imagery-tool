import numpy as np
import datetime as dt

class SatelliteProcessor:
    def __init__(self, dataset, file):
        self.dataset = dataset
        self.file = file

    def _get_timestamp(self):
        t = self.dataset.variables['t'][:].item()
        reference_time = dt.datetime(2000, 1, 1, 12, 0, 0)
        data_time = reference_time + dt.timedelta(seconds=float(t))

        return data_time

    def _get_cmi_data(self):
        return self.dataset.variables['CMI'][:] - 273.15  # Convert from Kelvin to Celsius
    
    def _get_latlon(self):
        proj_info = self.dataset.variables['goes_imager_projection']
        x = self.dataset.variables['x'][:]
        y = self.dataset.variables['y'][:]

        H = proj_info.perspective_point_height + proj_info.semi_major_axis
        r_eq = proj_info.semi_major_axis
        r_pol = proj_info.semi_minor_axis
        lon_0 = np.deg2rad(proj_info.longitude_of_projection_origin)

        # Meshgrid of scan angles
        X, Y = np.meshgrid(x, y)

        # Convert to lat/lon (from NOAA formula)
        a = np.sin(X)**2 + (np.cos(X)**2) * (np.cos(Y)**2 + (r_eq**2 / r_pol**2) * (np.sin(Y)**2))
        b = -2 * H * np.cos(X) * np.cos(Y)
        c = H**2 - r_eq**2

        # r_s = (-b - np.sqrt(b**2 - 4 * a * c)) / (2 * a)
        r_s = (-b - np.sqrt(np.maximum(b**2 - 4 * a * c, 0))) / (2 * a)

        s_x = r_s * np.cos(X) * np.cos(Y)
        s_y = -r_s * np.sin(X)
        s_z = r_s * np.cos(X) * np.sin(Y)

        lat = np.rad2deg(np.arctan((r_eq**2 / r_pol**2) * (s_z / np.sqrt((H - s_x)**2 + s_y**2))))
        lon = np.rad2deg(lon_0 - np.arctan(s_y / (H - s_x)))
        lat[np.isnan(lat)] = np.nan
        lon[np.isnan(lon)] = np.nan

        return lon, lat
    
    def process(self):
        lons , lats = self._get_latlon()
        
        file_dict = {
            'time': self._get_timestamp(),
            'cmi_data': self._get_cmi_data(),
            'lats': lats,
            'lons': lons,
        }
        
        # print("Data and coordinates retrieved successfully.")
        return file_dict
    
from colormaps import cmaps
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as mtransforms
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import MultipleLocator

class SatellitePlotter:
    def __init__(self, file_dict, storm, satellite):
        self.file_dict = file_dict
        self.storm = storm
        self.satellite = satellite
        self.storm_center = [float(storm['LAT']), float(storm['LON'])]

    def _lon_formatter(self, x, pos):
        hemi = 'E' if x > 0 else ('W' if x < 0 else '')
        return f'{abs(x):.0f}{hemi}'

    def _lat_formatter(self, y, pos):
        hemi = 'N' if y > 0 else ('S' if y < 0 else '')
        return f'{abs(y):.0f}{hemi}'

    def _add_gridlines(self, fig, ax):
        ax.yaxis.set_major_locator(MultipleLocator(2))
        ax.xaxis.set_major_locator(MultipleLocator(2))

        ax.xaxis.set_major_formatter(FuncFormatter(self._lon_formatter))
        ax.yaxis.set_major_formatter(FuncFormatter(self._lat_formatter))
        ax.tick_params(axis='x', direction='in', labelcolor='white', bottom=False, labelbottom=False, labeltop=True, labelrotation=90, pad=-25)
        ax.tick_params(axis='y', direction='in', labelcolor='white', left=False, labelleft=False, labelright=True, pad=-25)

        shift = 3 / 72  # 5 points = 5/72 inch
        offset_x = mtransforms.ScaledTranslation(shift, 0, fig.dpi_scale_trans)
        offset_y = mtransforms.ScaledTranslation(0, shift, fig.dpi_scale_trans)

        for label in ax.xaxis.get_majorticklabels():
            label.set_horizontalalignment('left')  # anchor left so it moves cleanly
            label.set_transform(label.get_transform() + offset_x)
            

        for label in ax.yaxis.get_majorticklabels():
            label.set_verticalalignment('bottom')  # anchor left so it moves cleanly
            label.set_transform(label.get_transform() + offset_y)

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_clip_path(ax.patch)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.grid(color='white', linestyle='-', linewidth=0.7, which='major', zorder=0)


    def _add_footer(self, fig, ax, c):
        cax = ax.inset_axes([0, 0, 1, 0.03])
        colorbar = fig.colorbar(c, cax=cax, fraction=0.046, pad=0.00, orientation='horizontal')
        colorbar.ax.tick_params(labelbottom=False)
        ax.add_patch(patches.Rectangle(
            (0, 0.03),
            1,
            0.04,
            transform = ax.transAxes,
            facecolor='white',
            alpha=0.9,
            zorder=2
        ))

        plt.text(0.5, 0.05, "https://github.com/Quinta11/hurricane-imagery-tool", horizontalalignment='center', verticalalignment='center', fontsize=10, color='black', transform=ax.transAxes, zorder=2)

    def _add_header(self, ax):
        rect_x = 0
        rect_y = 0.94
        rect_width = 0.43
        rect_height = 0.06

        rectangle = patches.Rectangle(
            (rect_x, rect_y),
            rect_width,
            rect_height,
            transform = ax.transAxes,
            linewidth=1,
            edgecolor='black',
            facecolor='white',
            zorder=2,
            alpha=0.9  # Transparency of the fill
        )

        ax.add_patch(rectangle)
        plt.text(0.01, 0.98, f'{self.storm.index[0].month}/{self.storm.index[0].day}/{str(self.storm.index[0].year)[-2:]} {str(self.storm.index[0].hour).zfill(2) + str(self.storm.index[0].minute).zfill(2)}Z  {self.storm['ATCF_ID'].iloc[0]} {self.storm['NAME'].iloc[0]} {int(self.storm['PRESSURE'].iloc[0])}mb {int(self.storm['WIND'].iloc[0])}kts', fontsize=10, color='black', transform=ax.transAxes, zorder=2)
        file_hour = str(self.file_dict['time'].hour).zfill(2)
        file_minute = str(self.file_dict['time'].minute).zfill(2)
        file_time = file_hour + file_minute
        file_date = str(self.file_dict['time'].month).zfill(2) + '/' + str(self.file_dict['time'].day).zfill(2) + '/' + str(self.file_dict['time'].year)[-2:]
        plt.text(0.01, 0.96, f'{file_date} {file_time}Z  {self.satellite.upper()} IR', fontsize=10, color='black', transform=ax.transAxes, zorder=2)

    def plot(self):
        # Determine bounds to use for plot
        lon_min, lon_max = self.storm_center[1] - 5, self.storm_center[1] + 5
        lat_min, lat_max = self.storm_center[0] - 5, self.storm_center[0] + 5
        # norm = mcolors.Normalize(vmin=-90, vmax=40)
        norm = mcolors.Normalize(vmin=-95, vmax=60)

        # Create plot, and plot visual data from .nc file
        fig, ax = plt.subplots(figsize=(8,8),constrained_layout=True)
        c = ax.pcolormesh(self.file_dict['lons'], self.file_dict['lats'], self.file_dict['cmi_data'], cmap=cmaps['rbtop3'], norm=norm)

        # Adjust size of plot, corresponding to plotted storm
        plt.tight_layout()
        ax.set_xlim(lon_min, lon_max)
        ax.set_ylim(lat_min, lat_max)
        ax.set_aspect('equal')

        # Add details to plot, such as header and footer info + overlayed grid
        self._add_gridlines(fig, ax)
        self._add_footer(fig, ax, c)
        self._add_header(ax)
        
        # Save plotted data as .png file
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        plt.savefig('goes_satellite_plot.png', dpi=300, bbox_inches=extent, pad_inches=0)
        plt.close()
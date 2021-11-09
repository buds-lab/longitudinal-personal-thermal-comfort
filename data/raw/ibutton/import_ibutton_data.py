import pandas as pd
import os
import glob
import statsmodels.api as sm
from influxdb import InfluxDBClient, DataFrameClient
import credentials as cd

from matplotlib import pyplot as plt

# lowess function
lowess_sm = sm.nonparametric.lowess


def interactive_legend():
    fig = plt.gcf()
    ax = plt.gca()
    leg = plt.gca().get_legend()
    alpha_hidden = 0.2

    lines = ax.lines  # get the lines in the plot
    lined = dict()
    # we will set up a dict mapping legend line to orig line, and enable picking on the legend line
    for leg_line, orig_line in zip(leg.get_lines(), lines):
        leg_line.set_picker(5)  # 5 pts tolerance
        lined[leg_line] = orig_line

    def on_pick(event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        leg_line = event.artist
        orig_line = lined[leg_line]

        # vis = not origline.get_visible()
        # origline.set_visible(vis)

        # change the alpha of the line showed in the plot
        alpha = orig_line.get_alpha()
        if alpha is None:
            orig_line.set_alpha(alpha_hidden)
            alpha = alpha_hidden
        elif alpha > 0.8:
            orig_line.set_alpha(alpha_hidden)
            alpha = alpha_hidden
        else:
            orig_line.set_alpha(1)
            alpha = 1

        # Change the alpha on the line in the legend so we can see what lines have been toggled
        if alpha == alpha_hidden:
            leg_line.set_alpha(alpha_hidden)
        else:
            leg_line.set_alpha(1.0)
        fig.canvas.draw()

    def on_pressed(event):
        if event.button == 3:
            for eachLine in lines:
                eachLine.set_alpha(alpha_hidden)
            return
        elif event.button == 2:
            for eachLine in lines:
                eachLine.set_alpha(1.0)
            return

    fig.canvas.mpl_connect('pick_event', on_pick)
    fig.canvas.mpl_connect('button_press_event', on_pressed)


class DataImport:
    """This class is used to import those data that are not automatically imported in Influx, e.g. ibuttons"""

    def __init__(self):
        self.cwd = os.getcwd()
        self.dir_data = os.path.join(os.path.dirname(os.getcwd()), 'Data')
        self.client = DataFrameClient(host=cd.influx_host, 
                                      port=cd.influx_port, 
                                      username=cd.influx_username,
                                      password=cd.influx_passwd,
                                      database=cd.influx_database, 
                                      ssl=True, 
                                      verify_ssl=True)
        self.timeZone = 'Asia/Singapore'

    def create_db_influx(self, db_name):
        print("Create database: " + db_name)
        self.client.create_database(db_name)

    # todo I may need to create a function which imports the ubibot data

    def import_ibutton(self):
        files = dict()
        device = 'iButtons'
        ext = '.csv'
        path_files = os.path.join(os.path.dirname(self.cwd), 'Data', device, 'to_import')
        files[device] = glob.glob(path_files + f'\\*{ext}')

        # import data iButton
        if files['iButtons']:  # check if there are new files that need to be processed
            for file in files['iButtons']:
                # read file
                _ = pd.read_csv(file, skiprows=18)
                try:
                    _.index = pd.to_datetime(_['Date/Time'], format='%d/%m/%y %I:%M:%S %p')
                except:
                    _.index = pd.to_datetime(_['Date/Time'], format='%d/%m/%Y %H:%M')
                _.index = _.index.tz_localize(self.timeZone).tz_convert('UTC').tz_localize(None)
                # if unit F than convert to C
                if _['Unit'].unique() != 'C':
                    _['Value'] = (_['Value'] * 9 / 5) + 32
                # save device ID
                # _['ID'] = os.path.splitext(os.path.basename(file))[0].split('_')[0]
                _ = _[['Value']].rename(columns={'Value': 'Temperature'})
                # send data to Influx
                self.client.write_points(_, 'ibutton',
                                         {'ibutton_id': os.path.splitext(os.path.basename(file))[0].split('_')[0]},
                                         protocol='line', time_precision='ms')
                # # code to cancel measurements
                # self.client.delete_series(database='people', measurement='ibutton')
                # move file to imported folder
                os.rename(file, file.replace('to_import', 'imported'))

if __name__ == '__main__':
    # import ibutton data
    DataImport().import_ibutton()


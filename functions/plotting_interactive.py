import matplotlib.pyplot as plt
plt.switch_backend('Qt5Agg')

from matplotlib.widgets import Cursor

def select_point(x,data):
        fig = plt.figure(figsize=(11, 7))
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter(x,data, s=3)
        plt.ylabel('Force (V)')
        plt.xlabel('Sample')
        plt.show()
        cursor = Cursor(ax, useblit=True, color='k', linewidth=1)
        zoom_ok = False
        print('\nZoom or pan to view, \npress spacebar when ready to click:\n')
        while not zoom_ok:
            zoom_ok = plt.waitforbuttonpress()
        print('Click once to select sample corresponding to beginning of last artefact: ')
        val = plt.ginput(1)
        last_artefact_LFP = float(val[0][0])
        print('Selected values: ', last_artefact_LFP)
        plt.close()
        
        return last_artefact_LFP


import time
import nplab
import sys
from nplab.experiment import Experiment, ExperimentStopped
from nplab.utils.notified_property import DumbNotifiedProperty

#  Gui Imports
from nplab.ui.ui_tools import UiTools, QuickControlBox
from nplab.utils.gui import QtWidgets, get_qt_app, uic


# Worth asking for a manual position reading first to compare to!
class BioFuMExperiment(Experiment):
    reading_interval = DumbNotifiedProperty(5)

    def __init__(self, reading_interval=5):
        super().__init__()
        self.reading_interval = reading_interval #  Default: 5 seconds between readings

    def run(self, *args, **kwargs):
        iteration = 0
        try:
            self.log('Starting experiment')
            images = self.create_data_group("images_%d")
            spectra = self.create_data_group("spectra_%d")

            while True:
                self.log(f"Starting iteration {iteration}")
                iteration_start = time.time()

                self.log('Focusing')
                self.log('Dummy: Focusing!')
                self.log('Taking picture')
                self.log('Dummy: Taking picture!')
                self.log('Taking spectrum')
                self.log('Dummy: Taking spectrum!')

                if iteration == 3:
                    self.log(f'Stopping after iteration {iteration}')
                    self.stop()

                next_iteration = iteration_start + self.reading_interval
                time_to_wait = next_iteration - time.time()
                self.log(f'Iteration {iteration} complete. Waiting...')
                self.wait_or_stop(time_to_wait)
                iteration += 1
        except ExperimentStopped:
            self.log('Experiment stopped')
        except Exception as e:
            self.log('Error!')
            self.log(str(e))
            self.log('Ending experiment')
        # finally:
            #  Do any cleanup?


    def get_qt_ui(self):
        """Return a user interface for the experiment"""
        gb = QuickControlBox("BioFuM Experiment")
        gb.add_doublespinbox("reading_interval")
        gb.add_button("start")
        gb.add_button("stop")
        gb.auto_connect_by_name(self)
        return gb


class BioFuMExperiment_Gui(QtWidgets.QMainWindow, UiTools):
    def __init__(self, experiment, parent=None):
        super(BioFuMExperiment_Gui, self).__init__(parent)
        uic.loadUi('dummy-experiment-ui.ui', self)
        self.experiment = experiment

        self.Main_widget = self.replace_widget(
            self.Controls,                #  layout
            self.Main_widget, #  old_widget
            self.experiment.get_qt_ui())     #  new_widget


if __name__ == '__main__':
    # try:
    #     nplab.current_datafile()  # Open diagloue to create file
    # except Exception as e:
    #     print('Error trying to set dataset')
    #     print(e)

    try:
        bfm_experiment = BioFuMExperiment()
    except Exception as e:
        print('Error creating BioFuMExperiment')
        print(e)


    app = get_qt_app()
    bfm_experiment_gui = BioFuMExperiment_Gui(bfm_experiment)
    bfm_experiment_gui.show()
    sys.exit(app.exec_())

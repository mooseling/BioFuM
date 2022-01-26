import time
import nplab
import sys
import traceback
from nplab.experiment import Experiment, ExperimentStopped
from nplab.utils.notified_property import DumbNotifiedProperty
from nplab.instrument.stage import DummyStage
from nplab.instrument.spectrometer import DummySpectrometer
from nplab.instrument.camera import DummyCamera
from nplab.instrument.camera.camera_with_location import CameraWithLocation

#  Gui Imports
from nplab.ui.ui_tools import UiTools, QuickControlBox
from nplab.utils.gui import QtWidgets, get_qt_app, uic


# Worth asking for a manual position reading first to compare to!
class BioFuMExperiment(Experiment):
    reading_interval = DumbNotifiedProperty(1) #  minutes

    def __init__(self, reading_interval=1):
        super().__init__()
        self.reading_interval = reading_interval

        #  Iniialise devices
        self.stage = DummyStage()
        self.camera = DummyCamera()
        self.spectrometer = DummySpectrometer()
        self.camera_and_stage = CameraWithLocation(self.camera, self.stage)

    def run(self, *args, **kwargs):
        iteration = 0
        try:
            self.log('Starting experiment')
            images = self.create_data_group('images_%d')
            spectra = self.create_data_group('spectra_%d')

            while True:
                self.log(f"Starting iteration {iteration}")
                iteration_start = time.time()

                self.log('Taking picture')
                images.create_dataset('image_%d',
                                      data=self.camera.raw_image(
                                          bundle_metadata=True,
                                          update_latest_frame=True))
                self.log('Reading spectrum')
                spectra.create_dataset('spectrum_%d',
                                       data=self.spectrometer.read_spectrum(
                                           bundle_metadata=True))

                next_iteration = iteration_start + (self.reading_interval * 60)
                time_to_wait = next_iteration - time.time()
                self.log(f'Iteration {iteration} complete. Waiting...')
                self.wait_or_stop(time_to_wait)
                iteration += 1
        except ExperimentStopped:
            self.log('Experiment stopped')
        except Exception as e:
            self.log('Error!')
            self.log(str(e))
            self.log(traceback.format_exc())
            self.log('Ending experiment')


    def get_qt_ui(self):
        """Return a user interface for the experiment"""
        control_box = QuickControlBox("BioFuM Experiment")
        control_box.add_doublespinbox("reading_interval")
        control_box.add_button("start")
        control_box.add_button("stop")
        control_box.auto_connect_by_name(self)
        return control_box


class BioFuMExperiment_Gui(QtWidgets.QMainWindow, UiTools):
    def __init__(self, experiment, parent=None):
        super(BioFuMExperiment_Gui, self).__init__(parent)
        uic.loadUi('biofum-experiment.ui', self)
        self.experiment = experiment

        self.Main_widget = self.replace_widget(
            self.Controls,               #  layout
            self.Main_widget,            #  old_widget
            self.experiment.get_qt_ui()) #  new_widget

        self.Camera_viewer = self.replace_widget(
            self.Device_viewers_layout,
            self.Camera_viewer,
            self.experiment.camera_and_stage.get_qt_ui())

        self.Spectrometer_viewer = self.replace_widget(
            self.Device_viewers_layout,
            self.Spectrometer_viewer,
            self.experiment.spectrometer.get_qt_ui())


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

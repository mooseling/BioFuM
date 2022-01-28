import sys
import time
import nplab
import traceback
from nplab.experiment import Experiment, ExperimentStopped
from nplab.instrument.stage.Marzhauser.tango import Tango, translate_axis
from nplab.instrument.camera.lumenera import LumeneraCamera
from nplab.instrument.camera.camera_with_location import CameraWithLocation
from nplab.instrument.spectrometer.seabreeze import OceanOpticsSpectrometer
from nplab.utils.notified_property import DumbNotifiedProperty
from nplab.ui.ui_tools import UiTools, QuickControlBox
from nplab.utils.gui import QtWidgets, get_qt_app, uic


class BioFuMExperiment(Experiment):
    reading_interval = DumbNotifiedProperty(10)  # minutes

    def __init__(self, reading_interval=10):
        super().__init__()
        self.reading_interval = reading_interval

        #  Initialise devices
        self.stage = Tango(com_name='COM1')
        self.camera = LumeneraCamera()
        self.spectrometer = OceanOpticsSpectrometer(0)
        self.camera_and_stage = CameraWithLocation(self.camera, self.stage)

        velocities = self.stage.GetVel()
        self.x_velocity = velocities['x']
        self.y_velocity = velocities['y']
        self.z_velocity = velocities['z']

    def run(self):
        iteration = 0
        try:
            self.log('Starting experiment')
            images = self.create_data_group('images_%d')
            spectra = self.create_data_group('spectra_%d')

            while True:
                self.log(f"Starting iteration {iteration}")
                iteration_start = time.time()

                self.log('Focusing')
                self.camera_and_stage.autofocus()
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
            pass  # don't raise an error if we just clicked "stop"
        except Exception as e:
            self.log('Error!')
            self.log(str(e))
            self.log(traceback.format_exc())
            self.log('Ending experiment')
            raise ExperimentStopped()

    def get_qt_ui(self):
        """Return basic controls GUI for the experiment"""
        box = QuickControlBox("BioFuM Experiment")
        box.add_doublespinbox("reading_interval")
        box.add_button("start")
        box.add_button("stop")
        box.add_doublespinbox('x_velocity')
        box.add_doublespinbox('y_velocity')
        box.add_doublespinbox('z_velocity')
        box.auto_connect_by_name(self)
        box.setMinimumWidth(400)
        return box

    @property
    def x_velocity(self):
        print('x_velocity getter called')
        return self._x_velocity

    @x_velocity.setter
    def x_velocity(self, velocity):
        self.log(f'setting x velocity to {self._x_velocity}')
        axis_code = translate_axis('x')
        self.stage.SetVelSingleAxis(axis_code, velocity)
        self._x_velocity = velocity

    @property
    def y_velocity(self):
        print('y_velocity getter called')
        return self._y_velocity

    @y_velocity.setter
    def y_velocity(self, velocity):
        self.log(f'setting y velocity to {self._y_velocity}')
        axis_code = translate_axis('y')
        self.stage.SetVelSingleAxis(axis_code, velocity)
        self._y_velocity = velocity

    @property
    def z_velocity(self):
        print('z_velocity getter called')
        return self._z_velocity

    @z_velocity.setter
    def z_velocity(self, velocity):
        self.log(f'setting z velocity to {self._z_velocity}')
        axis_code = translate_axis('z')
        self.stage.SetVelSingleAxis(axis_code, velocity)
        self._z_velocity = velocity


class BioFuMExperimentGui(QtWidgets.QMainWindow, UiTools):
    def __init__(self, experiment, parent=None):
        super(BioFuMExperimentGui, self).__init__(parent)
        uic.loadUi('biofum-experiment.ui', self)
        self.experiment = experiment

        self.Main_widget = self.replace_widget(
            self.Controls,                # layout
            self.Main_widget,             # old_widget
            self.experiment.get_qt_ui())  # new_widget

        self.Stage_controls = self.replace_widget(
            self.Controls,
            self.Stage_controls,
            self.experiment.stage.get_qt_ui())

        self.Camera_viewer = self.replace_widget(
            self.Device_viewers_layout,
            self.Camera_viewer,
            self.experiment.camera.get_qt_ui())

        self.Spectrometer_viewer = self.replace_widget(
            self.Device_viewers_layout,
            self.Spectrometer_viewer,
            self.experiment.spectrometer.get_qt_ui())


if __name__ == '__main__':
    try:
        nplab.current_datafile()  # Open dialogue to create file
    except Exception as e:
        print('Error trying to set dataset')
        print(e)
        print('Stopping')
        quit()

    try:
        bfm_experiment = BioFuMExperiment()
    except Exception as e:
        print('Error creating BioFuMExperiment')
        print(e)
        print('Stopping')
        quit()

    app = get_qt_app()
    bfm_experiment_gui = BioFuMExperimentGui(bfm_experiment)
    bfm_experiment_gui.show()
    sys.exit(app.exec_())

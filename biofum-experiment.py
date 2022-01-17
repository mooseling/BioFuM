import time
import nplab
from nplab.experiment import Experiment, ExperimentStopped
from nplab.instrument.stage.Marzhauser.tango import Tango
from nplab.instrument.camera.lumenera import LumeneraCamera
from nplab.instrument.spectrometer.seabreeze import OceanOpticsSpectrometer


# Worth asking for a manual position reading first to compare to!
class BioFuMExperiment(Experiment):
    wait_time = 300 #  5 minutes between readings


    def __init__(self):
        super().__init__()

        #  Iniialise devices
        try:
            self.stage = Tango()
            self.camera = LumeneraCamera()
            self.spectrometer = OceanOpticsSpectrometer()
            self.camera_and_stage = CameraWithLocation(camera, stage)
        except Exception:
            pass


    def run(self):
        iterations = 0
        try:
            self.log('Starting experiment')
            images = self.create_data_group("images_%d")
            spectra = self.create_data_group("spectra_%d")

            while True:
                self.log(f"Starting iteration {iterations}")
                iteration_start = time()

                self.log('Focusing')
                self.camera_and_stage.autofocus()
                self.log('Taking picture')
                images.create_dataset(self.camera.raw_image(
                                      bundle_metadata=True,
                                      update_latest_frame=True))
                self.log('Taking spectrum')
                spectra.create_dataset(self.spectrometer.read_spectrum(
                    bundle_metadata=True))

                iterations += 1
                next_iteration = iteration_start + self.wait_time
                self.wait_or_stop(next_iteration - time())
        except ExperimentStopped:
            pass #don't raise an error if we just clicked "stop"
        except Exception as e:
            self.log('Error!')
            self.log(str(e))
            self.log('Ending experiment')
        # finally:
            #  Do any cleanup?


if __name__ == '__main__':
    try:
        nplab.current_datafile()  # Open diagloue to create file
    except Exception as e:
        print('Error trying to set dataset')
        print(e)

    try:
        bfm_experiment = BioFuMExperiment()
    except Exception as e:
        print('Error creating BioFuMExperiment')
        print(e)

    try:
        bfm_experiment.run()
    except Exception as e:
        print('Error calling BioFuMExperiment.run')
        print(str(e))

import time
import nplab
from nplab.experiment import Experiment, ExperimentStopped


# Worth asking for a manual position reading first to compare to!
class BioFuMExperiment(Experiment):
    def __init__(self, reading_interval=5):
        super().__init__()
        self.reading_interval = reading_interval #  Default: 5 seconds between readings

    def run(self):
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

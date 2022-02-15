import nplab
from nplab.experiment import Experiment
from nplab.instrument.spectrometer.seabreeze import OceanOpticsSpectrometer



class SpectrometerTest(Experiment):
    def __init__(self):
        super().__init__()

    def run(self):
        self.log('Begin Spectrometer test')

        self.log('Creating OceanOpticsSpectrometer object...')
        try:
            #  Only one spectrometer, so its index should be 0
            spectrometer = OceanOpticsSpectrometer(0)
        except Exception as e:
            self.log('Error!')
            self.log(str(e))
            self.log('Ending test')
            return  # no point carrying on if creation failed
        self.log('Done creating object')

        self.log('Getting a reading and saving it to datafile...')
        try:
            spectrometer.save_spectrum()
        except Exception as e:
            self.log('Error!')
            self.log(str(e))




if __name__ == '__main__':
    try:
        nplab.current_datafile()  # Open diagloue to create file
    except Exception as e:
        print('Error trying to set dataset')
        print(e)

    try:
        camera_test = SpectrometerTest()
    except Exception as e:
        print('Error creating SpectrometerTest')
        print(e)

    try:
        camera_test.run()
    except Exception as e:
        print('Error calling SpectrometerTest.run')
        print(str(e))

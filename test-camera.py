import nplab
from nplab.experiment import Experiment
from nplab.instrument.camera.lumenera import LumeneraCamera


class CameraTest(Experiment):
    def __init__(self):
        super().__init__()

    def run(self):
        self.log('Begin Lumenera Camera test')

        self.log('Creating Lumenera object...')
        try:
            camera = LumeneraCamera()
        except Exception as e:
            self.log('Error!')
            self.log(str(e))
            self.log('Ending test')
            return  # no point carrying on if creation failed
        self.log('Done creating object')

        #  =====================================================
        #  ================ White Balance Tests ================
        #  ====================== On-Chip ======================
        #  =====================================================

        try:
            self.log('Getting dimensions from metadata')
            image_size = camera.get_metadata()['image_size']
            self.log(f'image_size: {str(image_size)}')
            width, height = image_size

            self.log('Trying OneShotAutoWhiteBalance(0, 0, width, height)')
            try:
                # All 4 arguments are required, it raises an exception otherwise
                camera.cam.OneShotAutoWhiteBalance(0, 0, width, height)
            except Exception as e:
                self.log(f'Exception: {str(e)}')
        except Exception as e:
            self.log(f'Did something wrong: {str(e)}')

        self.log('Getting an image and saving')
        try:
            camera.save_raw_image()
        except Exception as e:
            self.log('Error!')
            self.log(str(e))

        #  =====================================================
        #  ====================== Digital ======================
        #  =====================================================

        try:
            self.log('Getting dimensions from metadata')
            image_size = camera.get_metadata()['image_size']
            self.log(f'image_size: {str(image_size)}')
            width, height = image_size

            self.log('Trying DigitalWhiteBalance(0, 0, width, height)')
            try:
                # All 4 arguments are required, it raises an exception otherwise
                camera.cam.DigitalWhiteBalance(0, 0, width, height)
            except Exception as e:
                self.log(f'Exception: {str(e)}')
        except Exception as e:
            self.log(f'Did something wrong: {str(e)}')

        self.log('Getting an image and saving')
        try:
            camera.save_raw_image()
        except Exception as e:
            self.log('Error!')
            self.log(str(e))


if __name__ == '__main__':
    try:
        nplab.current_datafile()  # Open dialogue to create file
    except Exception as e:
        print('Error trying to set dataset')
        print(e)

    try:
        camera_test = CameraTest()
    except Exception as e:
        print('Error creating CameraTest. Ending test.')
        print(e)
        exit()

    try:
        camera_test.run()
    except Exception as e:
        print('Error calling CameraTest.run')
        print(str(e))

import nplab
from nplab.experiment import Experiment


#  ====================== TANGO CLASS ======================
#  Normally we import this from nplab package
#  But we're going to make several versions and see what happens
#  This is test 2: Don't use byref in ConnectSimple(com_name)

from nplab.instrument import Instrument
from nplab.instrument.stage import Stage
import ctypes
import sys
import os


#  ====================== Loading the Tango DLL ======================
#  this is just compatibility code, do not use this once the problem is fixed
#  The old lines are commented out below, just swap them back in
stage_class_path = os.path.dirname(nplab.instrument.stage.__file__)
print(stage_class_path)


# Load the Tango DLL
system_bits = '64' if (sys.maxsize > 2**32) else '32'
# path_here = os.path.dirname(__file__)
# tango_dll = ctypes.cdll.LoadLibrary(f'{path_here}/DLL/{system_bits}/Tango_DLL.dll')
tango_dll = ctypes.cdll.LoadLibrary(f'{stage_class_path}/Marzhauser/DLL/{system_bits}/Tango_DLL.dll')

# Set arg types for all dll functions we call
# LSID: Used to tell the DLL which Tango we are sending a command to
# The DLL can have up to 8 simultaneously connected Tangos
tango_dll.LSX_CreateLSID.argtypes = [ctypes.POINTER(ctypes.c_int)]
tango_dll.LSX_ConnectSimple.argtypes = [ctypes.c_int, ctypes.c_int,
                                        ctypes.c_char_p,
                                        ctypes.c_int, ctypes.c_bool]
tango_dll.LSX_Disconnect.argtypes = [ctypes.c_int]
tango_dll.LSX_FreeLSID.argtypes = [ctypes.c_int]
tango_dll.LSX_SetDimensions.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, ctypes.c_int]
tango_dll.LSX_MoveRelSingleAxis.argtypes = [ctypes.c_int, ctypes.c_int,
                                            ctypes.c_double, ctypes.c_bool]
tango_dll.LSX_MoveAbsSingleAxis.argtypes = [ctypes.c_int, ctypes.c_int,
                                            ctypes.c_double, ctypes.c_bool]
tango_dll.LSX_GetPos.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_double),
                                 ctypes.POINTER(ctypes.c_double),
                                 ctypes.POINTER(ctypes.c_double),
                                 ctypes.POINTER(ctypes.c_double)]
tango_dll.LSX_GetPosSingleAxis.argtypes = [ctypes.c_int, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_double)]
tango_dll.LSX_GetVel.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_double),
                                 ctypes.POINTER(ctypes.c_double),
                                 ctypes.POINTER(ctypes.c_double),
                                 ctypes.POINTER(ctypes.c_double)]


class Tango(Stage):
    axis_names = ('x', 'y', 'z', 'a')

    def __init__(self, unit='m'):
        Instrument.__init__(self)
        self.unit = unit

        # Connect to Tango
        lsid = ctypes.c_int()
        return_value = tango_dll.LSX_CreateLSID(ctypes.byref(lsid))
        assert return_value == 0, f'Tango.LSX_CreateLSID returned {return_value}'
        self.lsid = lsid.value
        self.ConnectSimple(1, 'COM1', 57600, False)

        self.set_units(unit)

    def close(self):
        self.Disconnect()
        self.FreeLSID()

    def move(self, pos, axis=None, relative=False):
        """Move the stage along a single axis"""
        if axis not in self.axis_names:
            raise Exception(f'{axis} is not a valid axis, must be one of {self.axis_names}')
        axis_number = self.translate_axis(axis)
        if relative:
            self.MoveRelSingleAxis(axis_number, pos, True)
        else:
            self.MoveAbsSingleAxis(axis_number, pos, True)

    def get_position(self, axis=None):
        if axis is None:
            return self.GetPos()
        return self.GetPosSingleAxis(axis)

    def is_moving(self, axes=None):
        """Returns True if any of the specified axes are in motion."""
        velocities = self.GetVel()
        for velocity in velocities.values():
            if velocity != 0:
                return True
        return False

    def set_units(self, unit):
        """Sets all dimensions to the desired unit"""
        unit_code = Tango.translate_unit(unit)
        self.SetDimensions(unit_code, unit_code, unit_code, unit_code)

    @staticmethod
    def translate_unit(unit):
        if unit == 'Microsteps':
            return 0
        elif unit == 'um':
            return 1
        elif unit == 'mm':
            return 2
        elif unit == 'degree':
            return 3
        elif unit == 'revolutions':
            return 4
        elif unit == 'cm':
            return 5
        elif unit == 'm':
            return 6
        elif unit == 'inch':
            return 7
        elif unit == 'mil':
            return 8
        else:
            raise Exception(f'Tried to put translate unknown unit: {unit}')

    @staticmethod
    def translate_axis(axis):
        if axis == 'x':
            return 1
        elif axis == 'y':
            return 2
        elif axis == 'z':
            return 3
        elif axis == 'a':
            return 4
        else:
            raise Exception(f'Tried to translate unknown axis: {axis}')

    # ============== Wrapped DLL Functions ==============
    # The following functions directly correspond to Tango DLL functions
    # As much as possible, they should present Python-like interfaces:
    # 1) Accept and return Python variables, not ctype types
    # 2) Return values rather than set them to referenced variables
    # 3) Check for error codes and raise exceptions
    # Note: error codes and explanations are in the Tango DLL documentation
    def ConnectSimple(self, interface_type, com_name, baud_rate, show_protocol):
        com_name = com_name.encode('utf-8')
        try:
            return_value = tango_dll.LSX_ConnectSimple(ctypes.c_int(self.lsid),
                                                       ctypes.c_int(interface_type),
                                                       com_name,
                                                       ctypes.c_int(baud_rate),
                                                       ctypes.c_bool(show_protocol))
        except Exception as e:
            raise Exception(f'Tango.LSX_ConnectSimple raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_ConnectSimple returned {return_value}'

    def Disconnect(self):
        try:
            return_value = tango_dll.LSX_Disconnect(ctypes.c_int(self.lsid))
        except Exception as e:
            raise Exception(f'Tango.LSX_Disconnect raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_Disconnect returned {return_value}'

    def FreeLSID(self):
        try:
            return_value = tango_dll.LSX_FreeLSID(ctypes.c_int(self.lsid))
        except Exception as e:
            raise Exception(f'Tango.LSX_FreeLSID raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_FreeLSID returned {return_value}'

    def SetDimensions(self, x_dim, y_dim, z_dim, a_dim):
        try:
            return_value = tango_dll.LSX_SetDimensions(ctypes.c_int(self.lsid),
                                                       ctypes.c_int(x_dim),
                                                       ctypes.c_int(y_dim),
                                                       ctypes.c_int(z_dim),
                                                       ctypes.c_int(a_dim))
        except Exception as e:
            raise Exception(f'Tango.LSX_SetDimensions raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_SetDimensions returned {return_value}'

    def MoveAbsSingleAxis(self, axis_number, value, wait):
        try:
            return_value = tango_dll.LSX_MoveAbsSingleAxis(ctypes.c_int(self.lsid),
                                                           ctypes.c_int(axis_number),
                                                           ctypes.c_double(value),
                                                           ctypes.c_bool(wait))
        except Exception as e:
            raise Exception(f'Tango.LSX_MoveAbsSingleAxis raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_MoveAbsSingleAxis returned {return_value}'

    def MoveRelSingleAxis(self, axis_number, value, wait):
        try:
            return_value = tango_dll.LSX_MoveRelSingleAxis(ctypes.c_int(self.lsid),
                                                           ctypes.c_int(axis_number),
                                                           ctypes.c_double(value),
                                                           ctypes.c_bool(wait))
        except Exception as e:
            raise Exception(f'Tango.LSX_MoveRelSingleAxis raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_MoveRelSingleAxis returned {return_value}'

    def GetPos(self):
        x_pos = ctypes.c_double()
        y_pos = ctypes.c_double()
        z_pos = ctypes.c_double()
        a_pos = ctypes.c_double()
        try:
            return_value = tango_dll.LSX_GetPos(ctypes.c_int(self.lsid),
                                                ctypes.byref(x_pos),
                                                ctypes.byref(y_pos),
                                                ctypes.byref(z_pos),
                                                ctypes.byref(a_pos))
        except Exception as e:
            raise Exception(f'Tango.LSX_GetPos raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_GetPos returned {return_value}'
        return {'x': x_pos.value, 'y': y_pos.value,
                'z': z_pos.value, 'a': a_pos.value}

    def GetPosSingleAxis(self, axis_number):
        pos = ctypes.c_double()
        try:
            return_value = tango_dll.LSX_GetPosSingleAxis(ctypes.c_int(self.lsid),
                                                          ctypes.c_int(axis_number),
                                                          ctypes.byref(pos))
        except Exception as e:
            raise Exception(f'Tango.LSX_GetPosSingleAxis raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_GetPosSingleAxis returned {return_value}'
        return pos.value

    def GetVel(self):
        x_velocity = ctypes.c_double()
        y_velocity = ctypes.c_double()
        z_velocity = ctypes.c_double()
        a_velocity = ctypes.c_double()
        try:
            return_value = tango_dll.LSX_GetVel(ctypes.c_int(self.lsid),
                                                ctypes.byref(x_velocity),
                                                ctypes.byref(y_velocity),
                                                ctypes.byref(z_velocity),
                                                ctypes.byref(a_velocity))
        except Exception as e:
            raise Exception(f'Tango.LSX_GetVel raised exception: {str(e)}')
        assert return_value == 0, f'Tango.LSX_GetVel returned {return_value}'
        return {'x': x_velocity.value, 'y': y_velocity.value,
                'z': z_velocity.value, 'a': a_velocity.value}


#  ====================== END ======================


# Worth asking for a manual position reading first to compare to!
class TangoTest(Experiment):
    def __init__(self):
        super().__init__()

    def run(self):
        self.log('Begin Tango test')

        self.log('Creating Tango object...')
        try:
            tango = Tango('mm')
        except Exception as e:
            self.log(f'Error: {str(e)}')
            self.log('Ending test')
            return  # no point carrying on if creation failed
        self.log('Done creating object')

        self.log('Getting all positions...')
        self.get_all_positions(tango)

        self.log('Getting a-position just to see what happens...')
        try:
            a_pos = tango.get_position(Tango.translate_axis('a'))
            self.log(f'Done. a-position: {str(a_pos)}')
        except Exception as e:
            self.log(f'Error: {str(e)}')

        # One thing to find out: Will it move sequentially?
        self.log('Moving x +5mm')  # right
        try:
            tango.move(5, 'x', True)  # True for relative move
        except Exception as e:
            self.log(f'Error: {str(e)}')
        self.log('Done. Getting positions...')
        self.get_all_positions(tango)

        self.log('Moving x -5mm')  # left
        try:
            tango.move(-5, 'x', True)  # True for relative move
        except Exception as e:
            self.log(f'Error: {str(e)}')
        self.log('Done. Getting positions...')
        self.get_all_positions(tango)

        self.log('Moving y +5mm')  # backwards
        try:
            tango.move(5, 'y', True)  # True for relative move
        except Exception as e:
            self.log(f'Error: {str(e)}')
        self.log('Done. Getting positions...')
        self.get_all_positions(tango)

        self.log('Moving y -5mm')  # forwards
        try:
            tango.move(-5, 'y', True)  # True for relative move
        except Exception as e:
            self.log(f'Error: {str(e)}')
        self.log('Done. Getting positions...')
        self.get_all_positions(tango)

        self.log('Moving z +5mm')  # down
        try:
            tango.move(5, 'z', True)  # True for relative move
        except Exception as e:
            self.log(f'Error: {str(e)}')
        self.log('Done. Getting positions...')
        self.get_all_positions(tango)

        self.log('Moving z -5mm')  # up
        try:
            tango.move(-5, 'z', True)  # True for relative move
        except Exception as e:
            self.log(f'Error: {str(e)}')
        self.log('Done. Getting positions...')
        self.get_all_positions(tango)

        self.log('Closing Tango connection')
        try:
            tango.close()
        except Exception as e:
            self.log(f'Error: {str(e)}')

    def get_all_positions(self, tango):
        self.log('Getting position')
        try:
            pos = tango.GetPos()
            self.log(f'Done getting position. Result: {str(pos)}')
        except Exception as e:
            self.log(f'Error: {str(e)}')

        self.log('Getting x position')
        try:
            x_pos = tango.GetPosSingleAxis(Tango.translate_axis('x'))
            self.log(f'Done getting x position. Result: {str(x_pos)}')
        except Exception as e:
            self.log(f'Error: {str(e)}')

        self.log('Getting y position')
        try:
            y_pos = tango.GetPosSingleAxis(Tango.translate_axis('y'))
            self.log(f'Done getting y position. Result: {str(y_pos)}')
        except Exception as e:
            self.log(f'Error: {str(e)}')

        self.log('Getting z position')
        try:
            z_pos = tango.GetPosSingleAxis(Tango.translate_axis('z'))
            self.log(f'Done getting z position. Result: {str(z_pos)}')
        except Exception as e:
            self.log(f'Error: {str(e)}')


if __name__ == '__main__':
    try:
        nplab.current_datafile()  # Open diagloue to create file
    except Exception as e:
        print(f'Error trying to set dataset: {str(e)}')

    try:
        tango_test = TangoTest()
        tango_test.run()
    except Exception as e:
        print(f'Error creating and running TangoTest: {str(e)}')

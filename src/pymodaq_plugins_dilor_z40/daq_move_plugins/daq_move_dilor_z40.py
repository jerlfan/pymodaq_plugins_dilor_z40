from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, comon_parameters_fun, \
    main  # common set of parameters for all actuators
from pymodaq.utils.parameter import Parameter

from pymodaq.utils.daq_utils import ThreadCommand, getLineInfo  # object used to send info back to the main thread
from easydict import EasyDict as edict  # type of dict
from pymodaq_plugins_dilor_z40.hardware.arduino_wrapper import ActuatorWrapper

from serial.tools import list_ports

ports = [str(port.name) for port in list_ports.comports()]
port = 'COM5'


#########


class DAQ_Move_dilor_z40(DAQ_Move_base):
    """Plugin for the Template Instrument

    This object inherits all functionality to communicate with PyMoDAQ Module through inheritance via DAQ_Move_base
    It then implements the particular communication with the instrument

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library
    # TODO add your particular attributes here if any

    """
    _controller_units = ActuatorWrapper.units  # TODO for your plugin: put the correct unit here
    is_multiaxes = False  # TODO for your plugin set to True if this plugin is controlled for a multiaxis controller
    stage_names = ['Motor 1']

    axes_names = ['grating']  # TODO for your plugin: complete the list
    _epsilon = 1  # TODO replace this by a value that is correct depending on your controller

    params = [  ## TODO for your custom plugin
                 # elements to be added here as dicts in order to control your custom stage
                 ############
                 {'title': 'Com port:', 'name': 'comport', 'type': 'str', 'limits': ports, 'value': port,
                  'tip': 'The serial COM port'},
                 # {'title': 'Laser wavelength:', 'name': 'wavelength', 'type': 'float', 'limits': ports, 'value': port,
                 # 'tip': 'The wavelength of the laser'},
                 {'title': 'Acceleration:', 'name': 'accel', 'type': 'int', 'value': 200,
                  'tip': 'Set the stepper motor acceleration'},
                 {'title': 'Max speed:', 'name': 'maxspeed', 'type': 'int', 'value': 1000,
                  'tip': 'Set the stepper motor max speed'},
             ] + comon_parameters_fun(is_multiaxes, axes_names, epsilon=_epsilon)

    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller: ActuatorWrapper  # = None

        # TODO declare here attributes you want/need to init with a default value
        pass

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        ## TODO for your custom plugin
        # raise NotImplemented  # when writing your own plugin remove this line
        pos = self.controller.get_value()  # when writing your own plugin replace this line
        pos = self.get_position_with_scaling(pos)
        self.emit_status(ThreadCommand('check_position', [pos]))
        return pos

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        self.controller.close_communication()  # when writing your own plugin replace this line

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        self.controller.accel_set(self.settings.child(('accel')).value())
        self.controller.max_speed_set(self.settings.child(('maxspeed')).value())

        if param.name() == 'accel':
            self.controller.accel_set(self.settings['accel'])
        elif param.name() == 'maxspeed':
            self.controller.max_speed_set(self.settings['maxspeed'])

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        # raise NotImplemented  # TODO when writing your own plugin remove this line and modify the one below
        # self.controller = ActuatorWrapper()
        self.ini_stage_init(old_controller=controller, new_controller=ActuatorWrapper())
        self.controller.open_communication(self.settings.child(('comport')).value())

        self.controller.accel_set(self.settings.child(('accel')).value())
        self.controller.max_speed_set(self.settings.child(('maxspeed')).value())

        info = "Connected"
        initialized = True  # self.controller.a_method_or_atttribute_to_check_if_init()  # todo
        return info, initialized

    def move_abs(self, value):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """
        value = self.check_bound(value)  # if user checked bounds, the defined bounds are applied here
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one

        ## TODO for your custom plugin
        self.controller.move_at(value)  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def move_rel(self, value):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        value = self.check_bound(self.get_actuator_value() + value)
        self.target_value = value
        value = self.set_position_relative_with_scaling(value)

        self.controller.move_at(value)  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def move_home(self):
        """Call the reference method of the controller"""

        ## TODO for your custom plugin
        self.move_abs(0)
        # self.controller.move_at(0)  # when writing your own plugin replace this line
        # self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

    def stop_motion(self):
        """Stop the actuator and emits move_done signal"""

        ## TODO for your custom plugin
        self.move_abs(0)
        # self.controller.your_method_to_stop_positioning()  # when writing your own plugin replace this line
        # self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))


if __name__ == '__main__':
    main(__file__)

import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from pymodaq_plugins_dilor_z40.hardware.ruler_wrapper import IK220


class DAQ_0DViewer_dilor_z40(DAQ_Viewer_base):
    """
    """
    params = comon_parameters+[{'title': 'Axis:', 'name': 'axis', 'type': 'int', 'value': 1.00},
        {'title': 'Laser Wavelength (nm):', 'name': 'las_wave', 'type': 'float', 'value': 457.00},
        {'title': 'correction:', 'name': 'correc', 'type': 'float', 'value': 5904.492}
        ## TODO for your custom plugin: elements to be added here as dicts in order to control your custom stage
        ]

    #def __init__(self, parent=None, params_state=None):
    #    super().__init__(parent, params_state)
    #    self.controller = None

    #def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
     #   self.controller = IK220()

        #TODO declare here attributes you want/need to init with a default value
        #pass

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'las_wave':
           self.wavelength = -1e7 / param.value()
        elif param.name() == 'correc':
            self.correction = param.value()
        elif param.name() == 'axis':
            self.axis = param.value()


    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        self.controller = IK220()
        # TODO for your custom plugin (optional) initialize viewers panel with the future type of data
        #self.data_grabed_signal_temp.emit([DataFromPlugins(name='Mock1',data=[np.array([0]), np.array([0])],
                                                         #  dim='Data0D',labels=['Mock1', 'label2'])])

        info = "Connected"
        initialized = True
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        #  self.controller.your_method_to_terminate_the_communication()  # when writing your own plugin replace this line

    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        ## TODO for your custom plugin

        # synchrone version (blocking function)
        #raise NotImplemented  # when writing your own plugin remove this line
        data_tot = self.controller.get_axis_position()
        self.data_grabed_signal.emit([DataFromPlugins(name='Ruler', data= [np.array([data_tot])],
                                                      dim='Data0D', labels=['dat0', 'data1'])])
        #########################################################

        # asynchrone version (non-blocking function with callback)
        #raise NotImplemented  # when writing your own plugin remove this line
        #self.controller.your_method_to_start_a_grab_snap(self.callback)  # when writing your own plugin replace this line
        #########################################################


    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.data_grabed_signal.emit([DataFromPlugins(name='Mock1', data=data_tot,
                                                      dim='Data0D', labels=['dat0', 'data1'])])

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        ## TODO for your custom plugin
        #raise NotImplemented  # when writing your own plugin remove this line
        #self.controller.your_method_to_stop_acquisition()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Stop']))
        ##############################
        return ''


if __name__ == '__main__':
    main(__file__)

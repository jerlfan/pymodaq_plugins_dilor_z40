"""
Demo Wrapper to illustrate the plugin developpement. This Mock wrapper will emulate communication with an instrument
"""

from time import perf_counter, sleep
import time
import math

from serial.tools import list_ports
ports = [port.name for port in list_ports.comports()]


from telemetrix import telemetrix
class ActuatorWrapper:
    units = 'wavenumber (cm-1)'
    def __init__(self):
        self._com_port = ''
        self._current_value = 0
        self._target_value = None




    def open_communication(self, port):
        """
        fake instrument opening communication.
        Returns
        -------
        bool: True is instrument is opened else False
        """
        self.device=telemetrix.Telemetrix(com_port=port)
        self.motor = self.device.set_pin_mode_stepper(interface=2, pin1=3, pin2=4)


        return True

    def current_position_callback(data):
        print(f'pos {data[2]}\n')
        global status
        status = data[2]

    def target_position_callback(data):
        print(f'target_position_callback returns {data[2]}')

    def distance_to_go_callback(data):
        print(f'distance_to_go_callback returns {data[2]}\n')

    def is_running_callback(data):
        global running
        running = data[1]
        return running

        print(f'is_running_callback returns {data[1]}\n')

    def the_callback(data):
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
        print(f'Motor {data[1]} absolute motion completed at: {date}.')


    def running_callback(data):
        if data[1]:
            print('The motor is running.')
        else:
            print('The motor IS NOT running.')

    def move_at(self, value):
        """
        Send a call to the actuator to move at the given value
        Parameters
        ----------
        value: (float) the target value
        """
        self._target_value = value
        self._init_value = self._current_value
        #0.0031178
        n_steps = round((self._target_value-self._init_value))
        print(f'valeur initiale: {self._init_value}')
        print(f'différence: {self._target_value-self._init_value}')
        #print(f'nombre de pas: {n_steps}')

        self.device.stepper_move(self.motor,n_steps)
        self.device.stepper_run(self.motor,completion_callback=ActuatorWrapper.the_callback)
        #self._start_time = perf_counter()
        self._moving = True
        #self.get_current_position(self.motor,self._current_value)

        self._target_value = value
        self._current_value = value

    def move_rel(self, value):
        """
        Send a call to the actuator to move at the given value
        Parameters
        ----------
        value: (float) the target value
        """
        self._target_value = self._current_value+value
        self._init_value=self._current_value
        # 0.0031178
        n_steps = round(value)
        print(f'valeur initiale: {self._init_value}')
        print(f'différence: {self._target_value - self._init_value}')
        # print(f'nombre de pas: {n_steps}')

        self.device.stepper_move(self.motor, n_steps)
        self.device.stepper_run(self.motor, completion_callback=ActuatorWrapper.the_callback)
        # self._start_time = perf_counter()
        self._moving = True
        # self.get_current_position(self.motor,self._current_value)


        self._current_value = self._target_value

    def max_speed_set(self,value):
        self.device.stepper_set_max_speed(self.motor, value)

    def accel_set(self,value):
        self.device.stepper_set_acceleration(self.motor, value)


    #def stop(self):
     #   self.sendToArduino(f'move,{stop}')

    #def stop(self):
     #   self.device.stepper_stop(self.motor)

    def current_position_callback(data):
        global status
        print(f'current_position_callback returns {data[2]}\n')
        return data[2]
    def get_value(self):
        """
        Get the current actuator value
        Returns
        -------
        float: The current value
        """
        #self.device.stepper_get_current_position(self.motor, ActuatorWrapper.current_position_callback)
        #self._current_value = self.ruler.get_axis_position(1)+5899.42
        #self._current_value=self.device.stepper_get_current_position(self.motor,ActuatorWrapper.current_position_callback)
        return self._current_value

    def close_communication(self):
        self.device.shutdown()
        return f'Motor disconnected:'




class ActuatorWrapperWithTau(ActuatorWrapper):

    units = '°K'

    def __init__(self):
        super().__init__()
        self._espilon = 1e-2
        self._tau = 3  # s
        self._alpha = None
        self._init_value = None
        self._start_time = 0
        self._moving = False

    def open_communication(self, com_port):
        """
        fake instrument opening communication. just checking the COM port exist
        Parameters
        ----------
        com_port: (str) the COM port identifier, eg 'COM1'

        Returns
        -------
        bool: True is instrument is opened else False
        """
        self._com_port = com_port
        if com_port in ports:
            return True
        else:
            return False

    @property
    def epsilon(self):
        return self._espilon

    @epsilon.setter
    def epsilon(self, eps):
        self._espilon = eps


    @property
    def is_moving(self):
        return self._moving

    @property
    def tau(self):
        """
        fetch the characteristic decay time in s
        Returns
        -------
        float: the current characteristic decay time value

        """
        return self._tau

    @tau.setter
    def tau(self, value):
        """
        Set the characteristic decay time value in s
        Parameters
        ----------
        value: (float) a strictly positive characteristic decay time
        """
        if value <= 0:
            raise ValueError(f'A characteristic decay time of {value} is not possible. It should be strictly positive')
        else:
            self._tau = value


    def move_at(self, value):
        """
        Send a call to the actuator to move at the given value
        Parameters
        ----------
        value: (float) the target value
        """
        self._target_value = value
        self._init_value = self._current_value
        self._alpha = math.fabs(math.log(self._espilon / math.fabs(self._init_value - self._target_value)))
        self._start_time = perf_counter()
        self._moving = True

    def stop(self):
        self._moving = False

    def get_value(self):
        """
        Get the current actuator value
        Returns
        -------
        float: The current value
        """
        if self._moving:
            curr_time = perf_counter()
            self._current_value = \
                math.exp(- self._alpha * (curr_time-self._start_time) / self._tau) *\
                (self._init_value - self._target_value) + self._target_value

        return self._current_value






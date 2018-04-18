#!/usr/bin/env python
###########################################################################
#(C) Copyright Pumpkin, Inc. All Rights Reserved.
#
#This file may be distributed under the terms of the License
#Agreement provided with this software.
#
#THIS FILE IS PROVIDED AS IS WITH NO WARRANTY OF ANY KIND,
#INCLUDING THE WARRANTY OF DESIGN, MERCHANTABILITY AND
#FITNESS FOR A PARTICULAR PURPOSE.
###########################################################################
"""
@package PowerSupply.py
Module to handle the control of a generic power supply, providing an \
abstraction layer for the user.
"""

__author__ = 'David Wright (david@asteriaec.com)'
__version__ = '0.1.0' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

from koradserial import KoradSerial
import Tkinter as TK
import sys
import serial

default_port = 'COM2'


# ---------
# Classes

class PowerSupply(object):
    """
    Class to serve as an abstraction layer between the program and the power 
    supply in use. Links a generic set of power supply functionality to the 
    specific functions required to operate the selected power supply.
    
    @attribute model    (string)     The model of the power supply in use
    @attribute port     (string)     The COM port being used by the power supply
    @attribute PS       (object)     The power supply object
    @attribute output   (object)     The output port of KA3005P Power Supply
    """    
    
    def __init__(self, Model):
        """
        Initialise the PowerSupply Object
    
        @param[in] Model     The model of the power supply selected (string)
        """       
        
        # Initialise attributes
        self.model = Model
        self.port = 'NULL'
        
        # check to see if the model requested is selected
        if self.model == 'KA3005P':
            # find the port associated with the KA3005P Power Supply
            self.port = findKoradPort()
            
        else:
            # The requested power supply is not supported
            raise ValueError('The Power Supply model selected is not supported'+
                             'by this Module')
        # end if        
    #end def
    
    
    def __enter__(self):
        """
        Enter a specific usage of the PowerSupply Object. this is called by the
        with statement.
    
        """        
        
        # check to see if a power supply has been detected previously
        if self.port == 'NULL':
            # it has not so attempt to detect one based on the model requested
            if self.model == 'KA3005P':
                # find the port associated with the KA3005P
                self.port = findKoradPort()
                
                # was a port found?
                if self.port != 'NULL':
                    # A port was found so open it
                    self.PS = KoradSerial(self.port)
                    self.output = self.PS.channels[0]
    
                else:
                    # no Power supply was found
                    raise IOError('No Korad Power Supply was detected')
                # end if
            # end if
            
        else:
            # A port has previously been found so open the port
            self.PS = KoradSerial(self.port)
            self.output = self.PS.channels[0]                
        #end if
        
        # return the object for use in with statement
        return self
    # end def
    
    
    def output_on(self):
        """ 
        Turn on the output of the power supply
        """
        if self.model == 'KA3005P':
            self.PS.output.on()
        # end if 
    # end def
    
    
    def output_off(self):
        """ 
        Turn off the output of the power supply
        """        
        if self.model == 'KA3005P':
            self.PS.output.off()
        # end if 
    # end def    
    
    
    def get_output(self):
        """ 
        Get the output state of the power supply.
        
        @return   (string)     the output state: 'on' or 'off'
        """        
        if self.model == 'KA3005P':
            return self.PS.status.output.name
        # end if
    # end def
    
    
    def get_mode(self):
        """ 
        Get the output mode of the power supply.
    
        @return   (string)     the output mode: 'constant_voltage' or 
                                                'constant_current'
        """         
        if self.model == 'KA3005P':
            return self.PS.status.channel1.name
        #endif
    # end def    
    
    
    def get_output_voltage(self):
        """ 
        Get the output voltage of the power supply.
    
        @return   (float)     the output voltage in volts
        """        
        if self.model == 'KA3005P':
            return self.output.output_voltage
        # end if 
    # end def 
    
    
    def get_voltage(self):
        """ 
        Get the output voltage setting of the power supply.
    
        @return   (float)     the output voltage setting in volts
        """         
        if self.model == 'KA3005P':
            return self.output.voltage
        # end if 
    # end def    
    
    
    def set_voltage(self, volts):
        """ 
        Set the output voltage setting of the power supply.
    
        @param[in]   volts     the new output voltage setting in volts (float)
        """        
        if self.model == 'KA3005P':
            self.output.voltage = volts
        # end if 
    # end def      
        
        
    def get_output_current(self):
        """ 
        Get the output current of the power supply.
    
        @return   (float)     the output current in amps
        """        
        if self.model == 'KA3005P':
            return self.output.output_current
        # end if 
    # end def 
    
    
    def get_current(self):
        """ 
        Get the output current setting of the power supply.
    
        @return   (float)     the output current setting in amps
        """        
        if self.model == 'KA3005P':
            return self.output.current
        # end if 
    # end def    
    
    
    def set_current(self, amps):
        """ 
        Set the output current setting of the power supply.
    
        @param[in]   amps     the new output current setting in amps (float)
        """         
        if self.model == 'KA3005P':
            self.output.current = amps
        # end if 
    # end def 
    
    
    def __exit__(self, type, value, traceback):
        """
        Exit the with statement and close all ports associuated with the 
        power supply
        """
        # only close a port if one was found.
        if self.port != 'NULL':
            if self.model == 'KA3005P':
                self.PS.close()
            #end if
        # end if        
    #end def    
# end class


class Power_Supply_GUI:
    """
    Class to operate the GUI for the power supply and the power supply itself.
    
    @attribute frame           (TK Frame)    The frame which contains the GUI 
                                             objects for this class
    @attribute model           (string)      The model of the power supply in use
    @attribute gui             (TK tk)       the root GUI object
    @attribute PS              (PowerSupply) The power supply object in use
    @attribute output_state    (string)      The current output state of the 
                                             power supply : 'on' or 'off'
    @attribute enabled         (bool)        Whether or not the gui is enabled
    @attribute on_button       (TK Button)   The button that turns the output 
                                             on and off
    @attribute voltage_setting (TK Entry)    The box into which desired votlages
                                             are entered
    @attribute current_setting (TK Entry)    The box into which desired currents
                                             are entered
    @attribute voltage_value   (TK Label)    Display of the actual power supply 
                                             voltage
    @attribute current_value   (TK Label)    Display of the actual power supply 
                                             current
    @attribute CV_label        (TK Label)    Indicator for constant voltage state
    @attribute CC_label        (TK Label)    Indicator for constant current state
    @attribute set_button      (TK Button)   Button that sends the new settings 
                                             to the power supply
    """  
    
    def __init__(self, gui_frame, gui, model, slave = False):
        """
        Initialise the PowerSupply GUI Object
        
        @param[in] gui_frame  The frame where all GUI items should be put 
                              (TK Frame)
        @param[in] gui        The root GUI object (TK tk)
        @param[in] model      The model of the power supply selected (string)
        """   
        
        # initialise attributes
        self.frame = gui_frame
        self.model = model
        self.gui = gui
        self.output_state = 'off'
        self.enabled = False
        self.slave = slave
        
        # initialise the powerSupply to be used
        self.PS = PowerSupply(self.model)
        
        # load the GUI elements
        self.load_gui()
    # end def


    def load_gui(self):
        """
        Add all the GUI elements to the GUI
        """
        
        # add a border to the frame
        self.frame.config(borderwidth = 2, relief = 'raised')        
        
        # title
        title = TK.Label(self.frame, text = self.model + " Power Supply",
                         font = "Arial 14 bold")
        title.grid(row = 0, column = 0, columnspan = 4)
        
        # output control button
        self.on_button = TK.Button(self.frame, text = 'Output On', 
                                   state='disabled', command = self.PS_On, 
                                   activebackground = 'green', width = 15,
                                   font = "Arial 10 bold")
        self.on_button.grid(row = 1, column = 0, columnspan = 4)
        
        # title for the settings column
        setpoint = TK.Label(self.frame, text = "Setting:",
                            font = "Arial 10 underline")
        setpoint.grid(row = 2, column = 1)
        
        # title for the vlaues column
        value = TK.Label(self.frame, text = "Current\nValue:",
                         font = "Arial 10 underline")
        value.grid(row = 2, column = 2)
        
        # title for the voltage row
        voltage = TK.Label(self.frame, text = "Voltage (V):")
        voltage.grid(row = 3, column = 0)
        
        # title for the current row
        current = TK.Label(self.frame, text = "Current (A):")
        current.grid(row = 4, column = 0)
        
        # box to enter voltages into
        self.voltage_setting = TK.Entry(self.frame)   
        self.voltage_setting.insert(0, '8.4')
        self.voltage_setting.grid(row = 3, column = 1)
        
        # box to enter currents into
        self.current_setting = TK.Entry(self.frame, text = "2")   
        self.current_setting.insert(0, '2')
        self.current_setting.grid(row = 4, column = 1)
        
        # label to display the current voltage
        self.voltage_value = TK.Label(self.frame, text = "-")
        self.voltage_value.grid(row = 3, column = 2)
        
        # label to display the current current
        self.current_value = TK.Label(self.frame, text = "-")
        self.current_value.grid(row = 4, column = 2)        
        
        # label to denote constant voltage mode
        self.CV_label = TK.Label(self.frame, text = 'C.V.')
        self.CV_label.grid(row = 3, column = 3)
        
        # label to denote constant current mode
        self.CC_label = TK.Label(self.frame, text = 'C.C.', background = 'green')
        self.CC_label.grid(row = 4, column = 3)        
        
        # button to send the settings to the power supply
        self.set_button = TK.Button(self.frame, text = 'Set', 
                                    state='disabled', command = self.set_PS,
                                    activebackground = 'green', width = 15,
                                    font = "Arial 10 bold")
        self.set_button.grid(row = 5, column=0, columnspan = 4, 
                              padx=10, pady=10)
        
        # update the gui from the power supply
        self.update_gui()     
    #end def
    
    
    def PS_On(self):
        """ 
        Turn on the power supply output when commanded by the GUI button
        """
        # attempt to communicate with the power supply
        try:
            with self.PS:
                # If communication is successful turn the output on
                self.PS.output_on()
                
                # reconfigure the button
                self.on_button.config(text = "Output Off", 
                                      command = self.PS_Off)
                # remmeber the new state
                self.output_state = 'on'
            # end with
            
        except:
            # no power supply was found so disable the GUI
            self.disable_gui()
        # end try 
    # end def
    
    
    def PS_Off(self):
        """ 
        Turn off the power supply output when commanded by the GUI button
        """
        # attempt to communicate with the power supply        
        try:
            with self.PS:
                # If communication is successful turn the output off
                self.PS.output_off()
                
                # reconfigure the button
                self.on_button.config(text = "Output On", command = self.PS_On)
                
                # remmeber the new state
                self.output_state = 'off'
            # end with
            
        except:
            # no power supply was found so disable the GUI
            self.disable_gui()
        # end try         
    # end def    
    
    
    def set_PS(self):
        """ 
        Send the settings entered into the GUI to the power supply
        """
        
        # extract the desired values from the gui
        voltage_text = self.voltage_setting.get()
        current_text = self.current_setting.get()
        
        # attempt to convert these values to floats
        try:
            voltage_int = float(voltage_text)
            current_int = float(current_text)
            
            # attempt to communicate with the power supply
            try:
                with self.PS:
                    # communications were successful so update the power supply
                    self.PS.set_voltage(voltage_int)
                    self.PS.set_current(current_int)
                #end with
                
            except:
                # communications failed so disable the gui
                self.disable_gui()
            # end try   
            
        except:
            # string to float conversion failed to reset the settings to 
            # the default
            self.voltage_setting.delete(0, 'end')
            self.voltage_setting.insert(0, '8.4')
            self.current_setting.delete(0, 'end')
            self.current_setting.insert(0, '2')
        #end try
    # end def   
    
    
    def disable_gui(self):
        """
        Disable the GUI elements
        """
        self.enabled = False
        self.on_button.config(state='disabled')
        self.set_button.config(state='disabled')
        self.voltage_setting.config(state='disabled')
        self.current_setting.config(state='disabled')      
    # end def
    
    
    def enable_gui(self):
        """
        Enable the GUI elements
        """
        
        if not self.slave:
            self.on_button.config(state='normal')
            self.set_button.config(state='normal')      
            self.voltage_setting.config(state='normal')
            self.current_setting.config(state='normal')    
        # end if
    # end def    
    
    
    def update_gui(self):
        """
        Update the gui from the power supply. This task becomes preiodic once 
        the GUI is running.
        """
        
        # default values
        voltage = '-'
        current = '-'
        
        # attempt to communicate with the power supply
        try:
            with self.PS:
                # communicatins were successful
                if not self.enabled:
                    # if the gui is not enabled then enable it
                    
                    self.voltage_setting.config(state='normal')
                    self.current_setting.config(state='normal') 
                    
                    self.voltage_setting.delete(0,'end')
                    self.voltage_setting.insert(0,str(self.PS.get_voltage()))
                    self.current_setting.delete(0,'end')
                    self.current_setting.insert(0,str(self.PS.get_current()))
                    
                    self.voltage_setting.config(state='disabled')
                    self.current_setting.config(state='disabled')                      
                    
                    self.enable_gui()
                    
                    self.enabled = True
                #end if
                    
                # read values from the power supply
                voltage = self.PS.get_output_voltage()
                current = self.PS.get_output_current()
                
                # insert these values into the GUI
                self.voltage_value.config(text=str(voltage))
                self.current_value.config(text=str(current))
                
                # check that the output state doesn't match the GUI
                if self.output_state != self.PS.get_output():
                    # there is a missmatch
                    if self.output_state == 'on':
                        # the GUI is erroniously displaying an on state so 
                        # change to off
                        self.on_button.config(text = "Output On", 
                                              command = self.PS_On)
                        self.output_state = 'off'
                    
                    else:
                        # the GUI is erroniously displaying an off state so 
                        # change to on                        
                        self.on_button.config(text = "Output Off", 
                                              command = self.PS_Off)
                        self.output_state = 'on'
                    # end if
                # end if
                
                # determine whether the power supply is running in CV or CC mode
                if self.PS.get_mode() == 'constant_voltage':
                    # it is in CV mode do display that
                    self.CV_label.config(background = 'green')
                    self.CC_label.config(background = self.frame.cget('bg'))
                    
                else:
                    # it is in CC mode do display that
                    self.CV_label.config(background = self.frame.cget('bg'))
                    self.CC_label.config(background = 'green')
                # end if
            #end with
            
        except:
            # communcations could not be esablished to disable the gui
            self.disable_gui()
        # end try  
        
        # schedule the next repetition of this function
        self.gui.after(1000, self.update_gui)
    #end def
    
    def close_GUI(self):
        """
        Function to reset controls on the power supply when the gui exits.
        """
        self.PS.__exit__(None, None, None)
    # end def    
# end class
              
            
#
# ----------------
# Private Functions
            
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
            
    @return    (list of strings)   list of usable com ports
    """
    
    # determine the system that this code is running on and build a list of 
    # all possible ports
    if sys.platform.startswith('win'):
        # windows
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    # end if

    # initialise result list
    result = []
    
    # iterate through all the ports checking for serial comms
    for port in ports:
        # attempt to establist communications
        try:
            s = serial.Serial(port)
            s.close()
            
            # add to the list of useable ports
            result.append(port)
            
        except (OSError, serial.SerialException):
            # was not a useable port
            pass
        # end try
    # end for
    
    return result
# end def

def findKoradPort():
    """ 
    Find the port that the Korad power supply is operating on
    
    @return   (string)    the name of the port that the power supply is using
                          'NULL' if it cannot be found
    """
    
    # initialise return value
    power_supply_port = 'NULL'
    
    # find all available ports
    available_ports = [default_port] + serial_ports()
    
    # iterate through the available ports to see if any is the power supply
    for port in available_ports:
        # try to communicate with each port as if it was the power supply
        try:
            # open the power supply port
            with KoradSerial(port) as com_test:
                # request the model name
                model_name = com_test.model.encode('ascii','ignore')
                
                # if the power supply name is acceptible then store that port 
                # name and exit
                if model_name.startswith('KORAD'):
                    power_supply_port = port
                    break;
                # end if
            # end with
        except:
            # this port is not a Korad power supply
            pass
        # end try
    # end for    
    
    return power_supply_port
# end def

def _test():
    """
    Test code for this module.
    """
    # construct the root frame
    root = TK.Tk()
    root.geometry('800x600')
    
    # construct a frame for the power supply gui
    test_frame = TK.Frame(root)
    test_frame.grid(row = 0, column = 0)
    
    # initialise the power supply gui
    PS_GUI = Power_Supply_GUI(test_frame, root, 'KA3005P')
    
    # start the GUI
    root.mainloop()
# end def

if __name__ == '__main__':
    # if this code is not running as an imported module run test code
    _test()
# end if
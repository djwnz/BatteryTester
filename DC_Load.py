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
@package DC_Load.py
Module to handle the control of a generic DC Load, providing an 
abstraction layer for the user.
"""

__author__ = 'David Wright (david@asteriaec.com)'
__version__ = '0.1.0' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

from pyMaynuo import MaynuoDCLoad
import Tkinter as TK
import sys
import serial
import time

# default values for the gui
gui_defaults = {'constant_current':    ['2.0', 'Amps'],
                'constant_voltage':    ['8.0', 'Volts'],
                'constant_power':      ['2.0', 'Watts'],
                'constant_resistance': ['100', 'Ohms']}

default_port = 'COM16'
default_address = 1

#
# ---------
# Classes

class DCLoad(object):
    """
    Class to serve as an abstraction layer between the program and the DC Load 
    in use. Links a generic set of DC Load functionality to the 
    specific functions required to operate the selected DC Load.
    
    @attribute model    (string)     The model of the DC Load in use
    @attribute port     (string)     The COM port being used by the DC Load
    @attribute addr     (int)        The address of the Load
    @attribute Load     (object)     The DC Load object
    """    
    
    def __init__(self, Model, address = None):
        """
        Initialise the DCLoad Object
    
        @param[in] Model     The model of the DC Load selected (string)
        """       
        
        # Initialise attributes
        self.model = Model
        self.port = 'NULL'
        self.addr = None
        
        # check to see if the model requested is selected
        if self.model == 'M9711':
            # find the port associated with the M97121 Load
            [self.port, self.addr] = findM9711Port(address)
            
        else:
            # The requested load is not supported
            raise ValueError('The DC Load model selected is not supported'+
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
            if self.model == 'M9711':
                # find the port associated with the KA3005P
                [self.port, self.addr] = findM9711Port(self.addr)
                
                # was a port found?
                if self.port != 'NULL':
                    # A port was found so open it
                    self.Load = MaynuoDCLoad(self.port, self.addr)
    
                else:
                    # no Power supply was found
                    raise IOError('No maynou M9711 Supply was detected')
                # end if
            # end if
            
        else:
            # A port has previously been found so open the port
            self.Load = MaynuoDCLoad(self.port, self.addr)             
        #end if
        
        self.Load.__enter__()
        
        # return the object for use in with statement
        return self
    # end def
    
    def re_enter(self):
        self.__enter__()
    # end def
    
    
    def load_on(self):
        """ 
        Turn on the inputs of the Load
        """
        if self.model == 'M9711':
            self.Load.on()
        # end if 
    # end def
    
    
    def load_off(self):
        """ 
        Turn off the inputs of the load
        """        
        if self.model == 'M9711':
            self.Load.off()
        # end if 
    # end def    
    
    
    def get_input(self):
        """ 
        Get the input state of the Load.
        
        @return   (string)     the input state: 'on' or 'off'
        """        
        if self.model == 'M9711':
            return self.Load.getInputStatus()
        # end if
    # end def
    
    
    def get_mode(self):
        """ 
        Get the output mode of the Load.
    
        @return   (string)     the output mode: 'constant_voltage' or 
                                                'constant_current'
        """         
        if self.model == 'M9711':
            with self.Load:
                return self.Load.getMode()
            # end with
        #endif
    # end def    
    
    
    def set_mode(self, mode, value):
        """
        Set the mode of the Load and define the value associated with it
        
        @param:     mode      The mode to set it to (string) one of:
                              constant_current, constant_power, 
                              constant_voltage, constant resistance.
        @param:     value     The value to use for this mode (float).
        """
        if mode == 'constant_current':
            if self.model == 'M9711':
                self.Load.setConstantCurrent(value)
                self.Load.setMode(mode)
            # end if
        #endif
            
        elif mode == 'constant_power':
            if self.model == 'M9711':
                try:
                    self.Load.setConstantPower(value)
                    time.sleep(0.010)
                    self.Load.setMode(mode)
                except ValueError:
                    print "known issue with checksum failure, writing probably still worked"
            # end if
        #endif
            
        elif mode == 'constant_voltage':
            if self.model == 'M9711':
                self.Load.setConstantVoltage(value)
                self.Load.setMode(mode)
            # end if
        #endif
            
        elif mode == 'constant_resistance':
            if self.model == 'M9711':
                self.Load.setConstantResistance(value)
                self.Load.setMode(mode)
            # end if
        #endif
            
        else:
            print mode + ' is an invalid input mode for the ' + self.model
        # end if
    # end def
    
    
    def get_voltage(self):
        """ 
        Get the input voltage of the Load.
    
        @return   (float)     the voltage in volts
        """        
        if self.model == 'M9711':
            return self.Load.getVoltage()
        # end if 
    # end def 
    
    
    def get_constant_voltage(self):
        """ 
        Get the constant voltage setting of the Load.
    
        @return   (float)     the constant voltage setting in volts
        """         
        if self.model == 'M9711':
            return self.Load.getConstantVoltage()
        # end if 
    # end def  
    
    
    def get_current(self):
        """ 
        Get the input current of the Load.
    
        @return   (float)     the current in Amps.
        """        
        if self.model == 'M9711':
            return self.Load.getCurrent()
        # end if 
    # end def 
    
    
    def get_constant_current(self):
        """ 
        Get the constant current setting of the Load.
    
        @return   (float)     the constant current setting in amps.
        """         
        if self.model == 'M9711':
            return self.Load.getConstantCurrent()
        # end if 
    # end def 
    
    
    def get_power(self):
        """ 
        Get the input Power of the Load.
    
        @return   (float)     the Power in Watts.
        """        
        if self.model == 'M9711':
            return (self.Load.getCurrent() * self.Load.getVoltage())
        # end if 
    # end def 
    
    
    def get_constant_power(self):
        """ 
        Get the constant power setting of the Load.
    
        @return   (float)     the constant power setting in Watts.
        """         
        if self.model == 'M9711':
            return self.Load.getConstantPower()
        # end if 
    # end def    
    
    
    def get_resistance(self):
        """ 
        Get the input resistance of the Load.
    
        @return   (float)     the Resistance in Ohms.
        """        
        if self.model == 'M9711':
            return (self.Load.getVoltage() / self.Load.getCurrent())
        # end if 
    # end def 
    
    
    def get_constant_resistance(self):
        """ 
        Get the constant resistnace setting of the Load.
    
        @return   (float)     the constant resistance setting in Ohms.
        """         
        if self.model == 'M9711':
            return self.Load.getConstantResistance()
        # end if 
    # end def   
    
    
    def set_keypad(self, value):
        """
        Truen the keypad of the load on or off.
        
        @param:    value      'on' or 'off' (string).
        """
        if self.model == 'M9711':
            if value == 'off':
                self.Load.setPC2(1)
                
            else:
                self.Load.setPC2(0)
            # end if
        # end if 
    # end def         
    
    
    def __exit__(self, type, value, traceback):
        """
        Exit the with statement and close all ports associuated with the 
        Load
        """
        self.Load.__exit__(type, value, traceback)
        # only close a port if one was found.
        #if self.port != 'NULL':
            #if self.model == 'M9711':
                #try:
                    #self.Load.serial.close()
                    
                #except:
                    ##port is already closed
                    #next
            ##end if
        ## end if        
    #end def    
# end class


class DC_Load_GUI:
    """
    Class to operate the GUI for the Load and the Load itself.
    
    @attribute frame           (TK Frame)     The frame which contains the GUI 
                                              objects for this class.
    @attribute model           (string)       The model of the Load in use.
    @attribute gui             (TK tk)        the root GUI object.
    @attribute Load            (DC_Load)      The DC Load object in use.
    @attribute output_state    (string)       The current input state of the 
                                              Load : 'on' or 'off'.
    @attribute enabled         (bool)         Whether or not the gui is enabled
    @attribute mode            (TK Stringvar) The mode of the DC load.
    @attribute cc_button       (RadioButton)  Selector for constant current mode.
    @attribute cv_button       (RadioButton)  Selector for constant voltage mode.
    @attribute cp_button       (RadioButton)  Selector for constant power mode.
    @attribute cr_button       (RadioButton)  Selector for constant resistance mode.
    @attribute setting         (TK Entry)     Box where Load settings are entered.
    @attribute units           (TK Label)     Units label for the settings box.
    @attribute set_button      (TK Button)    Button that sends the new settings 
                                              to the load.
    @attribute on_button       (TK Button)    The button that turns the input 
                                              on and off.
    @attribute voltage_value   (TK Label)     Display of the actual load
                                              voltage.
    @attribute current_value   (TK Label)     Display of the actual load
                                              current.
    @attribute power_value     (TK Label)     Display of the actual load
                                              power.
    
    """  
    
    def __init__(self, gui_frame, gui, model, slave = False):
        """
        Initialise the PowerSupply Object
        
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
        self.Load = DCLoad(self.model)
        
        with self.Load:
            self.Load.set_keypad('off')
        # end with
        
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
        title = TK.Label(self.frame, text = self.model + " Load", 
                         font = "Arial 14 bold")
        title.grid(row = 0, column = 0, columnspan = 4)
        
        # title for the mode column
        mode_title = TK.Label(self.frame, text = "Mode:", 
                              font = "Arial 10 underline")
        mode_title.grid(row = 1, column = 0)    
        
        # mode variable
        self.mode = TK.StringVar()
        with self.Load:
            self.mode.set(self.Load.get_mode())
        # end with
        
        # Mode radio buttons
        
        radio_frame = TK.Frame(self.frame)
        radio_frame.grid(row = 2, column = 0, rowspan = 4, sticky = 'nsew')
        
        self.cc_button = TK.Radiobutton(radio_frame, text = 'C.C.', 
                                        state='disabled', variable = self.mode, 
                                        value = 'constant_current')
        self.cc_button.grid(row = 0, column = 0, ipady = 2)
        
        self.cv_button = TK.Radiobutton(radio_frame, text = 'C.V.', 
                                        state='disabled', variable = self.mode, 
                                        value = 'constant_voltage')
        self.cv_button.grid(row = 1, column = 0, ipady = 2)
        
        self.cp_button = TK.Radiobutton(radio_frame, text = 'C.P.', 
                                        state='disabled', variable = self.mode, 
                                        value = 'constant_power')
        self.cp_button.grid(row = 2, column = 0, ipady = 2)
        
        self.cr_button = TK.Radiobutton(radio_frame, text = 'C.R.', 
                                        state='disabled', variable = self.mode, 
                                        value = 'constant_resistance')
        self.cr_button.grid(row = 3, column = 0, ipady = 2)        
        
        # title for the settings column
        setpoint = TK.Label(self.frame, text = "Setting:", 
                            font = "Arial 10 underline")
        setpoint.grid(row = 1, column = 1)
        
        with self.Load:
            # box to enter settings into
            self.setting = TK.Entry(self.frame)   
            self.setting.insert(0, gui_defaults[self.Load.get_mode()][0])
            self.setting.grid(row = 2, column = 1)        
            
            # units for the settings box
            self.units = TK.Label(self.frame, font = "Arial 10 italic",
                                  text = gui_defaults[self.Load.get_mode()][1])
            self.units.grid(row = 3, column = 1)
        # end with
        
        # button to send the settings to the power supply
        self.set_button = TK.Button(self.frame, text = 'Set', 
                                        state='disabled', command = self.set_Load,
                                        activebackground = 'green', width = 15,
                                        font = "Arial 10 bold")
        self.set_button.grid(row = 4, column=1, padx=5, pady=5)     
        
        # input control button
        self.on_button = TK.Button(self.frame, text = 'Input On', 
                                       state='disabled', command = self.Load_On, 
                                       activebackground = 'green', width = 15,
                                       font = "Arial 10 bold")
        self.on_button.grid(row = 5, column = 1, padx=5, pady=5)        
        
        
        
        # title for the Readings column
        readings = TK.Label(self.frame, text = "Readings:",
                            font = "Arial 10 underline")
        readings.grid(row = 1, column = 2, ipadx = 5)        
        
        reading_frame = TK.Frame(self.frame)
        reading_frame.grid(row = 2, column = 2, rowspan = 4, sticky = 'nsew')
        
        # label to display the current voltage
        self.voltage_value = TK.Label(reading_frame, text = "-")
        self.voltage_value.grid(row = 0, column = 0, ipadx = 5, ipady = 8, sticky = 'nsew')
        
        # label to display the current current
        self.current_value = TK.Label(reading_frame, text = "-")
        self.current_value.grid(row = 1, column = 0, ipadx = 5, ipady = 8, sticky = 'nsew')   
        
        # label to display the current Power
        self.power_value = TK.Label(reading_frame, text = "-")
        self.power_value.grid(row = 2, column = 0, ipadx = 5, ipady = 8, sticky = 'nsew')          
        
        # label to denote constant voltage mode
        V_label = TK.Label(reading_frame, text = 'V', font = "Arial 10 italic")
        V_label.grid(row = 0, column = 1, ipadx = 5, sticky = 'nsew')
        
        # label to denote constant voltage mode
        C_label = TK.Label(reading_frame, text = 'A', font = "Arial 10 italic")
        C_label.grid(row = 1, column = 1, ipadx = 5, sticky = 'nsew')
        
        # label to denote constant voltage mode
        P_label = TK.Label(reading_frame, text = 'W', font = "Arial 10 italic")
        P_label.grid(row = 2, column = 1, ipadx = 5, sticky = 'nsew')        
        
        # update the gui from the power supply
        self.update_gui()   
    #end def
    
    
    def Load_On(self):
        """ 
        Turn on the Load input when commanded by the GUI button
        """
        
        # attempt to communicate with the Load
        try:
            with self.Load:
                # If communication is successful turn the Input on
                self.Load.load_on()
                
                # reconfigure the button
                self.on_button.config(text = "Input Off", 
                                      command = self.Load_Off)
                # remmeber the new state
                self.output_state = 'on'
            # end with
            
        except:
            # no power supply was found so disable the GUI
            self.disable_gui()
        # end try 
    # end def
    
    
    def Load_Off(self):
        """ 
        Turn off the Load input when commanded by the GUI button
        """
        
        # attempt to communicate with the Load       
        try:
            with self.Load:
                # If communication is successful turn the output off
                self.Load.load_off()
                
                # reconfigure the button
                self.on_button.config(text = "Input On", command = self.Load_On)
                
                # remmeber the new state
                self.output_state = 'off'
            # end with
            
        except:
            # no power supply was found so disable the GUI
            self.disable_gui()
        # end try         
    # end def    
    
    
    def set_Load(self):
        """ 
        Send the settings entered into the GUI to the Load
        """
        
        # extract the desired values from the gui
        new_mode = self.mode.get()
        setting_text = self.setting.get()
        
        # attempt to convert to float
        try:
            setting_int = float(setting_text)
            
            # attempt to communicate with the Load
            try:
                with self.Load:
                    # communications were successful so update the Load
                    self.Load.set_mode(new_mode, setting_int)
                #end with
                
            except:
                # communications failed so disable the gui
                self.disable_gui()
            # end try   
            
        except:
            # string to float conversion failed to reset the settings to 
            # the default
            self.setting.delete(0, 'end')
            self.setting.insert(0, gui_defaults[self.mode.get()][0])
        #end try
    # end def   
    
    
    def disable_gui(self):
        """
        Disable the GUI elements
        """
        self.enabled = False
        self.on_button.config(state='disabled')
        self.set_button.config(state='disabled')
        self.setting.config(state='disabled')
        self.cc_button.config(state='disabled')  
        self.cv_button.config(state='disabled')
        self.cp_button.config(state='disabled')
        self.cr_button.config(state='disabled')
    # end def
    
    
    def enable_gui(self):
        """
        Enable the GUI elements
        """
        if not self.slave:
            self.on_button.config(state='normal')
            self.set_button.config(state='normal')
        # end if
        
        self.setting.config(state='normal')  
        self.cc_button.config(state='normal')  
        self.cv_button.config(state='normal')
        self.cp_button.config(state='normal')
        self.cr_button.config(state='normal')  
    # end def    
    
    
    def update_gui(self):
        """
        Update the gui from the Load. This task becomes preiodic once 
        the GUI is running.
        """
        
        # default values
        voltage = '-'
        current = '-'
        
        # attempt to communicate with the Load
        try:
            with self.Load:
                # communicatins were successful
                if not self.enabled:
                    # if the gui is not enabled then enable it
                    self.enable_gui()
                    
                    # update to match the current load mode
                    load_mode = self.Load.get_mode()
                    self.mode.set(load_mode)
                    self.units.config(text=gui_defaults[load_mode][1])   
                    
                    self.setting.delete(0, 'end')
                    if load_mode == 'constant_current':
                        self.setting.insert(0, '%.3f' % self.Load.get_constant_current())
                        
                    elif load_mode == 'constant_voltage':
                        self.setting.insert(0, '%.3f' % self.Load.get_constant_voltage())   
                        
                    elif load_mode == 'constant_power':
                        self.setting.insert(0, '%.3f' % self.Load.get_constant_power()) 
                        
                    elif load_mode == 'constant_resistance':
                        self.setting.insert(0, '%.3f' % self.Load.get_constant_resistance())   
                    # end if
                    
                    self.enabled = True
                #end if
                    
                # read values from the power supply
                voltage = self.Load.get_voltage()
                current = self.Load.get_current()
                power = self.Load.get_power()
                
                # insert these values into the GUI
                self.voltage_value.config(text= '%.3f' % voltage)
                self.current_value.config(text= '%.3f' % current)
                self.power_value.config(text= '%.3f' % power)
                
                # check that the output state doesn't match the GUI
                if self.output_state != self.Load.get_input():
                    # there is a missmatch
                    if self.output_state == 'on':
                        # the GUI is erroniously displaying an on state so 
                        # change to off
                        self.on_button.config(text = "Input On", 
                                              command = self.Load_On)
                        self.output_state = 'off'
                    
                    else:
                        # the GUI is erroniously displaying an off state so 
                        # change to on                        
                        self.on_button.config(text = "Input Off", 
                                              command = self.Load_Off)
                        self.output_state = 'on'
                    # end if
                # end if
                
                # get the current mode and update the units
                current_mode = self.mode.get()
                self.units.config(text = gui_defaults[current_mode][1])
            
        except:
            # communcations could not be esablished to disable the gui
            self.disable_gui()
        # end try  
        
        # schedule the next repetition of this function
        self.gui.after(1000, self.update_gui)
    #end def
    
    def close_GUI(self):
        """
        Function to reset controls on the load when the gui exits.
        """
        with self.Load:
            self.Load.set_keypad('on')
        # end with
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

def findM9711Port(address = None):
    """ 
    Find the port that the M9711 Load is operating on. This assumes that the
    Load is operating with address 0.
    
    @param    address:    The address of the Load (optional) (int).
    @return   (string)    The name of the port that the Load is using
                          'NULL' if it cannot be found.
    @return   (int)       The address of the Load (int) None if it cannot be 
                          found.
    """
    
    # initialise return value
    Load_port = 'NULL'
    Load_addr = None
    
    
    # find all available ports
    available_ports = [default_port] + serial_ports()
    
    # check if an address was specified
    if address == None:
        addresses = [default_address] + range(0,200)
        
    else:
        addresses = [address] + [default_address] + range(0,200)
    #end if
    
    # iterate through possible addresses
    for addr in range(1,200):
        # iterate through the available ports to see if any is the Load
        for port in available_ports:
            # try to communicate with each port as if it was the power supply
            try:
                # open the power supply port
                with MaynuoDCLoad(port, addr) as com_test:
                    # request the model name
                    model_name = com_test.getModel()  
                    Load_port = port
                    Load_addr = addr
                # end with
            except:
                # this port is not an M9711
                pass
            # end try
            
            if Load_port != 'NULL':
                break
            # end if
        # end for    
        if Load_port != 'NULL':
            break
        # end if        
    # end for
    
    return Load_port, Load_addr
# end def

def _test():
    """
    Test code for this module.
    """
    # construct the root frame
    root = TK.Tk()
    root.geometry('800x600')
    
    # construct a frame for the load gui
    test_frame = TK.Frame(root)
    test_frame.grid(row = 0, column = 0)
    
    # initialise the load gui
    Load_GUI = DC_Load_GUI(test_frame, root, 'M9711')
    
    # start the GUI
    root.mainloop()
# end def

if __name__ == '__main__':
    # if this code is not running as an imported module run test code
    _test()
# end if
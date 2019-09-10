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
@package Multimeter.py
Module to handle the control of a generic multimeter, providing an \
abstraction layer for the user.
"""

__author__ = 'David Wright (david@asteriaec.com)'
__version__ = '0.1.0' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

import Tkinter as TK
import sys
import ivi
import time
import visa

# Constants for Agilent 34410A Digital Multimeter
Agilent34410AIPAddress = "192.168.1.124"
AgilentDCVoltsMode = "dc_volts"
AgilentDCCurrentMode = "dc_current"
AgilentTwoWireReistanceMode = "two_wire_resistance"

# Constants for the Rigol DM3058E Digital Multimeter
RigolDM3058Especifier = '0x09C4::DM3R185250778'
# ---------
# Classes

class Multimeter(object):
    """
    Class to serve as an abstraction layer between the program and the multimeter 
    in use. Links a generic set of multimeter functionality to the 
    specific functions required to operate the selected multimeter.
    
    @attribute model    (string)     The model of the multimeter in use
    @attribute port     (string)     The port used by the multimeter
    @attribute MM       (object)     The multimeter object
    """    

    def __init__(self, Model):
        """
        Initialise the PowerSupply Object
    
        @param[in] Model     The model of the power supply selected (string)
        """       
        
        # Initialise attributes
        self.model = Model
        self.port = None
        self.rm = None
        
        # check to see if the model requested is selected
        if self.model == '34410A':
            # TODO
            pass
        
        elif self.model == 'DM3058E':
            self.rm = visa.ResourceManager()
            pass
        
        else:
            # The requested multimeter is not supported
            raise ValueError('The Multimeter model selected is not supported'+
                             'by this Module')
        # end if        
    #end def
    
    
    def __enter__(self):
        """
        Enter a specific usage of the Multimeter Object. this is called by the
        with statement.
    
        """        
        
        # check to see if a multimeter has been detected previously
        if self.port is None:
            # it has not so attempt to detect one based on the model requested
            if self.model == '34410A':
                # connect to the 34410A
                # find the port associated with the 34410A multimeter
                dmm_ip = "TCPIP0::{}::INSTR".format(Agilent34410AIPAddress)
                try:
                    self.port = ivi.agilent.agilent34410A(dmm_ip)
                except:
                    print("Failed to initialize the Agilent 34410A DMM, Is the ip address {} correct?".format(
                        Agilent34410AIPAddress))
                    raise
                # end try
                
            elif self.model == 'DM3058E':
                dmm_ip = "USB0::0x1AB1::{}::INSTR".format(RigolDM3058Especifier)
                try:
                    self.port = self.rm.open_resource(dmm_ip)
                    self.port.write(":FUNCtion2:VOLTage:DC")
                except:
                    print("Failed to initialize the Rigol 3DM3058E DMM, Is the usd specifier {} correct?".format(
                        RigolDM3058Especifier))
                    raise   
                # end try
            # end if
            
        else:
            # A port has previously been found so communicate through that port
            pass
            # TODO
            
        #end if
        
        # return the object for use in with statement
        return self
    # end def
    
    def open(self):
        """
        Use in place of __enter__ in classes that are compliant with the 'with' 
        statement
        """        
        
        # check to see if a multimeter has been detected previously
        if self.port is None:
            # it has not so attempt to detect one based on the model requested
            if self.model == '34410A':
                # connect to the 34410A
                # find the port associated with the 34410A multimeter
                dmm_ip = "TCPIP0::{}::INSTR".format(Agilent34410AIPAddress)
                try:
                    self.port = ivi.agilent.agilent34410A(dmm_ip)
                except:
                    print("Failed to initialize the Agilent 34410A DMM, Is the ip address {} correct?".format(
                        Agilent34410AIPAddress))
                    raise
                # end try
                
            elif self.model == 'DM3058E':
                dmm_ip = "USB0::0x1AB1::{}::INSTR".format(RigolDM3058Especifier)
                try:
                    self.port = self.rm.open_resource(dmm_ip)
                    self.port.write(":FUNCtion2:VOLTage:DC")
                except:
                    print("Failed to initialize the Rigol 3DM3058E DMM, Is the usd specifier {} correct?".format(
                        RigolDM3058Especifier))
                    raise   
                # end try
            # end if
            
        else:
            # A port has previously been found so communicate through that port
            pass
            # TODO
        #end if
    # end def
    
    
    def get_DC_voltage(self, secondary = False):
        """ 
        Retrieve a voltage measurement from the Multimeter
        
        @return   (float)     The voltage in volts
        """
        if self.model == '34410A':
            try:
                self.port.measurement_function = AgilentDCVoltsMode
                self.port.measurement.initiate()
                return self.port.measurement.fetch(100)
            except:
                print("Failed to get DC Voltage, is the DMM still on and connected?")
                raise
            # end try
            
        elif self.model == 'DM3058E':
            if secondary == False:
                if self.port.query(":FUNCtion?") != 'DCV\n':
                    self.port.write(":FUNCtion:VOLTage:DC")
                # end if
                try:
                    return float(self.port.query(":FUNCtion2:VALUe1?"))
                except:
                    print("Failed to get DC Voltage, is the DMM still on and connected?")
                    raise  
                # end try
            
            else:
                if self.port.query(":FUNCtion2?") != 'DCV':
                    self.port.write(":FUNCtion2:VOLTage:DC")
                # end if
                try:
                    return float(self.port.query(":FUNCtion2:VALUe2?"))
                except:
                    print("Failed to get DC Voltage, is the DMM still on and connected?")
                    raise  
                # end try     
            # end if
        # end if 
        
        return 0
    # end def
    
    
    def get_DC_current(self, secondary = False):
        """ 
        Retrieve a current measurement from the Multimeter
        
        @return   (float)     The current in amps
        """        
        if self.model == '34410A':
            try:
                self.port.measurement_function = AgilentDCCurrentMode
                self.port.measurement.initiate()
                return self.port.measurement.fetch(100)
            except:
                print("Failed to get DC Current, is the DMM still on and connected?")
                raise
            # end try
            
        elif self.model == 'DM3058E':
            if secondary == False:
                if self.port.query(":FUNCtion?") != 'DCI\n':
                    self.port.write(":FUNCtion:CURRent:DC")
                # end if
                try:
                    return float(self.port.query(":FUNCtion2:VALUe1?"))
                except:
                    print("Failed to get DC Current, is the DMM still on and connected?")
                    raise  
                # end try
            
            else:
                if self.port.query(":FUNCtion2?") != 'DCI\n':
                    self.port.write(":FUNCtion2:CURRent:DC")
                # end if
                try:
                    return float(self.port.query(":FUNCtion2:VALUe2?"))
                except:
                    print("Failed to get DC Current, is the DMM still on and connected?")
                    raise  
                # end try     
            # end if
        # end if 
        
        return 0
    # end def    
    
    
    def get_resistance(self, secondary = False):
        """ 
        Retrieve a resistance measurement from the Multimeter
        
        @return   (float)     The resistance measurement in ohms
        """        
        if self.model == '34410A':
            try:
                self.port.measurement_function = AgilentTwoWireReistanceMode
                self.port.measurement.initiate()
                return self.port.measurement.fetch(100)
            except:
                print("Failed to get Resistance, is the DMM still on and connected?")
                raise
                # end try

        elif self.model == 'DM3058E':
            if secondary == False:
                if self.port.query(":FUNCtion?") != '2WR':
                    self.port.write(":FUNCtion:RESistance")
                # end if
                try:
                    return float(self.port.query(":FUNCtion2:VALUe1?"))
                except:
                    print("Failed to get Resistance, is the DMM still on and connected?")
                    raise  
                # end try
            
            else:
                if self.port.query(":FUNCtion?") != '2WR':
                    print("Secondary Resistance is only available when primary is Resistance too")
                    return 0
                
                elif self.port.query(":FUNCtion2?") != '2WR':
                    self.port.write(":FUNCtion2:RESistance")
                # end if
                try:
                    return float(self.port.query(":FUNCtion2:VALUe2?"))
                except:
                    print("Failed to get Resistance, is the DMM still on and connected?")
                    raise  
                # end try     
            # end if            
        # end if 
    
        return 0
    # end def     
    
    
    def __exit__(self, type, value, traceback):
        """
        Exit the with statement and close all ports associuated with the 
        power supply
        """
        # only close a port if one was found.
        if self.port is not None:
            if self.model == '34410A':
                self.port.close()
                self.port = None
                
            elif self.port == 'DM3058E':
                self.port.close()
                self.port = None
            #end if
        # end if        
    #end def    
    
    def close(self):
        """
        use in place of __exit__ in classes that use the 'with' statement
        """
        # only close a port if one was found.
        if self.port is not None:
            if self.model == '34410A':
                self.port.close()
                self.port = None
                
            elif self.port == 'DM3058E':
                self.port.close()
                self.port = None
            #end if
        # end if        
    #end def     
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
    print("Opening DMM")
    #with Multimeter("34410A") as dmm:
        ## Take volts measurement
        #print("Getting DC Volts")
        #print("DC Volts: {}".format(dmm.get_DC_voltage()))
        #print("Sleeping for 20 seconds")
        #time.sleep(20)
        #print("Getting Two-Wire Resistance")
        #print("Two-Wire Resistance: {}".format(dmm.get_resistance()))
        #print("Sleeping for 20 seconds")
        #time.sleep(20)
        #print("Getting DC Current")
        #print("DC Current: {}".format(dmm.get_DC_current()))
        #print("Done testing Agilent 34410A DMM")
        
    with Multimeter("DM3058E") as dmm:
        # Take volts measurement
        print("Getting DC Volts")
        print("DC Volts: {}".format(dmm.get_DC_voltage()))
        print("Sleeping for 2 seconds")
        time.sleep(2)      
        print("Getting Two-Wire Resistance")
        print("Two-Wire Resistance: {}".format(dmm.get_resistance()))
        print("Sleeping for 2 seconds")
        time.sleep(2)
        print("Getting DC Current")
        print("DC Current: {}".format(dmm.get_DC_current()))
        time.sleep(2)   
        print("Getting DC Volts")
        print("DC Volts: {}".format(dmm.get_DC_voltage(secondary = True)))
        print("Sleeping for 2 seconds")
        time.sleep(2)      
        print("Getting Two-Wire Resistance")
        print("Two-Wire Resistance: {}".format(dmm.get_resistance(secondary = True)))
        print("Sleeping for 2 seconds")
        time.sleep(2)
        print("Getting DC Current")
        print("DC Current: {}".format(dmm.get_DC_current(secondary = True)))        
        print("Done testing Agilent 34410A DMM")  

    # construct the root frame
    root = TK.Tk()
    root.geometry('800x600')
    
    # construct a frame for the power supply gui
    test_frame = TK.Frame(root)
    test_frame.grid(row = 0, column = 0)
    
    # initialise the power supply gui
    #PS_GUI = Power_Supply_GUI(test_frame, root, 'KA3005P')
    
    # start the GUI
    root.mainloop()
# end def

if __name__ == '__main__':
    # if this code is not running as an imported module run test code
    _test()
# end if
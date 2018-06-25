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
@package Heater_Tester.py
Module to test BM2 heaters using a power supply and a multimeter.
"""

__author__ = 'David Wright (david@asteriaec.com)'
__version__ = '0.1.0' #Versioning: http://www.python.org/dev/peps/pep-0386/


#
# -------
# Imports

import Multimeter
import Power_Supply
import sys
import csv
import os
import time

EXECUTION_TIME = 5.0 #s
TEST_VOLTAGE = 16.0 #V
CURRENT_LIMIT = 1.0 #A
DATA_RATE = 1 #Hz

output_string = 'heater_test_'

def thermistor_voltage(resistance):
    # find the eqvialent voltage as measured on a SupMCU
    r_voltage = 3.3*resistance/(10000+resistance)
    
    # use the 3dof model to get the temperature
    return -10.064*(r_voltage**3) + 55.396*(r_voltage**2) - 129.03*r_voltage + 131.52  
# end def

with Power_Supply.PowerSupply('KA3005P') as PS:
    with Multimeter.Multimeter('34410A') as MM:
        
        # get the current working directory
        working_dir = os.getcwd()
        
        # find output dir
        output_dir = working_dir + '\\Heater test results\\'
        
        # get file list
        file_list = os.listdir(output_dir)
        csv_list = [filename for filename in file_list if filename.endswith('.csv')]
        
        # find the maximum filename number presetn in the directory
        max_number = 0
        for filename in csv_list:
            try:
                number = int(filename.split('.')[0].split('_')[2])
                if number > max_number:
                    max_number = number
                # end if
                
            except:
                pass
            # end try
        # end for
        
        # add one to the number
        max_number += 1
        
        # create the new filename
        new_filename = output_dir + '\\' + output_string + str(max_number) + '.csv'
        
        # open a csv file
        csv_output = open(new_filename, 'wb')
        output_writer = csv.writer(csv_output, delimiter = '\t')
        
        # write the header row
        output_writer.writerow(['Time (s)', 'Heater Voltage (V)', 'Heater Current (A)', 'Heater Power (W)', 'Thermistor Resistance (Ohm)', 'Thermistor temperature (degC)'])
        
        # record the start time
        start_time = time.time()
        
        #  turn on the output
        PS.set_voltage(TEST_VOLTAGE)
        PS.set_current(CURRENT_LIMIT)
        PS.output_on()
        
        # record measurements for the requisite time
        while ((time.time() - start_time) < EXECUTION_TIME):
            
            # take measurements
            current_time = time.time()-start_time
            voltage = PS.get_output_voltage()
            current = PS.get_output_current()
            power = voltage*current
            resistance = MM.get_resistance()
            temperature = thermistor_voltage(resistance)
            
            # write measurements
            output_writer.writerow([current_time, voltage, current, power, resistance, temperature])
            
            # wait for time to pass to maintain timing
            while (time.time() < (start_time + current_time + 1.0/DATA_RATE)):
                time.sleep(0.001)
            # end while
        # end while
        
        # turn off the output
        PS.output_off()
        
        # close the csv file
        csv_output.close() 
    # end with
# end with

print 'Test Completed!'
            
        
        

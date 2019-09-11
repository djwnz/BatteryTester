import DC_Load
import Power_Supply
import csv
import time
import numpy
import os


# parameters
# input voltage range
max_voltage = 12.8
min_voltage = 5.6
voltage_step = 2

voltage_settings = list(numpy.arange(min_voltage, max_voltage, voltage_step))
voltage_settings.reverse()

max_input_current = 4

# load range
min_power = 0.1
max_power = 15
power_step = 2

power_settings = list(numpy.arange(min_power, max_power, power_step))

output_filename = "Efficiency test.csv"
full_filename = os.getcwd() + '/' + output_filename

timestep = 2

# initialise the equipment
PS = Power_Supply.PowerSupply('KA3005P')
Load = DC_Load.DCLoad('M9711')

# init the CSV
if os.path.isfile(full_filename):
    os.remove(full_filename);
# end if

# set up the csv writing output
with open(full_filename, 'wb') as csv_output:
    output_writer = csv.writer(csv_output, delimiter = '\t')
    
    # write the header row
    output_writer.writerow(['Efficiency'])
    
    # write the second row
    second_row = ['', 'Power'] + power_settings
    output_writer.writerow(second_row)
    
    # write the third row
    output_writer.writerow(['Voltage'])
    
    with PS:
        with Load:
            # set up initial power supply setings
            PS.set_voltage(voltage_settings[0])
            PS.set_current(max_input_current)
            PS.output_on()
            
            # set up initial load settings
            Load.set_mode('constant_power', power_settings[0])
            Load.load_on()
            
            # iterate through the settings to test
            for voltage in voltage_settings:
                
                # set the voltage
                PS.set_voltage(voltage_settings)
                
                data_list = [voltage, '']
                
                for power in power_settings:
                    
                    time.sleep(timestep())
                    
                    output_power = Load.get_power()
                    output_voltage = Load.get_voltage()
                    
                    input_voltage = PS.get_output_voltage()
                    input_current = PS.get_output_current()
                    input_power = input_voltage*input_current
                    
                    if output_voltage < 4.9:
                        print "at " + str(input_voltage) + "V input, output has drooped to " + str(output_voltage) + "V, current drawn is " + str(input_current) + "A"
                    # end if
                    
                    data_list.append((output_power/input_power))
                # end for
                
                output_writer.writerow(data_list)
            # end for
            
            PS.output_off()
            Load.load_off()
        # end with
    # end with
# end with
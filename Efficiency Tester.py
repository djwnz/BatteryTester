import DC_Load
import Power_Supply
import csv
import time
import numpy
import os
import matplotlib.pyplot as plt


# parameters
# input voltage range
max_voltage = 5.2
min_voltage = 5
voltage_step = 0.2

voltage_settings = list(numpy.arange(min_voltage, max_voltage, voltage_step))
voltage_settings.reverse()

voltage_settings = [11.6, 11.4, 10.6, 9.4]
max_input_current = 5

# load range
min_power = 0.1
max_power = 20
power_step = 0.2

dropout_voltage = 4

power_settings = list(numpy.arange(min_power, max_power, power_step))

output_filename = "Efficiency test.csv"
full_filename = os.getcwd() + '/' + output_filename

output_filename2 = "Voltage test.csv"
full_filename2 = os.getcwd() + '/' + output_filename2

timestep = 2

## initialise the equipment
#PS = Power_Supply.PowerSupply('KA3005P')
#Load = DC_Load.DCLoad('M9711')

## init the CSV
#if os.path.isfile(full_filename):
    #os.remove(full_filename);
## end if

## init the CSV
#if os.path.isfile(full_filename2):
    #os.remove(full_filename2);
## end if

#start_time = time.time()

## set up the csv writing output
#with open(full_filename, 'wb') as csv_output:
    #output_writer = csv.writer(csv_output, delimiter = '\t')
    
    ## write the header row
    #output_writer.writerow(['Efficiency'])
    
    ## write the second row
    #second_row = ['', 'Power'] + power_settings
    #output_writer.writerow(second_row)
    
    ## write the third row
    #output_writer.writerow(['Voltage'])    
    
    ## set up the csv writing output
    #with open(full_filename2, 'wb') as csv_output2:
        #output_writer2 = csv.writer(csv_output2, delimiter = '\t')    
    
        ## write the header row
        #output_writer2.writerow(['Voltage'])
        
        ## write the second row
        #second_row = ['', 'Power'] + power_settings
        #output_writer2.writerow(second_row)
        
        ## write the third row
        #output_writer2.writerow(['Voltage'])
    
        #with PS:
            #with Load:
                ## set up initial power supply setings
                #PS.set_voltage(voltage_settings[0])
                #PS.set_current(max_input_current)
                #PS.output_on()
                
                ## set up initial load settings
                #Load.set_mode('constant_power', power_settings[0])
                #Load.load_on()
                
                #voltage_counter = 0
                
                ## iterate through the settings to test
                #for voltage in voltage_settings:
                    
                    ## set the voltage
                    #PS.set_voltage(voltage)
                    
                    #data_list = [voltage, '']
                    #data_list2 = [voltage, '']
                    
                    #for power in power_settings:
                        
                        #Load.set_mode('constant_power', power)
                        
                        #time.sleep(timestep)
                        
                        #read_successful = False
                        #read_attempts = 0
                        
                        #while (not read_successful) and (read_attempts < 100):
                            #try:
                                #output_current = Load.get_current()
                                #time.sleep(0.010)
                                #output_voltage = Load.get_voltage()
                                #output_power = output_current*output_voltage
                                #read_successful = True
                            
                            #except:
                                #Load.re_enter()
                                #read_attempts += 1
                                #print "Load reading at " + str(voltage) + "V input and " + str(power) + "W load was unsuccessful"
                            ## end try
                        ## end while
                        
                        #if read_successful:
                            #input_voltage = PS.get_output_voltage()
                            #input_current = PS.get_output_current()
                            #input_power = input_voltage*input_current
                            
                            #if output_voltage < dropout_voltage:
                                #print "at " + str(input_voltage) + "V input, output has drooped to " + str(output_voltage) + "V, current drawn is " + str(input_current) + "A"
                            ## end if
                        
                            #data_list.append((output_power/input_power))
                            #data_list2.append(output_voltage)
                        
                        #else:
                            #data_list.append(data_list[-1])
                            #data_list.append(data_list2[-1])
                            #print "Load reading at " + str(voltage) + "V input and " + str(power) + "W load was still unsuccessful"
                        ## end try
                    ## end for
                    
                    #voltage_counter += 1
                    #complete_percentage = int(100*voltage_counter/len(voltage_settings))
                    #total_time_estimate = (time.time() - start_time)*100/complete_percentage
                    #time_to_go = int((total_time_estimate - (time.time() - start_time))/60)
                    
                    #print "Test is " + str(complete_percentage) + "% complete, estimated completion in " + str(time_to_go) + " minutes"
                    
                    #output_writer.writerow(data_list)
                    #output_writer2.writerow(data_list2)
                ## end for
                
                #PS.output_off()
                #try:
                    #Load.load_off()
                    
                #except:
                    #print "Failed to turn load off"
                ## end try
                    
            ## end with
        ## end with
    ## end with
## end with

# plot

with open(full_filename, 'r') as csv_input:
    readCSV = csv.reader(csv_input, delimiter=',')
    
    power = []
    voltage = []
    efficiency = []
    
    row_count = 0
    for row in readCSV:
        if row_count == 1:
            power = [float(i) for i in row[2:]]
            
        elif row_count >= 3:
            voltage.append(float(row[0]))
            try:
                efficiency.append([100*float(i) for i in row[2:]])
            except:
                efficiency.append([0 for i in row[2:]])
            # end try
        # end if
        row_count += 1
    # end for
    
    x = numpy.asarray(power, dtype=numpy.float32)
    y = numpy.asarray(voltage, dtype=numpy.float32)
    Z = numpy.asarray(efficiency, dtype=numpy.float32)
    
    X,Y = numpy.meshgrid(x,y)
    
    levels = [0, 1, 20, 40, 60, 70, 80, 85, 90, 95, 100]
    plt.figure()
    mycmap = plt.get_cmap('gnuplot2')
    cp = plt.contourf(X, Y, Z, levels, cmap=mycmap)
    plt.colorbar(cp)
    plt.title('PTH08T221WAZ % Efficiency at 5V')
    plt.xlabel('Applied Load (W)')
    plt.ylabel('Supply Voltage (V)')
    plt.show()    
# end with

with open(full_filename2, 'r') as csv_input:
    readCSV = csv.reader(csv_input, delimiter=',')
    
    power = []
    voltage = []
    efficiency = []
    
    row_count = 0
    for row in readCSV:
        if row_count == 1:
            power = [float(i) for i in row[2:]]
            
        elif row_count >= 3:
            voltage.append(float(row[0]))
            try:
                efficiency.append([float(i) for i in row[2:]])
            except:
                efficiency.append([0 for i in row[2:]])
            # end try
        # end if
        row_count += 1
    # end for
    
    x = numpy.asarray(power, dtype=numpy.float32)
    y = numpy.asarray(voltage, dtype=numpy.float32)
    Z = numpy.asarray(efficiency, dtype=numpy.float32)
    
    X,Y = numpy.meshgrid(x,y)
    
    levels = [0, 4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.95, 5.0, 5.05, 5.1]
    plt.figure()
    mycmap = plt.get_cmap('gnuplot2')
    cp = plt.contourf(X, Y, Z, levels, cmap=mycmap)
    plt.colorbar(cp)
    plt.title('PTH08T221WAZ Output Voltage at 5V')
    plt.xlabel('Applied Load (W)')
    plt.ylabel('Supply Voltage (V)')
    plt.show()    
# end with
            
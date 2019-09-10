import Multimeter
import time
import csv
import os
import shutil


filename = "Multimeter_log.csv"
logging_period = 0.1
logging_duration = 10

full_filename = os.getcwd() + '/' + filename

# delete the old file if it exists
if os.path.isfile(full_filename):
    try:
        os.remove(full_filename)
    except:
        print 'Could not delete ' + filename
        raise
    #end try
# end if

# set up the csv writing output
csv_output = open(full_filename, 'wb')
output_writer = csv.writer(csv_output, delimiter = '\t')

# write the header row
output_writer.writerow(['Time (s)' , 'Current'])

# start the timer
start_time = time.time()

# open the multimeter
with Multimeter.Multimeter("DM3058E") as dmm:
    # constrain the logging to the time requested
    while (time.time() - start_time < logging_duration):
        
        # read the current
        current = dmm.get_DC_current()
        
        # capture the time stamp (after current incase current reading takes variable time)
        loop_time = time.time()
        
        output_writer.writerow([(loop_time-start_time), current])
        
        # waste extra time
        while (time.time() - loop_time) < logging_period:
            time.sleep(0.001)
        # end while
    # end while
# end with

csv_output.close()
    
    
#!/usr/bin/env python

"""
This is the Python script part of my TempMonitoring project (github.com/drew-loukusa/TempMonitoring)
which pairs with an Arduino to monitor the temperature of a room.

This script sends startup parameters to and recieves data from the Arduino.
This script has a number of command line flags which can be used to modify it's behavior, 
run the script with the -h flag to see all of the available flags.
"""
import os
import time
import serial
import datetime 
import argparse 

__author__      = "Drew Loukusa"
__copyright__   = "Copyright 2019, Drew Loukusa"
__license__     = "GNU General Public License v3.0"
__status__      = "Prototype"

# DEFAULTS:
#==============================================================================#
#The following line is for serial over GPIO:
PORT = "COM5"
BAUDRATE = 9600 
TIMEOUT = 300 # Seconds
UPDATE_FREQUENCY = 30 # Seconds
FILE_NAME = None
TIME_LIMIT = "Not Set"

# ARGS:
#==============================================================================#
p = argparse.ArgumentParser()
add = p.add_argument

add('-p',   dest    = 'port', 
            default = PORT, 
            help    = "Which port the program shoud listen on")

add('-b',   dest    = 'baudrate',
            default = BAUDRATE, 
            help    = "Baud rate such as 9600 or 115200 etc")

add('-t',   dest    = 'timeout', 
            default = TIMEOUT,
            help    = "(Seconds) Set a read timeout value. Must be set to a value greater\
                        than the update frequency")

add('-uf',  dest    = 'update_freq', 
            default = UPDATE_FREQUENCY,
            help    = "(Seconds) Set how often the data is updated. Interval should not be\
                        less than 3 seconds since values from the sensor can be\
                        up to 2 seconds old.")

add('-f',   dest    = 'file_name', 
            default = FILE_NAME,
            help    = "Save output to a file named FILE_NAME")


add('-tl',  dest    = 'time_limit', 
            default = TIME_LIMIT,
            help    = "(Seconds) Set how long the script should run")


add('-sl',  dest    = 'single_line', 
            action  = 'store_true',
            help    = "Instead of writing each update as it's own line (logging style) \
                        display each update on the same line, overwriting the last")

add('--pretty', dest    = 'pretty', 
                action  = 'store_true',
                help    = "Hides the startup parameters, except for time_limit and update frequency\
                            set and also has a pretty header and other stuff. AND COLORS")

args = p.parse_args()

# Main:
#==============================================================================#
def monitor_temperature(   
            port=PORT, 
            baudrate=BAUDRATE, 
            timeout=TIMEOUT,             
            update_freq=UPDATE_FREQUENCY, 
            file_name=FILE_NAME,
            time_limit=TIME_LIMIT,
            single_line=False,
            pretty_mode=False,
        ):
    
    # Clear the screen:
    from sys import platform
    if platform == "linux" or platform == "linux2":
        os.system('clear')
    elif platform == "win32":
        os.system('cls')


    # Convert values as necessary:
    timeout     = float(timeout)    
    update_freq = float(update_freq)
    if time_limit != "Not Set":
        time_limit = float(time_limit)

    # Quit if timeout is less than the update freq:
    #----------------------------------------------------------------------------#
    if timeout <= update_freq: 
        print("ERROR: Timeout was set to a value less than the update frequency")
        quit()

    # Open the port:
    #----------------------------------------------------------------------------#
    try:
        ser = serial.Serial(port=port, 
                            baudrate=baudrate, 
                            timeout=timeout, 
                            write_timeout=5)

    except serial.serialutil.SerialException as e:
        print(e)
        quit()


    def get_data():
        return ser.readline().decode("utf-8").rstrip('\n')


    # Transmit the update frequency to the Arduino:       
    #----------------------------------------------------------------------------#    
   
    time.sleep(2) # Wait 2 seconds for the Arduino to setup.

    # I haven't figured out why yet, but the program freezes if you don't wait 
    # for the Arduino to get started. I think the write() call gets stuck because 
    # the port hasn't been opened yet by the Arduino? I tried setting write_timeout
    # for the Serial object but that didn't seem to help.

    # In any case, this works. I'll have to look into this more.

    # Send the update frequency to the Arduino:
    data = str(update_freq)+"$"
    ser.write(data.encode('utf-8'))       

    # Setup stream object:
    stream = None
    if file_name: stream = Stream(fname=file_name, mode='f')
    else:         stream = Stream(mode='p')

    # Emit Title, Parameters and Column Labels: 
    #----------------------------------------------------------------------------#
    #┌ ┐ └ ┘
    header = [
        "AM2302 Humidity - Temperature Sensor",
        "DIV"+"-"*81,
        "Port: {}\t\tBaudrate: {}\t\t\tUpdate Freq (Sec): {}"
                                    .format(port, baudrate,update_freq),
        "Timeout (Sec): {}\tTime Limit (Sec): {}"
                                    .format(timeout, time_limit),
        "DIV"+"-"*81,
        "Time\t\t\tRH\t \tTemp (F)\tHeat Index (F)",
    ]

    if pretty_mode:
         header = [
            "{:^76s}".format("AM2302 Humidity - Temperature Sensor"),
            "DIV"+"-"*78,
            "Port: {}\t\tBaudrate: {}\t\tUpdate Freq (Sec): {}"
                                        .format(port, baudrate,update_freq),
            "Timeout (Sec): {}\tTime Limit (Sec): {}"
                                        .format(timeout, time_limit),
            "DIV"+"-"*78,
            "Time\t\t\tRH\t \tTemp (F)\tHeat Index (F)",
        ]

    if pretty_mode: stream.write("┌"+"-"*78+"┐")

    for line in header: 
        
        if pretty_mode: 
            if line[0:3] == "DIV":
                line = "+" + line[3:] + "+"
            else: 
                line = "| " + line + "{:>80}".format("|")

        stream.write(line)

    if pretty_mode: stream.write("+"+"-"*78+"+")

    # Wait for data on the serial port, then print it out as it's recieved:
    #----------------------------------------------------------------------------#
    loop = True
    time_ran = 0
    
    # This loop does "stuff" and then waits 1 second before doing it again.
    # It uses modulo arithmatic to check if it's time to get and emit data.
    # This is so that the script can check how long it's been running and quit on time.
    
    cur_data = ""
    while loop:
        # If a time limit was set, check if it's time to quit:
        if time_limit != "Not Set" and time_ran >= time_limit:
            loop = False
            continue


        # Check if we should get and emit data:
        elif time_ran % update_freq == 0:
            try:          
                cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")        
                cur_line = get_data()            

                # Occasionally, the script will read before the data is sent
                # by the Arduino. If this happens then we just wait a tiny bit,
                # then read again:
                if cur_line == "":
                    time.sleep(0.05)
                    cur_line = get_data()
                    time_ran += 0.05

                # if single_line:                   
                #     print("\033[%d;%dH" % (7, 0))
                cur_data = cur_time + "\t" + cur_line
                if not single_line: 
                    stream.write(cur_time + "\t" + cur_line)
                             
            except KeyboardInterrupt:            
                loop = False   
                continue         
            except:
                print('Data could not be read') 

        if single_line:
            print("\033[%d;%dH" % (4, 0))
            stream.write("Timeout (Sec): {}\tTime Limit (Sec): {}\t\tTime Ran (Sec): {}\n"
                        .format(timeout, time_limit, time_ran))
            stream.write("-"*81+"\n")
            stream.write("Time\t\t\tRH\t \tTemp (F)\tHeat Index (F)\n")      
            stream.write(cur_data)  

        time.sleep(1)                  
        time_ran += 1 

class Stream:
    """ Allows an object to be created that will either send output to standard out or to a file

        If a file name is given 'fname' and the mode is set to 'f', then the when write() is called
        the object will write the data out to a file.

        If the file mode is specified, a file object will be created on initilization of the Stream
        object. When the Stream object is deleted, the file object will be closed by the __del__ method
        of the class.
    """ 

    def __init__(self, fname=None, mode='p'):
        ''' p = print mode
            f = file mode '''
        self.mode = mode    
        self.file = None 

        if self.mode not in ['p', 'f']: 
            raise Exception("Mode must be 'p' (print mode) or 'f' (file mode) ")

        if self.mode == 'f':            
            self.file = open(fname,'w+')

    def __del__(self):
        if self.mode == 'f':
            self.file.close()

    def write(self, *strings):
        # Build string to be emitted:
        outtext = ""
        for string in strings:
            outtext += string 

        if self.mode == 'p':
            print(outtext.rstrip('\n'))
        elif self.mode == 'f':
            self.file.write(outtext)
        elif self.mode == 'pf':
            self.file.write(outtext)
            print(outtext.rstrip('\n'))

    

if __name__ == "__main__":
    monitor_temperature(
            args.port, 
            args.baudrate,
            args.timeout, 
            args.update_freq, 
            args.file_name,
            args.time_limit,
            args.single_line,
            args.pretty,
        )
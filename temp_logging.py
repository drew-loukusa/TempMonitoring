import time
import serial
import datetime 
import argparse 

#TODO:
#==============================================================================#

# The next thing to add:

# Finish the -o flag for saving the data to a file
        # > I think still having the header info on the command line while 
        #   it outputs to a file would be good. With a note saying as such
        #   and a blinking ellipse to show that it's running 
        #   and how much time is left if the -tl flag was used
# Add a flag which controls how long the script will run. -tl 
# 



# I should change it so that I have the python script send the data update frequency it 
# expects to the Arduino.

# The Arduino would have to wait for an initial message, then start sending data.

# That would actually be the way to do it. 

# You could have a number of options that you could set here in the script,
# or even better, with command line flags, that then get sent to the Arduino.

# You could have it change: what data gets recorded, format, etc etc. 

# DEFAULTS:
#==============================================================================#
#The following line is for serial over GPIO:
PORT = "COM5"
BAUDRATE = 9600 
TIMEOUT = 300 # Seconds
UPDATE_FREQUENCY = 30 # Seconds
FILE_NAME = None

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
            help    = "Set a read timeout value. Must be set to a value greater\
                        than the update frequency")

add('-uf',  dest    = 'update_freq', 
            default = UPDATE_FREQUENCY,
            help    = "Set how often the data is updated. Interval should not be\
                        less than 3 seconds since values from the sensor can be\
                        up to 2 seconds old.")

add('-f',   dest    = 'file_name', 
            default = FILE_NAME,
            help    = "Save output to a file named FILE_NAME")

args = p.parse_args()

# Main:
#==============================================================================#
def main(   
            port=PORT, 
            baudrate=BAUDRATE, 
            timeout=TIMEOUT,             
            update_freq=UPDATE_FREQUENCY, 
            file_name=FILE_NAME
        ):
    
    timeout     = float(timeout)
    update_freq = float(update_freq)

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


    # Transmit the update frequency to the Arduino:       
    #----------------------------------------------------------------------------#    
   
    time.sleep(2) # Wait 2 seconds for the Arduino to setup.

    # I haven't figured out why yet, but the program freezes if you don't wait 
    # for the Arduino to get started. I think the write() call gets stuck because 
    # the port hasn't been opened yet by the Arduino? I tried setting write_timeout
    # for the Serial object but that didn't seem to help.

    # In any case, this works. I'll have to look into this more.

    data = str(update_freq)+"$"
    ser.write(data.encode('utf-8'))       

    # Setup stream object:
    stream = None
    if file_name: stream = Stream(fname=file_name, mode='f')
    else:         stream = Stream(mode='p')

    # Emit Title, Parameters and Column Labels: 
    #----------------------------------------------------------------------------#
    stream.write("AM2302 Humidity - Temperature Sensor")
    stream.write("Port: {}\tBaudrate: {}\t\tUpdate Freq (Sec): {}\tTimeout (Sec):{}"
                                .format(port, baudrate,update_freq, timeout))
    stream.write("-"*81)
    stream.write("Time\t\t\tRH\t \tTemp (F)\tHeat Index (F)")      

    # Wait for data on the serial port, then print it out as it's recieved:
    #----------------------------------------------------------------------------#
    loop = True
    while loop:
        try:          
            cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")        
            cur_line = get_data(ser)            

            # Occasionally, the script will read before the data is sent
            # by the Arduino. If this happens then we just wait a tiny bit,
            # then read again:
            if cur_line == "":
                time.sleep(0.05)
                cur_line = get_data(ser)

            stream.write(cur_time + "\t" + cur_line)  

            # The Arduino is set to send data every update_freq seconds, 
            # so wait that long between reading data:
            time.sleep(update_freq)                        
        except KeyboardInterrupt:            
            loop = False
            stream.close()
        except:
            print('Data could not be read') 

def get_data(ser):
    return ser.readline().decode("utf-8").rstrip('\n')

class Stream:
    def __init__(self, fname=None, mode='p'):
        ''' p = print mode
            f = file mode '''
        self.mode = mode    
        self.file = None 

        if self.mode not in ['p', 'f']: 
            raise Exception("Mode must be 'p' (print mode) or 'f' (file mode) ")

        if self.mode == 'f':            
            self.file = open(fname,'w+')


    def write(self, *strings):
        # Build string to be emitted:
        outtext = ""
        for string in strings:
            outtext += string 

        if self.mode == 'p':
            print(outtext)
        if self.mode == 'f':
            self.file.write(outtext)

    def close(self):
        self.file.close()

if __name__ == "__main__":
    main(args.port, args.baudrate, args.timeout, args.update_freq, args.file_name)
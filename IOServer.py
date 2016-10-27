### TODO: ADD

'''
Implementation of a server with a background thread updating the values of the
server as it is running. The server continously reads from a supplied input
file and continously writes to a supplied output file.

The program can be run with the options -I (--inputfile)
where the user supplies a inputfile with data and sequential addressing.
The supplied input file must be a csv file where the data is orderd in the
following way:
Address, Discrete Input, Coils, Holding Registers, Input Registers
If no input file is supplied dummy data is created.

The outputfile created by the program is a csv file and contains data orderd in
the aformentionend way. If the -O (--outputfile) option is not used a file
called "OutputExampleFile.csv" will be created in the same directory as the
program is run from.
'''
#---------------------------------------------------------------------------#
# import the modbus libraries we need
#---------------------------------------------------------------------------#
from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

#---------------------------------------------------------------------------#
# import the twisted libraries we need
#---------------------------------------------------------------------------#
from twisted.internet.task import LoopingCall

#---------------------------------------------------------------------------#
# configure the service logging
#---------------------------------------------------------------------------#
import logging
logging.basicConfig()
log = logging.getLogger("pymodbus")
#log = logging.getLogger()
#log.setLevel(logging.DEBUG)
#---------------------------------------------------------------------------#
# Import other services
#---------------------------------------------------------------------------#
from optparse import OptionParser


import sys
import csv

#---------------------------------------------------------------------------#
# initialize the server information
#---------------------------------------------------------------------------#
identity = ModbusDeviceIdentification()
identity.VendorName  = 'pymodbus'
identity.ProductCode = 'PM'
identity.VendorUrl   = 'http://github.com/bashwork/pymodbus/'
identity.ProductName = 'pymodbus Server'
identity.ModelName   = 'pymodbus Server'
identity.MajorMinorRevision = '1.0'


#---------------------------------------------------------------------------#
# initialize your data store
#---------------------------------------------------------------------------#
def initialize_datablock():
    '''
        Creates and initializes a dummy datablock
    '''
    return ModbusSlaveContext(
        di = ModbusSequentialDataBlock(0, [17]*52),
        co = ModbusSequentialDataBlock(0, [17]*52),
        hr = ModbusSequentialDataBlock(0, [17]*52),
        ir = ModbusSequentialDataBlock(0, [17]*52))

def read_filedata(filename):
    '''
        Reads a supplied CSV file of format:
        Address, Discrete Input, Coils, Holding Registers, Input Registers
        And returns a ModbusSlaveContext for use by a modbus server
    '''
#   Create empty dictionaries used for the input from CSV file
    di = {}
    co = {}
    hr = {}
    ir = {}
    with open(filename, newline='') as csvfile:
        data = csv.reader(csvfile,delimiter=',')
        log.debug("Reading Inputfile")
        for row in data:
            # Read data into dictionaries, row[0] is address and rest is
            # di = Discrete input, ci = Coils, hr = Holding Registers
            # ir = Input Registrs
            # Addresses should be 1 or higher
            di[int(row[0])] = bool(row[1] in ['True','TRUE'])
            co[int(row[0])] = bool(row[2] in ['True','TRUE'])
            hr[int(row[0])] = int(row[3])
            ir[int(row[0])] = int(row[4])

    log.debug("Done!")
    return ModbusSlaveContext(
        di = ModbusSparseDataBlock(di),
        co = ModbusSparseDataBlock(co),
        hr = ModbusSparseDataBlock(hr),
        ir = ModbusSparseDataBlock(ir))

def updating_writer(a):
    ''' A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.
    :param arguments: The input arguments to the call
    Input arguments require a filename and ModbusSlaveContext
    '''
    filename = a[0]
    context = a[1]
    data = read_filedata(filename)
    log.debug("Updating context")
    i = 0
    for i in range(0,51):
        context[0].setValues(1,i,data.getValues(1,i))
        context[0].setValues(2,i,data.getValues(2,i))
        context[0].setValues(3,i,data.getValues(3,i))
        context[0].setValues(4,i,data.getValues(4,i))
        #log.debug("New values: "+ str(data.getValues(2,i)) + str(data.getValues(1,i))
        # + str(data.getValues(3,i)) + str(data.getValues(4,i)))
    log.debug("Done updating context!")

def write_filedata(a):#filename,a):
    '''
        Write the data of from a context to a CSV file.
        This function requires that there are no gaps in
        addressing. That is all addresses must be sequential
        for this function to be able to fully write the contents
        of the context.
    '''
    filename = a[0]
    data = a[1]
    data = data[0]
    log.debug("Writing to file")
    with open(filename,'w',newline='') as csvfile:
        w = csv.writer(csvfile,delimiter=',')
        i = 0
        #print("After: ")
        while(data.validate(1,i) == True):
            # Get values, (function code, Address, Count=1)
            # FC 4 = Read Input Register
            # FC 3 = Read holding register
            # FC 2 = Read Discrete Input (Boolean values)
            # FC 1 = Read Coil (Boolean values)
            line = [i+1,data.getValues(2,i)[0],data.getValues(1,i)[0],data.getValues(3,i)[0],
            data.getValues(4,i)[0]]
            #print(line)
            w.writerow(line)
            i = i+1
    log.debug("Filewrite done!")



#---------------------------------------------------------------------------#
# initialize our program settings
#---------------------------------------------------------------------------#
def get_options():
    ''' A helper method to parse the command line options

    :returns: The options manager
    '''
    parser = OptionParser()

    parser.add_option("-D", "--debug",
        help="Enable debug tracing",
        action="store_true", dest="debug", default=False)

    parser.add_option("-I","--inputfile",
        help="Name of input file to initialize values",
        dest="input_filename", default="None")

    parser.add_option("-O","--outputfile",
        help="Name of outputfile for writing values",
        dest="output_filename", default="OutputExampleFile.csv")

    (opt, arg) = parser.parse_args()
    return opt

#---------------------------------------------------------------------------#
# run the server you want
#---------------------------------------------------------------------------#
def main():
    option = get_options()

    if option.debug:
        try:
            log.setLevel(logging.DEBUG)
            logging.basicConfig()
        except Exception(e):
    	    print("Logging is not supported on this system")


    InFilename = option.input_filename #sys.argv[1]
    OutFilename = option.output_filename #sys.argv[2]

    if InFilename in {"None"}:
        store = initialize_datablock()
    else:
        store = read_filedata(InFilename)

    context = ModbusServerContext(slaves=store,single=True)

    time = 5 # 5 seconds delay
    loopOut = LoopingCall(f=write_filedata,a=(OutFilename,context))
    loopOut.start(time, now=False)
    if InFilename in {"None"}:
        pass
    else:
        loopIn = LoopingCall(f=updating_writer,a=(InFilename,context,))
        loopIn.start(time+0.1, now=False) # initially delay by time

    StartTcpServer(context, identity=identity, address=("localhost", 5020))

if __name__ == "__main__":
    main()

'''
Pymodbus Server With Updating Thread
--------------------------------------------------------------------------
This is an example of having a background thread updating the
context while the server is operating. This can also be done with
a python thread::
    from threading import Thread
    thread = Thread(target=updating_writer, args=(context,))
    thread.start()
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
log = logging.getLogger()
log.setLevel(logging.DEBUG)

import sys
import csv
#---------------------------------------------------------------------------#
# define your callback process
#---------------------------------------------------------------------------#
def updating_writer(a):
    ''' A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.
    :param arguments: The input arguments to the call
    '''
    log.debug("updating the context")
    context  = a[0]
    register = 3
    slave_id = 0x00
    address  = 1
    values   = context[slave_id].getValues(register, address, count=1)
    values   = [v + 1 for v in values]
    log.debug("new values: " + str(values))
    context[slave_id].setValues(register, address, values)

#---------------------------------------------------------------------------#
# initialize your data store
#---------------------------------------------------------------------------#
# store = ModbusSlaveContext(
#     di = ModbusSequentialDataBlock(0, [17]*100),
#     co = ModbusSequentialDataBlock(0, [17]*100),
#     hr = ModbusSequentialDataBlock(0, [17]*100),
#     ir = ModbusSequentialDataBlock(0, [17]*100))
# context = ModbusServerContext(slaves=store, single=True)

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

def read_filedata(filename):
#   Create empty dictionaries used for the input from CSV file
    di = {}
    co = {}
    hr = {}
    ir = {}
    with open(filename, newline='') as csvfile:
        data = csv.reader(csvfile,delimiter=',')
        log.debug("Reading Inputfile")
        #print("Before: ")
        for row in data:
            # Read data into dictionaries, row[0] is address and rest is
            # di = Discrete input, ci = Coils, hr = Holding Registers
            # ir = Input Registrs
            # Addresses should be 1 or higher
#            print([row[0],row[1],row[2],row[3],row[4]])
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
    '''
    filename = a[0]
    context = a[1]
    #print("I'm in!")
    data = read_filedata(filename)
    log.debug("Updating context")
    #print("Updating the context!")
    i = 0
    for i in range(0,51):
        context[0].setValues(1,i,data.getValues(1,i))
        context[0].setValues(2,i,data.getValues(2,i))
        context[0].setValues(3,i,data.getValues(3,i))
        context[0].setValues(4,i,data.getValues(4,i))
        #print("New values: "+ str(data.getValues(2,i)) + str(data.getValues(1,i))
        # + str(data.getValues(3,i)) + str(data.getValues(4,i)))
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
# run the server you want
#---------------------------------------------------------------------------#
InFilename = sys.argv[1]
OutFilename = sys.argv[2]

store = read_filedata(InFilename)
context = ModbusServerContext(slaves=store,single=True)

time = 5 # 5 seconds delay
loopOut = LoopingCall(f=write_filedata,a=(OutFilename,context))
loopOut.start(time, now=False)
loopIn = LoopingCall(f=updating_writer,a=(InFilename,context,))
loopIn.start(time+0.1, now=False) # initially delay by time
StartTcpServer(context, identity=identity, address=("localhost", 5020))

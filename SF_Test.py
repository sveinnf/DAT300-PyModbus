
# Import necessary functions
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import csv
#--------------------------------------------------------------------------#
# Datablock Builders
#--------------------------------------------------------------------------#
# def build_sequential():
#     '''
#     This builds a quick mock sequential datastore with 100 values for each
#     discrete, coils, holding, and input bits/registers.
#     '''
#     data = {
#         'di' : seqblock(0, [bool(x) for x in range(1, 100)]),
#         'ci' : seqblock(0, [bool(not x) for x in range(1, 100)]),
#         'hr' : seqblock(0, [int(x) for x in range(1, 100)]),
#         'ir' : seqblock(0, [int(2*x) for x in range(1, 100)]),
#     }
#     return data

# def build_sparse():
#     '''
#     This builds a quick mock sparse datastore with 100 values for each
#     discrete, coils, holding, and input bits/registers.
#     '''
#     data = {
#         'di' : sparblock([bool(x) for x in range(1, 100)]),
#         'ci' : sparblock([bool(not x) for x in range(1, 100)]),
#         'hr' : sparblock([int(x) for x in range(1, 100)]),
#         'ir' : sparblock([int(2*x) for x in range(1, 100)]),
#     }
#     return data

def main():

#    data = open("TestData.txt","r")
#    f = data.readlines()
#   Create empty dictionaries used for the input from CSV files
    di = {}
    ci = {}
    hr = {}
    ir = {}
    with open("CSVtest2.csv", newline='') as csvfile:
        data = csv.reader(csvfile,delimiter=',')
        print("Before: ")
        for row in data:
            # Read data into dictionaries, row[0] is address and rest is
            # corresponding data
            print([row[0],row[1],row[2],row[3],row[4]])
            di[int(row[0])] = int(row[1])
            ci[int(row[0])] = int(row[2])
            hr[int(row[0])] = int(row[3])
            ir[int(row[0])] = int(row[4])

    # WORK IN PROGRESS, taken from Async-ServerExample
    store = ModbusSlaveContext(
        di = ModbusSparseDataBlock(di),
        ci = ModbusSparseDataBlock(ci),
        hr = ModbusSparseDataBlock(hr),
        ir = ModbusSparseDataBlock(ir))
    context = ModbusServerContext(slaves=store,single=True)

    for i in di:
        print(di[i])
#   Write to CSV file
    with open('CSVtest2.csv','w',newline='') as csvfile:
        testwriter = csv.writer(csvfile,delimiter=',')
        print("Writing: ")
        for i in di:
            line = [i,di[4-i],ci[4-i],hr[4-i],ir[4-i]]
            print(line)
            testwriter.writerow(line)




    # for line in f:
    #     line = line.split(',')
    #     di[int(line[0])] = int(line[1])
    #     ci[int(line[0])] = int(line[2])
    #     hr[int(line[0])] = int(line[3])
    #     ir[int(line[0])] = int(line[4])
    #
#    diblock  = sparblock(di)
#    print(diblock)


    #print(x.getValues(0))

    #Test stuff
    r = ModbusSparseDataBlock([int(2*x) for x in range(1,10)])
    print(r.getValues(0))
    r.setValues(0,50)
    print(r.getValues(0))
    y = {'a':5,'b':10,'c':20}
    print(y['a'])
    y['d'] = 40
    print(y)

#---------------------------------------------------------------------------#
# Main jumper
#---------------------------------------------------------------------------#
if __name__ == "__main__":
    main()

# DAT300-PyModbus
Implementation of a server with a background thread updating the values of the
server as it is running. The server continuously reads from a supplied input
file and continuously writes to a supplied output file.

The program can be run with the options -I (--inputfile)
where the user supplies a input file with data and sequential addressing.
The supplied input file must be a csv file where the data is ordered in the
following way:
Address, Discrete Input, Coils, Holding Registers, Input Registers
If no input file is supplied dummy data is created.

The output file created by the program is a csv file and contains data ordered in
the aforementioned way. If the -O (--outputfile) option is not used a file
called "OutputExampleFile.csv" will be created in the same directory as the
program is run from. The option -S (--use_samefile) can also be invoked and
results in reading and writing to the same file.

The program has the option of controlling the read and write frequency, that is
how often the files are updated. The option -R (--read_frequency) sets the time,
in seconds, between reads of the input file. The option -W (--write_frequency)
sets the time, in seconds, between writes to the output file. Default is
-R 5 seconds and -W 5.1 seconds. Note that the read time should preferably be
shorter then the write time such that the script can import changes from the
input file before writing to the output file.

For console output/debugging the option -D (--debug) can be set.

NOTICE!
All addresses in the input file should start from 1 and be in sequential order
from there. Leaving gaps in the addressing will cause the write_filedata
function to terminate at the first gap.

LIMITATIONS!
The decision on which input has final say when comparing the contents of the
pymodbus registers and that of the input file was made with the following
reasoning.
As Discrete Input and Input registers are read only tables, the values
contained in the input file to be read overwrites the contents of the pymodbus
Discrete Input and Input registers if they disagree with the current value of
the registers.
For Coils and Holding registers, as they are read/write registers, the current
values of the registers overwrites the values received by the input file.
In summary:
As modifications by a client to the DI and Input registers of a server are not
allowed, the values of the input files are taken as updates by a I/O system and
are kept. However, as Coils and Holding registers are read/write we assume that
we want to keep updates made by the client to the server, therefore we keep the
servers version and disregard the values of the input file for these registers.

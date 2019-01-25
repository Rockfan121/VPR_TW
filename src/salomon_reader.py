"""
Example file:

C101

VEHICLE
NUMBER     CAPACITY
  25         200

CUSTOMER
CUST NO.  XCOORD.   YCOORD.    DEMAND   READY TIME  DUE DATE   SERVICE   TIME
 
    0      40         50          0          0       1236          0                                 
    1      45         68         10        912        967         90 
... (CUSTOMER CUST NO column from 0 to VECHICLE NUMBER or moved by 1)    
"""


class Instance:
    def __init__(self):
        self.name = "unknown"
        self.capacity = 0
        self.vehicle_count = 0


    def read_instance(self, filename):
        with open(filename, 'r') as open_f:
            self.name = open_f.readline()                     # Title for benchmark
            for p in range(3):
            open_f.readline()                             # Empty line, "VECHICLE", reast of header
            line = open_f.readline()
            line.trim() # Get rid of whitespaces before and after the line
            words = line.split()
            if len(words) == 2:
                self.vehicle_count = int(words[0])
                self.capacity = int(words[1])

            vehicles = []
            while line != '\n':
                line = open_f.readline()


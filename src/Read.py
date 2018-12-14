#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

class Data(object):
    def __init__(self, row = None):
        if not row:
            self.empty()
            return
        row = row.strip()
        row = row.split()
        if len(row) == 7:
            row = list(map(lambda x: int(x), row))
            attrs = ['customer', 'x_coord', 'y_coord', 'demand', 'ready_time', 'due_date', 'service_time']
            obj = dict()
            for (k, v) in zip(attrs, row):
                setattr(self, k, v)
    def empty(self):
        self.customer = -1
        self.x_coord = 0
        self.y_coord = 0
        self.demand = 0
        self.ready_time = 0
        self.due_date = 0
        self.service_time = 0
    def __repr__(self):
        return 'Data object: {}'.format(str(self.__dict__))

def get_data():
    open_f = open('../input/C101.txt', 'r')
    name = (open_f.readline()).strip()                     # Title for benchmark
    for p in range(3):
        open_f.readline()                             # Empty line, "VECHICLE", reast of header
    line = open_f.readline()
    line = line.strip() # Get rid of whitespaces before and after the line
    words = line.split()
    if len(words) == 2:
        vehicle_count = int(words[0])
        capacity = int(words[1])
        print('Vehicle count: {}'.format(vehicle_count))
        print('Capacity: {}'.format(capacity))

    data = []
    for i in range(4):
        open_f.readline()

    for line in open_f:
        line = line.strip()
        # Non empty line
        if line != '':
            d = Data(line)
            if d:
                data.append(d)


    # In[2]:


    for d in data:
        print(d.__dict__)
    return data


# In[3]:


import math
def dist(point1, point2):
    diff_x = point2.x_coord - point1.x_coord
    diff_y = point2.y_coord - point2.y_coord
    return math.sqrt(diff_x**2 + diff_y**2)


# In[4]:


class Solution(object):
    """set of sequences of customers ids
       len(set) cannot be longer than count of vehicles
       For each vehicle, it cannot take more demand that the defined capacity
    """
    def __init__(self, routes):
        self.routes = routes
    
    def __repr__(self):
        return str(self.__dict__)
    
class Constraints(object):
    def __init__(self, vehicles, capacity):
        self.vehicle_count = vehicles
        self.capacity = capacity
    def __repr__(self):
        return str(self.__dict__)


class Route(object):
    """
        Route of single vehicle with global constraints
    """
    def __init__(self, constraints, vehicle_id, sequence, data):
        self.constraints = constraints
        self._id = vehicle_id
        self.seq = sequence
        self.cost = 0
        self.feasable = self.check_feasability(data)
        
    def __repr__(self):
        return str(self.__dict__)
    
    def check_feasability(self, data):
        '''
        place is the id of place in the route.
        Each vehicle start at (0, 0) on time 0.
        
        '''
        cap = self.constraints.capacity
        for place in self.seq:
            cap -= data[place].demand
        if cap < 0:
            return "overload"
        return self.count_cost(data)['result']
        
    def count_cost(self, data):
        current_time = 0
        
        baza = Data()
        baza.x_coord = data[0].x_coord
        baza.y_coord = data[0].y_coord
        cost = 0

        last_place = baza
        # example data[place] = "{'customer': 25, 'x_coord': 25, 'y_coord': 52, 
        # 'demand': 40, 'ready_time': 169, 'due_date': 224, 'service_time': 90}"
        for place in self.seq:
            target = data[place]
            arrival_time = current_time + dist(target, last_place)
            last_place = target
            if arrival_time < target.ready_time:
                arrival_time = target.ready_time
            if arrival_time <= target.due_date:
                cost += arrival_time - current_time
                current_time = arrival_time + target.service_time
            else:
                # print("Cannot create route")
                return {'result': "overtime", 'cost': float('inf') }
        if len(self.seq) > 0:
            cost += dist(data[self.seq[-1]], baza)
        self.cost = cost
        return {'result': "ok", 'cost': cost }

    def make_feasible(self, data):
        seq_copy: list = [ x for x in self.seq]
        dependencies = {}
        pos = 0
        for place in self.seq:
            info = data[place]
            dependencies[place] = GraphNode(place, info.ready_time, info.due_date, pos)
            pos += 1
        for place in dependencies.values():
            place.get_priority(dependencies)

        new_deps = sorted(dependencies.values(), key=lambda x: x.value()) ####
        seq_copy = [x.no for x in new_deps]
        self.seq = seq_copy



class GraphNode(object):
    def __init__(self, no, ready_time, due_time, position):
        self.PROPORTION = 10000
        self.no = no
        self.ready_time = ready_time
        self.due_time = due_time
        self.position = position
        self.prio = 0

    def get_priority(self, allNodes):
        current = 0
        if self.prio > 0:
            return self.prio
        for node in allNodes.values():
            if node.due_time < self.ready_time:
                current = max(current, node.get_priority(allNodes))
        self.prio = current + 1
        return self.prio

    def value(self):
        return self.prio * self.PROPORTION + self.position

# In[5]:


# r = Route(Constraints(vehicle_count, capacity), 0, [0, 3, 4, 20], data)
# print("r value:")
# print(r)
    


# In[ ]:





# In[ ]:





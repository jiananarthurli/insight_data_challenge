from datetime import datetime
from time import time
import sys
import os

class pharmRecord(object):
    
    def __init__(self, input_path, output_path, k=None, logging=False, log_path=None):
        # file paths
        self.input_path = input_path
        self.output_path = output_path
        self.log_path = log_path
        
        # output top k prescribed drugs. 
        # k=None by default and all drugs are in the output
        self.k = k
        
        # logging flag
        self.logging = logging
        
        # dictionary for drug records
        self.records = {}
        
        # heap and stack for record sorting
        self.hp = []
        self.stack = []
    

    # create and recycle the file handlers using __enter__ and __exit__
    def __enter__(self):

        if self.logging:
            self.log_f = open(self.log_path, 'w')

        self.input_f = open(self.input_path, 'r')
        self.output_f = open(self.output_path, 'w')

        return self
    
    def __exit__(self, exc_type, exc_value, traceback):

        if self.logging:
            if not exc_type:
                self.log(status='NORMAL', 
                         message='Program finished successfully.')
            else:
                self.log(status='ERROR', 
                         message='Program was terminated unexpectedly.')
            self.log_f.close()

        self.input_f.close()
        self.output_f.close()
    
    # logging function
    def log(self, status='', message='', line_num=None, line=''):
        if line_num is not None:
            log_line = str(datetime.now()) + '\t' + status + '\t' + message + '\t' + str(line_num) + '\t' + line + '\n'
        else:
            log_line = str(datetime.now()) + '\t' + status + '\t' + message + '\t' + '\t' + '\n' # keep the log format uniform
        self.log_f.write(log_line)
    
    
    # read the input file into self.records
    def read_input(self):
    
        line_num = -1
        
        tic = time() # record starting time
        if self.logging:
            self.log(status='NORMAL', message='start reading the input file.')
    
        # read the file by lines
        for line in self.input_f:
            
            line_num += 1
            if line_num == 0:
                continue
            line_array = line.strip().split(',')

            try:
                int(line_array[0]) # check if the record number is an integer. If not, skip this line.
            except ValueError:
                if self.logging:
                    self.log(status='WARNING', 
                             message='Missing record number.', 
                             line_num=line_num, 
                             line=line)
                continue

            try:
                float(line_array[-1]) # check if the last element is a valid float. If not, skip this line.
            except ValueError:
                if self.logging:
                    self.log(status='WARNING', 
                             message='Missing drug price.', 
                             line_num=line_num, 
                             line=line)
                continue

            patient_name = ','.join(line_array[1:-2]) # patients' last and first name are joined using ','
            drug_name = line_array[-2] # assume the second last element is the drug name
            drug_cost = float(line_array[-1]) # assume the last element is the drug cost. 

            if drug_name not in self.records: # make a new entry for a drug if not in the dictionary
                self.records[drug_name] = {'patients' : set(), 'costs' : 0}

            self.records[drug_name]['patients'].add(patient_name) # use hashset to remove name duplication
            self.records[drug_name]['costs'] += drug_cost # sum all the costs for a drug
            
        if self.logging:
            self.log(status='NORMAL', 
                     message='Finish reading {} lines in {} seconds.'.format(line_num, time() - tic))
    
    
    # sort the medicine records using heap
    def sort(self):
        
        # heap-sort object
        heap = pharmHeap()
        
        if self.logging:
            self.log(status='NORMAL',
                     message='Start sorting the drug records.')
                
            for key in self.records.keys():
                elem = (key, len(self.records[key]['patients']), self.records[key]['costs'])
#                elem = (key, len(self.records[key]['patients']), int(self.records[key]['costs'])) # to pass the online test, somehow the total prices have to be integers.
                heap.push(self.hp, elem)
                if self.k is not None: # only keep the top k drugs in the heap
                    if len(self.hp) > self.k:
                        heap.pop(self.hp) # pop the drug record with minimum total cost if the max heap size is reached
        
        # pop all the recods in the heap into the stack
        while self.hp:
            self.stack.append(heap.pop(self.hp))
        
        if self.logging:
            self.log(status='NORMAL', 
                     message='Sorting finished.')
    
    
    # write the sorted drug records into output file
    def write_output(self):
        
        length = len(self.stack)
        line = '' # line to be written
        
        line = 'drug_name,num_prescriber,total_cost\n'
        self.output_f.write(line)
        
        while self.stack:
            elem = self.stack.pop() # Drug records are stored in reversed order in stack.
            line = elem[0] + ',' + str(elem[1]) + ',' + str(elem[2]) + '\n'
            self.output_f.write(line)
        
        if self.logging:
            self.log(status='NORMAL', 
                     message='Written {} drug records.'.format(length))
            

class pharmHeap:
    # Maintain a minimum heap, so that the element on top has the minimum total_cost. 
    # If there is a tie, element with higher alphabetical order position would be placed on top
    
    # push the new element to the end, then sift up
    def push(self, hq, elem):
        i = len(hq)
        hq.append(elem)
        self.siftUp(hq, i)

        
    # swap the min element on heap top with the one on the end
    # then pop the min element and sift down
    def pop(self, hq):
        hq[0], hq[-1] = hq[-1], hq[0]
        elem = hq.pop()
        self.siftDown(hq, 0)
        return elem
    
    
    # move hq[i] upwards until heap condition satisfied
    def siftUp(self, hq, i):
        p = self.parent(i)
        if p is not None and self.compare(hq[i], hq[p]):
            hq[i], hq[p] = hq[p], hq[i]
            # call the function recursively if the heap condition is not satisfied
            self.siftUp(hq, p)
    
    
    # move hq[i] downwards until heap condition satisfied
    def siftDown(self, hq, i):
        lc = self.lChild(hq, i)
        rc = self.rChild(hq, i)
        
        # if both left child and right child exist
        if lc and rc:
            # if both children are smaller than the element, swap with the smaller child
            if self.compare(hq[lc], hq[i]) and self.compare(hq[rc], hq[i]):
                if self.compare(hq[lc], hq[rc]):
                    hq[i], hq[lc] = hq[lc], hq[i]
                    self.siftDown(hq, lc)
                else:
                    hq[i], hq[rc] = hq[rc], hq[i]
                    self.siftDown(hq, rc)
        # if at most one child exists or smaller than the element, swap if it exists and is smaller the element
        if lc and self.compare(hq[lc], hq[i]):
            hq[i], hq[lc] = hq[lc], hq[i]
            self.siftDown(hq, lc)
        if rc and self.compare(hq[rc], hq[i]):
            hq[i], hq[rc] = hq[rc], hq[i]
            self.siftDown(hq, rc)

            
    # index of the parent. Return None if doesn't exist.
    def parent(self, i):
        if i == 0:
            return None
        return (i - 1) // 2

    
    # index of the left child. Return None if doesn't exist.
    def lChild(self, hq, i):
        lc = 2 * i + 1
        if lc >= len(hq):
            return None
        return lc
    
    
    # index of the right child. Return None if doesn't exist.
    def rChild(self, hq, i):
        rc = 2 * i + 2
        if rc >= len(hq):
            return None
        return rc
    
    
    # compare if RA is "smaller than" RB
    # compare the total_cost first, if total_costs are equal, compare whether RA's name is after RB's name in alphabetical order
    # record: (drug_name, patients, total_cost)
    def compare(self, RA, RB):
        # when total_costs are unequal, only compare the costs
        if RA[2] < RB[2]:
            return True
        if RA[2] > RB[2]:
            return False
        
        # when total_costs are equal, compare the name
        return RA[0] > RB[0]    
    
    
def main():

    # the program needs at least two parameters
    if len(sys.argv) < 3:
        print('Input and output paths are not specified.')
        return

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.isfile(input_path):
        print('Input file \'{}\' does not exist.'.format(input_path))
        return
        
    k = None # output all the drug records by default. if k is not None then top k records are in the output.
    logging = True # logging is enabled by default.
    log_path = 'log.txt' # default logging path.
    
    # if parameter K exists
    try: 
        k = int(sys.argv[3])
    except (IndexError, ValueError):
        pass
    
    # if the logging flag parameter exists
    try: 
        sys.argv[4]
        if sys.argv[4] == '1':
            k = True
        elif sys.argv[4] == '0':
            k = False
        else:
            print('Logging flag should be 0 or 1. Program continues with logging.')
    except (IndexError, ValueError):
        pass
    
    # if a customized log path is specified
    try:
        sys.argv[5]
        log_path = sys.argv[5]
    except IndexError:
        pass

    with pharmRecord(input_path, output_path, k, logging, log_path) as pharmrecord:
        pharmrecord.read_input()
        pharmrecord.sort()
        pharmrecord.write_output()

if __name__ == '__main__':
    main()
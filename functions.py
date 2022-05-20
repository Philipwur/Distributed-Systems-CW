# -*- coding: utf-8 -*-
import coursework_pb2

'''
import file for functions used by both server and client, to save space
'''

#a function to flatten the matrix before being sent between server and client
def fltn(array):
    return [item for sublist in array for item in sublist]

#a function to compress the matrix into the format shown in the proto file
#contrains number of rows and full data set
def zip_mat(matrix):
    
    rows = len(matrix[0])
    values = fltn(matrix)
    
    proto_matrix = coursework_pb2.Matrix(rows = rows, 
                                         values = values)
    
    return proto_matrix

#function to take matrix out of its compressed state
def decomp_mat(proto_matrix):
    
    values, rows = proto_matrix.values, proto_matrix.rows

    matrix = [[values[i+j*rows] for i in range(rows)] for j in range (rows)]

    return matrix

#function to read file and obtain matrix
def get_mat(filename):
    
    with open(filename) as file1:
        
        matrix = [[int(num) for num in line.split(" ")] 
                   for line in file1]
    return matrix
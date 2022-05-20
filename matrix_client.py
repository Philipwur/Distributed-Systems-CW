# -*- coding: utf-8 -*-
import timeit
import math
import numpy as np

import grpc
import asyncio
import logging
import coursework_pb2 as pb2
import coursework_pb2_grpc as pb2_grpc

import functions as fun

#this function sends a request to a server to multiply or add the matrices
async def send_request(Matrix_1, Matrix_2, server, method):
    
    stub = pb2_grpc.MatrixOperationStub(grpc.insecure_channel(server))
    
    Matrix_1 = fun.zip_mat(Matrix_1)
    Matrix_2 = fun.zip_mat(Matrix_2)
    
    if method == "add":
        add = stub.Addition(pb2.Matrices_in(Matrix_1 = Matrix_1, 
                                            Matrix_2 = Matrix_2))
        out = fun.decomp_mat(add.matrix_3)
        return out
    
    elif method == "mult":
        mult = stub.Multiplication(pb2.Matrices_in(Matrix_1 = Matrix_1, 
                                                   Matrix_2 = Matrix_2))
        out = fun.decomp_mat(mult.Matrix_3)
        return out
    
    
#converts matrix into blocks of 2
def blockify(array):
    
    block_matrix = []
    
    for i in range(0, (len(array)), 2):
        temp = []
    
        for j in range(0, (len(array)), 2):
        
            temp.append([[array[i][j], array[i][j+1]],
                         [array[i+1][j], array[i+1][j+1]]])
        
            if j == len(array) - 2:
                block_matrix.append(temp)
    
    out = np.block(block_matrix)
    return out


#takes matrix out of blocked form and back into normal matrix
def de_blockify(array):
    count = -1
    
    de_blocked = [[0 for i in range(2 * len(array))]
                 for j in range(2 * len(array))]
    
    for i in range(0, len(array)):
        for j in range(0, 2):
            count += 1
            for k in range(0, len(array)):
                k2 = k*2
                de_blocked[count][k2] += array[i][k][j][0]
                de_blocked[count][k2+1] += array[i][k][j][1]

    out = de_blocked
    return out

#this function calculates how many servers are needed to meet the deadline
async def deadline_scaler(Matrix_1, Matrix_2, deadline):
    
    test_block_1 = blockify(Matrix_1)
    
    test_block_2 =  blockify(Matrix_2)
    
    start = timeit.timeit()
    await send_request(test_block_1[0][0], test_block_2[0][0], "localhost:8080", "mult")
    time_taken = timeit.timeit() - start
    
    #total amount of multiplication operations is the size of the matrix to the power of 3
    num_servers = int(min(8, math.ceil(1 + (time_taken * (len(Matrix_1) ** 3/deadline)))))
    return num_servers


async def multiply_blocks(block_1, block_2, servers):
    #steps
    #1 identify what block pairs have to be multiplied with what (without addition step)
    #2 spread the workload to the amount of servers defined
    #3 send jobs to servers
    #4 collect block multiples
    
    
    results = [[0 for i in range(len(block_1))] 
                 for j in range(len(block_1))]
    
    task_list = []
    
    for i in range(len(block_1)):
        for j in range(len(block_1)):
            for k in range(len(block_1)):
                x, y = block_1[i][k], block_2[k][j]
                task1 = asyncio.create_task(send_request(x, y, servers[k], "mult"))
                task_list.append(task1)
    
    response = await asyncio.gather(*task_list)
    results = []
    for res in response:
        results.append(res)
        
    print(results)
    

    return results

    
async def run():
    
    servers = ["localhost:{}".format(port) for port in range(8080, 8088)]
    
    deadline = 0.5
    
    Matrix_1 = fun.get_mat("matrix_1.txt")
    Matrix_2 = fun.get_mat("matrix_2.txt")
    
    num_servers = await deadline_scaler(Matrix_1, Matrix_2, deadline)
    #for the sake of example num_servers is 3 since deadline scalar recieves 1 constantly
    #servers = servers[:3]
    
    Matrix_1 = blockify(Matrix_1)
    Matrix_2 = blockify(Matrix_2)
    
    Matrix_3 = await multiply_blocks(Matrix_1, Matrix_2, servers)
    
    
    print(Matrix_3)
    #print(np.mat(Matrix_3))
    

if __name__ == "__main__":
    logging.basicConfig()
    asyncio.run(run())
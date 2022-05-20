# -*- coding: utf-8 -*-
import logging
import os
import numpy as np

import grpc
import coursework_pb2
import coursework_pb2_grpc

from concurrent import futures
from multiprocessing import Process

import functions as fun

class Mat_operations(coursework_pb2_grpc.MatrixOperationServicer):
    
    def Addition(self, request, context): 
        
        print("addition request recieved on {}".format(os.getpid()))
        Matrix_1 = fun.decomp_mat(request.Matrix_1)
        Matrix_2 = fun.decomp_mat(request.Matrix_2)
        
        Matrix_3 = np.add(Matrix_1, Matrix_2)
        #print(Matrix_3)
        Matrix_3 = fun.zip_mat(Matrix_3)
        
        out = coursework_pb2.Matrix_out(Matrix_3 = Matrix_3)
        
        return out
    
    def Multiplication(self, request, context):
        
        print("multiplication request recieved on {}".format(os.getpid()))
        Matrix_1 = fun.decomp_mat(request.Matrix_1)
        Matrix_2 = fun.decomp_mat(request.Matrix_2)
        
        Matrix_3 = np.matmul(Matrix_1, Matrix_2)

        Matrix_3 = fun.zip_mat(Matrix_3)
        
        out = coursework_pb2.Matrix_out(Matrix_3 = Matrix_3)
        
        return out

def serve(port):
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    coursework_pb2_grpc.add_MatrixOperationServicer_to_server(Mat_operations(),
                                                              server)
    server.add_insecure_port('[::]:{}'.format(port))
    server.start()
    print("Server Online on {}".format(port), " process:", os.getpid())
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    for port in range(8080, 8088):
        p = Process(target=serve, args = (port,))
        p.start()

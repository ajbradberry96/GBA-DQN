# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 11:44:16 2019

@author: Moosnum2
"""

import socket               
import matplotlib.image as mpimg
import queue
import time
 # A LEFT RIGHT NOTHING
 
action_dict = {"1000" : '|    0,    0,    0,  100,.......A...|', 
               "0100" : '|    0,    0,    0,  100,..L........|',
               "0010" : '|    0,    0,    0,  100,...R.......|', 
               "0001" : '|    0,    0,    0,  100,...........|'}
class Server():
    def __init__(self):
        self.s = socket.socket()         # Create a socket object
        self.host = 'localhost'          # Get local machine name
        self.port = 36296                # Reserve a port for your service.
        self.s.bind((self.host, self.port))        # Bind to the port
        self.RECV_BUFFER = 4096          # Advisable to keep it as an exponent of 2

        print("Server started. Listening on port ", self.port)
        self.s.listen(5)                 # Now wait for client connection.
        
        self.c, addr = self.s.accept()     # Establish connection with client.
        print('Got connection from', addr)
        print(self.c.recv(self.RECV_BUFFER).decode('utf-8'))
        self.c.send(bytes('Connected to Python.','utf-8'))
    
        # Get the number of frames in a stack
        self.num_frames = int(self.c.recv(self.RECV_BUFFER).decode('utf-8'))
        print("Number of frames per stack: ", self.num_frames)
        self.restart()
        
    def get_state(self):
        frame_stack = queue.Queue(maxsize=self.num_frames)
        self.c.send(bytes("send state",'utf-8'))
        data = self.c.recv(self.RECV_BUFFER).decode("utf-8")
        self.c.send(bytes("State received.",'utf-8'))

        
        for i in range(self.num_frames):
            frame_stack.put(mpimg.imread('../States/frame' + str(i + 1)+ '.png'))

        score = int(data.split(',')[0])
        game_over_num = int(data.split(',')[1])
        if game_over_num == 1:
            game_over = False
        else:
            game_over = True

        self.c.recv(self.RECV_BUFFER)
        return (frame_stack, score, game_over)
    
    def send_action(self, action):
        # Action comes as a one-hot list
        self.c.send(bytes("receive action",'utf-8'))
        self.c.recv(self.RECV_BUFFER)
        
        
        self.c.send(bytes(action_dict[action],'utf-8'))
        self.c.recv(self.RECV_BUFFER)
        
    def restart(self):
        self.c.send(bytes("restart",'utf-8'))
        self.c.recv(self.RECV_BUFFER)
        
    def close(self):
        print("Closing connection with GBA")
        self.c.send(bytes("close",'utf-8'))
        time.sleep(1)
        self.c.close()
        self.s.close()
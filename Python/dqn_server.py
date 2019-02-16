# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 11:44:16 2019

Module containing Server() class, which communicates over TCP with a Lua 
script in BizHawk.

@author: Moosnum2
"""

import socket               
import matplotlib.image as mpimg
import time
import subprocess

NUM_FRAMES = 4
# Dictionary mapping action numbers to their corresponding Input Log
# strings. For SMB, the available actions are A LEFT RIGHT NOTHING
action_dict = {0 : '|    0,    0,    0,  100,.......A...|', 
               1 : '|    0,    0,    0,  100,..L........|',
               2 : '|    0,    0,    0,  100,...R.......|', 
               3 : '|    0,    0,    0,  100,...........|'}
class Server():
    def __init__(self):
        # Create a socket object
        self.s = socket.socket()         
        self.host = 'localhost'          
        self.port = 36296                
        self.s.bind((self.host, self.port))
        self.RECV_BUFFER = 4096
    
        print("Server started. Listening on port ", self.port)
        
        # Now wait for client connection. At this point, start Lua script
        self.s.listen(5)                 
        
        self.s.settimeout(30)
        
        self.start_game()

    def start_game(self):
        self.game = subprocess.Popen(['../Emulation/EmuHawk.exe', 
                                 '--lua=../Emulation/dqn_client.lua', 
                                 '../Emulation/ROMS/SMA4.gba'])
    
        # Establish connection with client.
        self.c, addr = self.s.accept()     
        print('Got connection from', addr)
        print(self.c.recv(self.RECV_BUFFER).decode('utf-8'))
        self.c.send(bytes('Connected to Python.','utf-8'))
    
        # Get the number of frames in a stack
        self.num_frames = int(self.c.recv(self.RECV_BUFFER).decode('utf-8'))
        print("Number of frames per stack: ", self.num_frames)
        print("Should be equal to:", NUM_FRAMES)
        
    def get_state(self):
        # Saves the most recent 4 frames, and receives the score and game_over
        frame_stack = []
        self.c.send(bytes("send state",'utf-8'))
        data = self.c.recv(self.RECV_BUFFER).decode("utf-8")
        self.c.send(bytes("State received.",'utf-8'))

        # Add the frames to the stack from file
        for i in range(self.num_frames):
            frame_stack.append(mpimg.imread('../States/frame' + str(i + 1)+ '.png'))
        
        # Score and game over data are sent as score,game_over
        score = int(data.split(',')[0])
        game_over_num = int(data.split(',')[1])
        
        # game_over_num is 0 if the game is over, 1 otherwise  
        if game_over_num == 1:
            game_over = False
        else:
            game_over = True

        self.c.recv(self.RECV_BUFFER)
        return (frame_stack, score, game_over)
    
    def get_action(self):
        self.c.send(bytes("send action", 'utf-8'))
        data = self.c.recv(self.RECV_BUFFER).decode("utf-8")

        return int(data)
    
    def send_action(self, action):
        # Send action to emulator in Input Log string form
        self.c.send(bytes("receive action",'utf-8'))
        self.c.recv(self.RECV_BUFFER)
        
        self.c.send(bytes(action_dict[action],'utf-8'))
        self.c.recv(self.RECV_BUFFER)
        
    def restart(self):
        # Reset the game to its starting state
        self.c.send(bytes("restart",'utf-8'))
        self.c.recv(self.RECV_BUFFER)
        
    def close(self):
        # Close TCP connection and server
        print("Closing connection with GBA")
        self.c.send(bytes("close",'utf-8'))
        time.sleep(1)
        self.c.close()
        self.s.close()
        self.game.terminate()
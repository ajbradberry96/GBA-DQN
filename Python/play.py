# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 07:10:56 2019

Module that has an alread trained DQN play the game

@author: Moosnum2
"""

import dqn_server
import preprocessor
import agent as a
import numpy as np
import tensorflow as tf
import time as t
start = t.time()

# Number of available actions
N_ACTIONS = 4
# Number of frames per stack
N_FRAMES = 4

agent = a.Agent(N_ACTIONS)
server = dqn_server.Server()
prep = preprocessor.Preprocessor(N_FRAMES)

with tf.Session() as sess:
    # Load the model
    agent.restore(sess, "./models/model.ckpt")
    server.restart()
     
    frames, score, game_over = server.get_state()
    stack = prep.stack_frames(frames)
    
    while not game_over:
        # Take the biggest Q value (= the best action)
        Qs = agent.get_Qs([stack], sess)[0]
        
        # Take the biggest Q value (= the best action)
        action = np.argmax(Qs)
        
        server.send_action(action)
        
        frames, score, game_over = server.get_state()
        stack = prep.stack_frames(frames)

    print("Score: ", score)
    server.close()
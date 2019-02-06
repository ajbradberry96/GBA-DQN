# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 17:40:03 2019

@author: Moosnum2
"""

import dqn_server
import preprocessor
import agent as a
import numpy as np

# Number of actions available to our agent
N_ACTIONS = 4
# Number of frames per stack
N_FRAMES = 4
# Maximum number of steps in any given episode
MAX_SESS = 3000

agent = a.Agent(N_ACTIONS)
server = dqn_server.Server(N_FRAMES)
prep = preprocessor.Preprocessor(N_FRAMES)

# Pre load agent's memory
new_frames = None
new_score = None
new_game_over = None
action = None
reward = None
new_stack = None
new_game = True

for i in range(MAX_SESS):
    # If it's the first step
    if new_game:
        # Start a new episode
        server.restart()
        
        # First we need a state (again)
        frames, score, game_over = server.get_state()
        stack = prep.stack_frames(frames)
        
        new_game = False
    else:
        # Otherwise, we just completed a step, so add a memory
        agent.add_memory((stack, action, reward, new_stack, new_game_over))
        # Set old state
        frames, score, game_over = new_frames, new_score, new_game_over
        
    # Get the rewards and next state
    action = server.get_action()

    new_frames, new_score, new_game_over = server.get_state()
    new_stack = prep.stack_frames(new_frames)
    
    # Disincentivize game overs...
    if new_game_over:
        end_score = -10
    else:
        end_score = -.01
    reward = ((new_score - score) / 10 + end_score) / 100
    
    # If we're dead
    if new_game_over:
        # We finished the episode
        next_state = np.zeros(stack.shape)
        
        # Add experience to memory
        agent.add_memory((stack, action, reward, next_state, new_game_over))
        
        new_game = True

server.close()
agent.save_memory("../Memories/mem.pkl")
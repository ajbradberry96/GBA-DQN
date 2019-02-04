# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 21:27:06 2019

Memory for a DQN Agent

@author: Moosnum2
"""
import numpy as np
from collections import deque

class Memory():
    def __init__(self, max_size):
        # Create memory buffer of size max_size
        self.buffer = deque(maxlen = max_size)
    
    def add(self, experience):
        # Add a memory to the buffer
        self.buffer.append(experience)
    
    def sample(self, batch_size):
        # Get a random sample of memories from buffer
        buffer_size = len(self.buffer)
        index = np.random.choice(np.arange(buffer_size),
                                 size = batch_size,
                                 replace = False)
        
        return [self.buffer[i] for i in index]
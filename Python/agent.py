# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 21:22:12 2019

@author: Moosnum2
"""
import dqn
import memory

class Agent():
    def __init__(self, N_ACTIONS):                
        ### MEMORY HYPERPARAMETERS
        self.pretrain_length = 64
        self.memory_size = 1000000          # Number of experiences the Memory can keep
        self.model = dqn.DQN()
        self.memory = memory.Memory(self.memory_size)
        
        self.model.set_up_board()
    
    def add_memory(self, experience):
        self.memory.add(experience)
    
    def predict_action(self, decay_step, state, sess):
        return self.model.predict_action(decay_step, state, sess)
    
    def memory_sample(self, batch_size):
        return self.memory.sample(batch_size)
    
    def get_Qs(self, next_states, sess):
        return self.model.get_Qs(next_states, sess)
    
    def get_loss(self, states_mb, targets_mb, actions_mb, sess):
        return self.model.get_loss(states_mb, targets_mb, actions_mb, sess)
    
    def write(self, episode, states_mb, targets_mb, actions_mb, sess):
        self.model.write(episode, states_mb, targets_mb, actions_mb, sess)
        
    def save(self, sess, path):
        self.model.save(sess, path)
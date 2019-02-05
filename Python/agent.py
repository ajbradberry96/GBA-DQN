# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 21:22:12 2019

Module containing Agent() class, which holds memories and generates 
predictions from a model (currently, a DQN) based upon game states.

@author: Moosnum2
"""
import dqn
import memory
import pickle as pkl

class Agent():
    def __init__(self, N_ACTIONS, memory_path=None):                
        if memory_path == None:
            ### MEMORY HYPERPARAMETERS
            # Number of experiences the Memory can keep     
            self.memory = memory.Memory(1000000)
        else:
            self.memory = pkl.load(open(memory_path, 'rb'))
            
        self.model = dqn.DQN()
        # Set up tensorboard
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
        
    def restore(self, sess, path):
        self.model.restore(sess, path)
    
    def save_memory(self, path):
        pkl.dump(self.memory, open(path, 'wb'))
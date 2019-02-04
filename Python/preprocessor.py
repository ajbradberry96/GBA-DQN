# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 21:25:32 2019

Preprocesses frames into a stack of 84x84 grayscale images
@author: Moosnum2
"""
import skimage.transform
import skimage.color
from collections import deque
import numpy as np

class Preprocessor():
    def __init__(self, n_frames):
        # Number of frames per stack
        self.n_frames = n_frames
        
    def preprocess_frame(self, frame, width=84, height=84):
        # Lower resolution of frame and change to grayscale
        frame = skimage.transform.resize(frame, (height, width))
        frame = skimage.color.rgb2gray(frame)
        return frame
    
    def stack_frames(self, frames):
        # Given unprocessed frames, create stack of processed frames
        stack  =  deque([np.zeros((84, 84), dtype=np.int) for i in range(self.n_frames)], maxlen=self.n_frames)
        
        for frame in frames:
            stack.append(self.preprocess_frame(frame))
        
        return np.stack(stack, axis=2)
    
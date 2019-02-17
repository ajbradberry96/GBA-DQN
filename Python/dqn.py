# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 21:26:46 2019

Module containing basic DQN

@author: Moosnum2
"""
import tensorflow as tf
import numpy as np

class DQN():
    def __init__(self, name='DQNetwork'):
        # Reset the graph
        tf.reset_default_graph()
        
        ### MODEL HYPERPARAMETERS
        # Our input is a stack of 4 84x84 frames
        self.state_size = [84,84,4]    
        # Number of actions available (TODO:Make this a passable parameter?)
        self.action_size = 4
        # Alpha
        self.learning_rate =  0.0001      
        
        # Exploration parameters for epsilon greedy strategy
        self.explore_start = 1.0            
        self.explore_stop = 0.05            
        self.decay_rate = 0.0001            
        
        with tf.variable_scope(name):
            # We create the placeholders
            self.inputs_ = tf.placeholder(tf.float32, [None, *self.state_size], name="inputs")
            
            self.actions_ = tf.placeholder(tf.float32, [None, self.action_size], name="actions_")

                
            # target_Q is R(s,a) + ymax Qhat(s', a')
            self.target_Q = tf.placeholder(tf.float32, [None], name="target")
                
            """
            First convnet:
            CNN
            BatchNormalization
            ELU
            """
            # Input is 84x84x4
            self.conv1 = tf.layers.conv2d(inputs=self.inputs_,
                                          filters=32,
                                          kernel_size=[8,8],
                                          strides=[4,4],
                                          padding="VALID",
                                          kernel_initializer=tf.contrib.layers.xavier_initializer_conv2d(),
                                          name="conv1")
                
            self.conv1_batchnorm = tf.layers.batch_normalization(self.conv1,
                                                                 training=True,
                                                                 epsilon=1e-5,
                                                                 name='batch_norm1')
                
            self.conv1_out = tf.nn.elu(self.conv1_batchnorm, name="conv1_out")
            ## --> [20, 20, 32]
                
                
            """
            Second convnet:
            CNN
            BatchNormalization
            ELU
            """
            self.conv2 = tf.layers.conv2d(inputs=self.conv1_out,
                                          filters=64,
                                          kernel_size=[4,4],
                                          strides=[2,2],
                                          padding="VALID",
                                          kernel_initializer=tf.contrib.layers.xavier_initializer_conv2d(),
                                          name="conv2")
            
            self.conv2_batchnorm = tf.layers.batch_normalization(self.conv2,
                                                                 training=True,
                                                                 epsilon=1e-5,
                                                                 name='batch_norm2')
    
            self.conv2_out = tf.nn.elu(self.conv2_batchnorm, name="conv2_out")
                ## --> [9, 9, 64]
                
                
            """
            Third convnet:
            CNN
            BatchNormalization
            ELU
            """
            self.conv3 = tf.layers.conv2d(inputs=self.conv2_out,
                                          filters=128,
                                          kernel_size=[4,4],
                                          strides=[2,2],
                                          padding="VALID",
                                          kernel_initializer=tf.contrib.layers.xavier_initializer_conv2d(),
                                          name="conv3")
            
            self.conv3_batchnorm = tf.layers.batch_normalization(self.conv3,
                                                                 training=True,
                                                                 epsilon=1e-5,
                                                                 name='batch_norm3')
    
            self.conv3_out = tf.nn.elu(self.conv3_batchnorm, name="conv3_out")
            ## --> [3, 3, 128]
                
                
            self.flatten = tf.layers.flatten(self.conv3_out)
            ## --> [1152]
                
                
            self.fc1 = tf.layers.dense(inputs=self.flatten,
                                       units=256,
                                       activation=tf.nn.elu,
                                       kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                       name="fc1")
                
            self.fc2 = tf.layers.dense(inputs=self.fc1,
                                       units=256,
                                       activation=tf.nn.elu,
                                       kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                       name="fc2")
            
            self.fc3 = tf.layers.dense(inputs=self.fc2,
                                       units=256,
                                       activation=tf.nn.elu,
                                       kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                       name="fc3")
                        
            self.output = tf.layers.dense(inputs=self.fc3, 
                                          kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                          units=self.action_size, 
                                          activation=None)
    
      
            # Q is our predicted Q value.
            self.Q = tf.reduce_sum(tf.multiply(self.output, self.actions_), axis=1)
                
                
            # The loss is the difference between our predicted Q_values and the Q_target
            # Sum(Qtarget - Q)^2
            self.loss = tf.reduce_mean(tf.square(self.target_Q - self.Q))
                
            self.optimizer = tf.train.RMSPropOptimizer(self.learning_rate).minimize(self.loss)
            
        # Saver will help us to save our model
        self.saver = tf.train.Saver()
        
    def set_up_board(self):
        # Setup TensorBoard Writer
        self.writer = tf.summary.FileWriter("/tensorboard/dqn/1")

        ## Losses
        tf.summary.scalar("Loss", self.loss)

        self.write_op = tf.summary.merge_all()
        
    """
    This function will do the part
    With ϵ select a random action atat, otherwise select at=argmaxaQ(st,a)
    """
    def predict_action(self, decay_step, state, sess):
        ## EPSILON GREEDY STRATEGY
        # Choose action a from state s using epsilon greedy.
        ## First we randomize a number
        exp_exp_tradeoff = np.random.rand()
    
        # Here we'll use an improved version of our epsilon greedy strategy used in Q-learning notebook
        explore_probability = self.explore_stop + (self.explore_start - self.explore_stop) * np.exp(-self.decay_rate * decay_step)
        
        if (explore_probability > exp_exp_tradeoff):
            # Make a random action (exploration)
            action = np.random.randint(0, self.action_size)
            
        else:
            # Get action from Q-network (exploitation)
            # Estimate the Qs values state
            Qs = sess.run(self.output, feed_dict={self.inputs_: state.reshape((1, *state.shape))})
            
            # Take the biggest Q value (= the best action)
            action = np.argmax(Qs)
                    
        return action, explore_probability
    
    def get_Qs(self, next_states_mb, sess):
        # Get Q values given a mini-batch of states
        return sess.run(self.output, feed_dict={self.inputs_: next_states_mb})
    
    def get_loss(self, states_mb, targets_mb, actions_mb, sess):
        # Return loss value for given mini-batch
        return sess.run([self.loss, self.optimizer],
                        feed_dict={self.inputs_: states_mb,
                                   self.target_Q: targets_mb,
                                   self.actions_: actions_mb})
    
    def write(self, episode, states_mb, targets_mb, actions_mb, sess):
        # Write summary to tensorboard
        summary = sess.run(self.write_op, feed_dict={self.inputs_: states_mb,
                                               self.target_Q: targets_mb,
                                               self.actions_: actions_mb})
        self.writer.add_summary(summary, episode)
        self.writer.flush()
        
    def save(self, sess, path):
        # Save the model to file
        self.saver.save(sess, path)
        
    def restore(self, sess, path):
        # Restore the model from file
        self.saver.restore(sess, path)

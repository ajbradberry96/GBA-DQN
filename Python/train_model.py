# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 12:02:42 2019

Main logic for training DQN model.

@author: Moosnum2
"""

import dqn_server
import preprocessor
import agent as a
import numpy as np
import tensorflow as tf
import time as t

WATCH_ME = True
# So we can time how long training takes...
start = t.time()
# Number of actions available to our agent
N_ACTIONS = 4
# Number of frames per stack
N_FRAMES = 4
# Number of episodes to train
TRAIN_LEN = 300
# Maximum number of steps in any given episode
MAX_SESS = 10000
# Training batch size
BATCH_SIZE = 64
GAMMA = .95

if WATCH_ME:
    agent = a.Agent(N_ACTIONS, "../Memories/mem.pkl")
else:
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

for i in range(BATCH_SIZE + 1):
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
        
    # Random action, since we're just filling memory
    action = np.random.randint(0, N_ACTIONS)
    
    # Get the rewards and next state
    server.send_action(action)
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

# Initialize loss to 1 (ARBITRARY, CHANGE LATER?)
loss = 1.0
# Train it
with tf.Session() as sess:
    # Initialize the variables
    sess.run(tf.global_variables_initializer())
    
    # Initialize the decay rate (that will use to reduce epsilon) 
    decay_step = 0

    # Init the game
    server.restart()

    for episode in range(TRAIN_LEN):
        # Set step to 0
        step = 0
        
        # Initialize the rewards of the episode
        episode_rewards = []
        
        # Make a new episode and observe the first state
        frames, score, game_over = server.get_state()
        stack = prep.stack_frames(frames)

        while step < MAX_SESS:
            if step != 0:
                agent.add_memory((stack, action, reward, new_stack, new_game_over))
                frames, score, game_over = new_frames, new_score, new_game_over
            
            step += 1
            
            # Increase decay_step
            decay_step += .15
            
            # Predict the action to take and take it
            action, explore_probability = agent.predict_action(decay_step, stack, sess)

            # Get the rewards
            server.send_action(action)
            new_frames, new_score, new_game_over = server.get_state()
            new_stack = prep.stack_frames(new_frames)
            
            if new_game_over:
                end_score = -10
            else:
                end_score = -.01
            reward = ((new_score - score) / 10 + end_score) / 100
            
            # Add the reward to total reward
            episode_rewards.append(reward)

            # If the game is finished
            if new_game_over:
                # the episode ends so no next state
                next_state = np.zeros(stack.shape)

                # Set step = max_steps to end the episode
                step = MAX_SESS

                # Get the total reward of the episode
                total_reward = np.sum(episode_rewards)

                print('Episode: {}'.format(episode),
                          'Total reward: {:.4f}'.format(total_reward),
                          'Training loss: {:.4f}'.format(loss),
                          'Explore P: {:.4f}'.format(explore_probability),
                          'End score: {}'.format(new_score))

                agent.add_memory((stack, action, reward, next_state, new_game_over))
                
                server.restart()


        ### LEARNING PART            
        # Obtain random mini-batch from memory
        batch = agent.memory_sample(BATCH_SIZE)
        states_mb = np.array([each[0] for each in batch], ndmin=3)
        actions_mb = [[0,0,0,0] for _ in range(BATCH_SIZE)]
        for i, each in enumerate(batch):
            actions_mb[i][each[1]] = 1
        #actions_mb = np.array([each[1] for each in batch])
        rewards_mb = np.array([each[2] for each in batch]) 
        next_states_mb = np.array([each[3] for each in batch], ndmin=3)
        dones_mb = np.array([each[4] for each in batch])

        target_Qs_batch = []

         # Get Q values for next_state 
        Qs_next_state = agent.get_Qs(next_states_mb, sess)
        
        # Set Q_target = r if the episode ends at s+1, otherwise set Q_target = r + gamma*maxQ(s', a')
        for i in range(0, len(batch)):
            terminal = dones_mb[i]

            # If we are in a terminal state, only equals reward
            if terminal:
                target_Qs_batch.append(rewards_mb[i])
                
            else:
                target = rewards_mb[i] + GAMMA * np.max(Qs_next_state[i])
                target_Qs_batch.append(target)
                

        targets_mb = np.array([each for each in target_Qs_batch])
        
        # CHECK THIS
        loss, _ = agent.get_loss(states_mb, targets_mb, actions_mb, sess)

        # Write TF Summaries
        agent.write(episode, states_mb, targets_mb, actions_mb, sess)

        # Save model every 5 episodes
        if episode % 5 == 0:
            agent.save(sess, "./models/model2.ckpt")
            print("Model Saved")

# Close the connection            
server.close()

# How long did that take? (Really friggen long, amirite?)
print("Took", t.time() - start, "seconds.")
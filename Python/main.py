# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 12:02:42 2019

@author: Moosnum2
"""

import dqn_server

server = dqn_server.Server()
for _ in range(100):
    frames, score, game_over = server.get_state()
    for i in range(4):
        frames.get()
    
    server.send_action("1000")
server.close()

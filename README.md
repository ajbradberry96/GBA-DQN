# GBA-DQN

A standard DQN being designed to be able to play any GBA game, currently setting up to play the original Mario Bros. from the cartridge Super Mario Advance 4.

# Setup

Download this Repo

Install Bizhawk from here: http://tasvideos.org/Bizhawk.html

Place all of the resulting files in Emulation/ folder.

Place a ROM of Super Mario Advance 4 with filename "SMA4.gba" into the Emulation/ROMs/ folder.

Download LuaSocket from here: http://w3.impa.br/~diego/software/luasocket/installation.html

Arrange LuaSocket in the manner described here with Emulation being the root directory: https://stackoverflow.com/questions/33428382/add-luasocket-to-program-bizhawk-shipped-with-own-lua-environment

In BizHawk, go to Config/Customization/Advanced and change the lua core to LuaInterface. Restart Bizhawk.

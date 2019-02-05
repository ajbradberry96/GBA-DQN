local tcp = require("socket").tcp()
local receive_buffer = ""
local message = ""
local success, error = tcp:connect('localhost', 36296)

-- Number of frames in a stack
local num_frames = 4

memory.usememorydomain("IWRAM")

if not success then
  print("Failed to connect to server:", error)
  return
end

client.setscreenshotosd(false)
tcp:send("Connected to GBA.")

tcp:settimeout(.003)

message, error, receive_buffer = tcp:receive("*l", receive_buffer)
print(receive_buffer)

-- Let the server know how many frames in a stack
tcp:send(num_frames)

function restart()
  -- Set the game state to the starting position
  savestate.load("./GBA/State/begin.State")
  tcp:send("restarted")
end

function send_state()
  -- Send state of game
  -- i. Screenshots
  for i=1, num_frames do
    emu.frameadvance() 
    client.screenshot("../States/frame" .. i .. ".png")
  end

  -- ii. Score
  score = memory.read_u32_le(0x3DE4)
  
  -- iii. Game over?
  game_over = memory.read_u8(0x5C0B)

  -- Send in format score,game_over
  tcp:send(tostring(score).. "," .. tostring(game_over))
  receive_buffer = ""
  message, error, receive_buffer = tcp:receive("*l", receive_buffer)
  if tostring(receive_buffer) ~= "State received." then
    print("Error receiving frames") 
    print(receive_buffer)
    return
  end

  tcp:send("Finished sending state")
end

function receive_action()
  -- Receive an action from the server in Input Log form
  tcp:send("ready")
  receive_buffer = ""
  message, error, receive_buffer = tcp:receive("*l", receive_buffer)

  -- Set that action as the action for the next frame
  joypad.setfrommnemonicstr(receive_buffer)
  tcp:send("action received")
end

function send_action()
  -- Send an action to the server in table form
  buttons = joypad.get()
  if buttons['A'] == true then tcp:send('0')
  elseif buttons['Left'] == true then tcp:send('1')
  elseif buttons['Right'] == true then tcp:send('2')
  else tcp:send('3')
  end
end

function close()
  -- Close TCP connection and set game running forever so BizHawk can be closed
  print("closing...")
  tcp:close()
  while true do emu.frameadvance() end
end

while true do
  -- Receive command from server and run it.
  receive_buffer = ""
  message, error, receive_buffer = tcp:receive("*l", receive_buffer)
  command = tostring(receive_buffer)
  if command == "restart" then restart() end
  if command == "send state" then send_state() end
  if command == "receive action" then receive_action() end
  if command == "send action" then send_action() end
  if command == "close" then close() end
end
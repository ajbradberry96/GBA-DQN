local tcp = require("socket").tcp()
local receive_buffer = ""
local message = ""
local success, error = tcp:connect('localhost', 36296)
--Number of frames in a stack
local num_frames = 4

memory.usememorydomain("IWRAM")

if not success then
  print("Failed to connect to server:", error)
  return
end

client.setscreenshotosd(false)
tcp:send("Connected to GBA.")

tcp:settimeout(.005)

message, error, receive_buffer = tcp:receive("*l", receive_buffer)
print(receive_buffer)

--Let the server know how many frames in a stack
tcp:send(num_frames)

function restart()
  savestate.load("./GBA/State/begin.State")
  tcp:send("restarted")
end

function send_state()
  --Send state of game
  --i. Screenshots
  for i=1, num_frames do
    emu.frameadvance() 
    client.screenshot("../States/frame" .. i .. ".png")
  end

  --ii. Score
  score = memory.read_u32_le(0x3DE4)
  
  --iii. Game over?
  game_over = memory.read_u8(0x5C0B)

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
  tcp:send("ready")

  receive_buffer = ""
  message, error, receive_buffer = tcp:receive("*l", receive_buffer)
  joypad.setfrommnemonicstr(receive_buffer)
  tcp:send("action received")
end

function close()
  print("closing...")
  tcp:close()
  while true do emu.frameadvance() end
end

while true do
  --print(joypad.get())
  receive_buffer = ""
  message, error, receive_buffer = tcp:receive("*l", receive_buffer)
  command = tostring(receive_buffer)
  if command == "restart" then restart() end
  if command == "send state" then send_state() end
  if command == "receive action" then receive_action() end
  if command == "close" then close() end
end
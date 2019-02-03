local tcp = require("socket").tcp()
local receive_buffer = ""
local message = ""
local success, error = tcp:connect('localhost', 36296)
--Number of frames in a stack
local num_frames = 4

if not success then
  print("Failed to connect to server:", error)
  return
end

client.setscreenshotosd(false)
tcp:send("Connected to GBA.")

tcp:settimeout(.015)

message, error, receive_buffer = tcp:receive("*a", receive_buffer)
print(receive_buffer)

--Let the server know how many frames in a stack
tcp:send(num_frames)

--Start game
savestate.load("./GBA/State/begin.State")

while true do
  --Send state of game

  --i. Screenshots
  for i=1, num_frames do
    emu.frameadvance() 
    client.screenshot("../States/frame" .. i .. ".png")
  end
  
  --ii. Score

  --iii. Game over?

  tcp:send("State captured.")
  receive_buffer = ""
  message, error, receive_buffer = tcp:receive("*a", receive_buffer)
  if tostring(receive_buffer) ~= "Frames received." then
    print("Error receiving frames") 
    print(receive_buffer)
  end
  --tcp:send(score)
  --message, error, receive_buffer = tcp:receive("*a", receive_buffer)
  --tcp.send(game_over)

  --Receive next action
  --message, error, receive_buffer = tcp:receive("*a", receive_buffer)
  --print(receive_buffer)


  --Apply action to game


  --Advance game state or reset game if over
  

end
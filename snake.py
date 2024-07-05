import sys
import time
import random
import math

if sys.implementation.name == "micropython":
    from pimoroni_i2c import PimoroniI2C
    from pimoroni import HEADER_I2C_PINS
    # from breakout_encoder import BreakoutEncoder
    from breakout_encoder_wheel import BreakoutEncoderWheel, UP, DOWN, LEFT, RIGHT, CENTRE, NUM_LEDS
    from interstate75 import Interstate75, DISPLAY_INTERSTATE75_32X32
    i2c = PimoroniI2C(**HEADER_I2C_PINS)
    wheel = BreakoutEncoderWheel(i2c)

def cleari75(debugmode=True):
    if debugmode:
        print("Clearing Board...")
    graphics.set_pen(graphics.create_pen(0,0,0))
    graphics.clear()    # Clear board with current pen
    i75.update()
    return True

def drawLine(x,y,dir,r,g,b,debug=False):
    return True

def newFoodLocation():
    x = random.randint(1,30)
    y = random.randint(1,30)
    print(str(x) + ":" + str(y))
    return [x,y]

def initializei75(debugmode=True)->bool:
    global width
    global height
    global graphics
    global i75
    global BLUE
    global RED
    global BLACK
    global YELLOW
    
    print("  Initializing i75...")

    # if not debug and not sys.implementation.name == "micropython":
    if not sys.implementation.name == "micropython":
        print("i75 Board Required")
        return False
    
    i75 = Interstate75(display=DISPLAY_INTERSTATE75_32X32)
    graphics = i75.display
    width = i75.width
    height = i75.height

    BLACK = graphics.create_pen(0, 0, 0)
    BLUE = graphics.create_pen(0, 0, 255)
    RED = graphics.create_pen(255, 0, 0)
    YELLOW = graphics.create_pen(255,255,0)
    
    print("  Initialized")
    return True

# Draw border and food
def drawPlayfield(debugmode=True)->bool:
    # Draw border
    graphics.set_pen(BLUE)
#     graphics.line(0, 0, width, 0)
#     graphics.line(0, 0, 0, height)
#     graphics.line(height, width, 0, width-1)
#     graphics.line(height, width, height-1, 0)
    
    graphics.rectangle(0,0,32,32)
    graphics.set_pen(BLACK)
    graphics.rectangle(1,1,30,30)

    # Draw Food
    graphics.set_pen(RED)
    graphics.pixel(foodlocation[0], foodlocation[1])
    return True

def drawSnake(debugmode=True):
    global snakedata
    if snakeData == None:
        return False
    graphics.set_pen(YELLOW)
    lastdata = snakeData[0]
    for data in snakeData:        
        graphics.line(data[0],data[1],lastdata[0],lastdata[1])
        graphics.pixel(data[0],data[1])
        lastdata = data
    return True

def subListItems(a,b):
    ad = a[0]-b[0]
    bd = a[1]-b[1]
    return [ad,bd]

def move_a_towards_b(a, b, step_size=1.0):
    a = a[:]  # Create a copy of a to avoid modifying the original list
#     while a != b:
    # Step 1: Calculate the difference vector
    difference_vector = [b_i - a_i for a_i, b_i in zip(a, b)]
    
    # Step 2: Calculate the magnitude of the difference vector
    magnitude = math.sqrt(sum([component ** 2 for component in difference_vector]))
    
    if magnitude == 0:
        print("Equal")
        return -1
    else:
        print("Not equal")
    
    # Step 3: Normalize the difference vector to get the direction vector
    direction_vector = [component / magnitude for component in difference_vector]
    
    # Step 4: Move a towards b by adding the direction vector to a
    a = [a_i + direction_vector_i * step_size for a_i, direction_vector_i in zip(a, direction_vector)]
    
    # Round the coordinates to avoid floating-point arithmetic issues
    a = [round(coord) for coord in a]
    
    print(f'Moving to: {a}')  # Print the current position of a
    
    return a

def checkCollision(debug=True):
    global snakeData
    global snakeHeading
    
    # Check hitting wall
    print("Checking " + str(snakeData[-1]) + " for wall")
    if snakeData[-1][0]>31 or snakeData[-1][1]>31 or snakeData[-1][0]<1 or snakeData[-1][1]<1:
        print("Hit the wall at " + str(snakeData[-1]))
        return "WALL"
    
    # Check eating food
    if snakeData[-1] == foodlocation:
        print("Hit the food at " + foodlocation)
        return "FOOD"
    
    # Check hitting self
    # for segment in snake
    #  if head is in segment
    #	return "SELF"
        
    
    # If hit self
    # return "SELF"
    
    return 0

def moveSnake():
    global snakeHeading
    global snakeData
    
    snakeData[-1] = [snakeData[-1][0] + snakeHeading[0], snakeData[-1][1] + snakeHeading[1]]
    
    newA = move_a_towards_b(snakeData[0],snakeData[1])
    if newA == -1:
        snakeData.pop(0)
    else:
        snakeData[0] = newA
    print(snakeData[0])

def checkControls():
    global wheel
    global snakeHeading
    if wheel.pressed(UP):
        print("UP")
        snakeData.append(snakeData[-1])
        snakeHeading = [0,-1]
    if wheel.pressed(LEFT):
        print("LEFT")
        snakeData.append(snakeData[-1])
        snakeHeading = [-1,0]
    if wheel.pressed(RIGHT):
        print("RIGHT")
        snakeData.append(snakeData[-1])
        snakeHeading = [1,0]
    if wheel.pressed(DOWN):
        print("DOWN")
        snakeData.append(snakeData[-1])
        snakeHeading = [0,1]

    pass

    
if __name__ == "__main__":
#     debug = sys.argv.__contains__("debug")
#     print(sys.argv)
    debug=True

    # Game variables
    #foodlocation = [16,16]
    foodlocation = newFoodLocation()
    snakeData = [[15,5],[18,5],[18,10],[15,10],[15,20],[19,20],[19,19]] #,[12,19],[12,13]]
    #snakeData = [[16,16],[16,16]]
    snakeHeading = [0,-1]

    if debug:
        print("=== Snake RP2040 ===")

    if not initializei75(debug):
        print("Failure Setting Up Board; Exiting...")
        exit()
        
    cleari75(debug)
    
    print("Begining Game Loop")
    print(snakeData)
    
    while True:
#         cleari75(False)
        drawPlayfield(debug)
        drawSnake(debug)        
        i75.update()
        moveSnake()
        result = checkCollision()
        if result == "WALL":
            break
        checkControls()
        print(snakeData)
        time.sleep(0.2)

    print("DONE")


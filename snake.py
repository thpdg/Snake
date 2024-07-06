import sys
import time
import random
import math

if sys.implementation.name == "micropython":
    from pimoroni_i2c import PimoroniI2C
    from pimoroni import HEADER_I2C_PINS
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

def newFoodLocation(debug=False):
    global snakeData
    foodLoc = [0,0]
    foodLoc[0] = snakeData[-2][0]
    foodLoc[1] = snakeData[-2][1]
    while is_point_on_line_segments(snakeData, foodLoc):
        foodLoc[0] = random.randint(1,30)
        foodLoc[1] = random.randint(1,30)
    if debug: print("New food location: " + str(foodLoc[0]) + ":" + str(foodLoc[1]))
    return foodLoc

def initializei75(debugmode=True)->bool:
    global width
    global height
    global graphics
    global i75
    global BLUE
    global RED
    global LT_RED
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
    LT_RED = graphics.create_pen(128, 0, 0)
    YELLOW = graphics.create_pen(255,255,0)
    
    print("  Initialized")
    return True

# Draw border and food
def drawPlayfield(debugmode=True)->bool:
    # Draw border
    graphics.set_pen(BLUE)
    graphics.rectangle(0,0,32,32)

    # Draw playfield
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

def move_a_towards_b(a, b, step_size=1.0, debug=False):
    global growSnake
    
    if growSnake > 0:
        growSnake = growSnake - 1
        return a

    a = a[:]  # Create a copy of a to avoid modifying the original list
#     while a != b:
    # Step 1: Calculate the difference vector
    difference_vector = [b_i - a_i for a_i, b_i in zip(a, b)]
    
    # Step 2: Calculate the magnitude of the difference vector
    magnitude = math.sqrt(sum([component ** 2 for component in difference_vector]))
    
    if magnitude == 0:
        if debug:
            print("Equal")
        return -1
    else:
        if debug:
            print("Not equal")
    
    # Step 3: Normalize the difference vector to get the direction vector
    direction_vector = [component / magnitude for component in difference_vector]
    
    # Step 4: Move a towards b by adding the direction vector to a
    a = [a_i + direction_vector_i * step_size for a_i, direction_vector_i in zip(a, direction_vector)]
    
    # Round the coordinates to avoid floating-point arithmetic issues
    a = [round(coord) for coord in a]
    
    if debug:
        print(f'Moving to: {a}')  # Print the current position of a
    
    return a

def is_point_on_line_segments(vertexes, point):
    """Checks if the given point lies on any of the horizontal or vertical line segments defined by the array of vertexes"""
    n = len(vertexes)
    
    for i in range(n - 2):
        p1 = vertexes[i]
        p2 = vertexes[i + 1]
        
        if p1[0] == p2[0]:  # Vertical segment
            if point[0] == p1[0] and min(p1[1], p2[1]) <= point[1] <= max(p1[1], p2[1]):
                return True
        elif p1[1] == p2[1]:  # Horizontal segment
            if point[1] == p1[1] and min(p1[0], p2[0]) <= point[0] <= max(p1[0], p2[0]):
                return True
            
    return False

def checkCollision(debug=True):
    global snakeData
    global snakeHeading
    
    # Check hitting wall
    if debug:
        print("Checking " + str(snakeData[-1]) + " for wall")
    if snakeData[-1][0]>30 or snakeData[-1][1]>30 or snakeData[-1][0]<1 or snakeData[-1][1]<1:
        print("Hit the wall at " + str(snakeData[-1]))
        return "WALL"
    
    # Check eating food
    if snakeData[-1] == foodlocation:
        print("Hit the food at " + str(foodlocation))
        return "FOOD"
    
    # Check hitting self
    if is_point_on_line_segments(snakeData, snakeData[-1]):
        print("Hit Self " + str(snakeData[-1]))
        return "SELF"
    
    return 0

def moveSnake(debug=False):
    global snakeHeading
    global snakeData
    
    snakeData[-1] = [snakeData[-1][0] + snakeHeading[0], snakeData[-1][1] + snakeHeading[1]]
    
    newA = move_a_towards_b(snakeData[0],snakeData[1], 1.0, debug)
    if newA == -1:
        snakeData.pop(0)
    else:
        snakeData[0] = newA
    if debug:
        print(snakeData[0])

def checkControls(debug=False):
    global wheel
    global snakeHeading
    if wheel.pressed(UP):
        if debug: print("UP")
        snakeData.append(snakeData[-1])
        snakeHeading = [0,-1]
    if wheel.pressed(LEFT):
        if debug: print("LEFT")
        snakeData.append(snakeData[-1])
        snakeHeading = [-1,0]
    if wheel.pressed(RIGHT):
        if debug: print("RIGHT")
        snakeData.append(snakeData[-1])
        snakeHeading = [1,0]
    if wheel.pressed(DOWN):
        if debug: print("DOWN")
        snakeData.append(snakeData[-1])
        snakeHeading = [0,1]

    pass

def waitRestart():
    global wheel
    while True:
        if wheel.pressed(CENTRE):
            return True
    time.sleep(0.2)
    
def initializeSnake():
    global foodlocation
    global snakeData
    global snakeHeading
    global growSnake
    
    growSnake = 0
    snakeData = [[15,5],[18,5],[18,10],[15,10],[15,20],[19,20],[19,19]] #,[12,19],[12,13]]
    snakeHeading = [0,-1]
    foodlocation = newFoodLocation()

def displaySelfFail():
    drawPlayfield()
    graphics.set_pen(LT_RED)
    graphics.rectangle(1,1,30,30)
    drawSnake()
    #blink?
    i75.update()
    pass
    
if __name__ == "__main__":
#     debug = sys.argv.__contains__("debug")
#     print(sys.argv)
    debug=False

    # Game variables
    #foodlocation = [16,16]
#     foodlocation = newFoodLocation()
#     snakeData = [[15,5],[18,5],[18,10],[15,10],[15,20],[19,20],[19,19]] #,[12,19],[12,13]]
#     #snakeData = [[16,16],[16,16]]
#     snakeHeading = [0,-1]
    initializeSnake()

    if debug:
        print("=== Snake RP2040 ===")

    if not initializei75(debug):
        print("Failure Setting Up Board; Exiting...")
        exit()
        
    cleari75(debug)
    
    print("Begining Game Loop")
    print("Initial Snake Data: " + str(snakeData))
    
    while True:
#         cleari75(False)
        drawPlayfield(debug)
        checkControls()
        drawSnake(debug)        
        i75.update()
        moveSnake(debug)
        result = checkCollision(debug)
        if result == "WALL" or result == "SELF":
            displaySelfFail()
            waitRestart()
            initializeSnake()
        if result == "FOOD":
            growSnake = 5
            foodlocation = newFoodLocation()
        # if result == "SELF":
        #     displaySelfFail()
        #     waitRestart()
        #     initializeSnake()

        if debug:
            print(snakeData)
        time.sleep(0.2)

    print("DONE")


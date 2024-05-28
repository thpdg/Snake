import sys
import time
import random

if sys.implementation.name == "micropython":
    from pimoroni_i2c import PimoroniI2C
    from pimoroni import HEADER_I2C_PINS  # or PICO_EXPLORER_I2C_PINS or HEADER_I2C_PINS
    from breakout_encoder_wheel import BreakoutEncoderWheel, UP, DOWN, LEFT, RIGHT, CENTRE, NUM_LEDS
    from interstate75 import Interstate75, DISPLAY_INTERSTATE75_32X32

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

    BLUE = graphics.create_pen(0, 0, 255)
    RED = graphics.create_pen(255, 0, 0)
    YELLOW = graphics.create_pen(255,255,0)
    
    print("  Initialized")
    return True

# Draw border and food
def drawPlayfield(debugmode=True)->bool:
    # Draw border
    graphics.set_pen(BLUE)
    graphics.line(0, 0, width, 0)
    graphics.line(0, 0, 0, height)
    graphics.line(height, width, 0, width-1)
    graphics.line(height, width, height-1, 0)

    # Draw Food
    graphics.set_pen(RED)
    graphics.pixel(foodlocation[0], foodlocation[1])
    return True


if __name__ == "__main__":
#     debug = sys.argv.__contains__("debug")
#     print(sys.argv)
    debug=True

    # Game variables
    #foodlocation = [16,16]
    foodlocation = newFoodLocation()

    if debug:
        print("=== Snake RP2040 ===")

    if not initializei75(debug):
        print("Failure Setting Up Board; Exiting...")
        exit()
        
    cleari75(debug)
    
    print("Begining Game Loop")
    
    while True:
        # foodlocation = newFoodLocation()
        drawPlayfield(debug)
        i75.update()
        time.sleep(.2)

    print("DONE")


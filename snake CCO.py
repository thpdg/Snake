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

def cleari75(debug_mode=True):
    if debug_mode:
        print("Clearing Board...")
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.clear()
    i75.update()
    return True

def new_food_location(debug=False):
    global snake_data
    food_loc = [snake_data[-2][0], snake_data[-2][1]]
    while is_point_on_line_segments(snake_data, food_loc):
        food_loc = [random.randint(1, 30), random.randint(1, 30)]
    if debug:
        print(f"New food location: {food_loc[0]}:{food_loc[1]}")
    return food_loc

def initialize_i75(debug_mode=True) -> bool:
    global width, height, graphics, i75, BLUE, RED, LT_RED, BLACK, YELLOW

    print("Initializing i75...")

    if not sys.implementation.name == "micropython":
        print("i75 Board Required")
        return False
    
    i75 = Interstate75(display=DISPLAY_INTERSTATE75_32X32)
    graphics = i75.display
    width, height = i75.width, i75.height

    BLACK = graphics.create_pen(0, 0, 0)
    BLUE = graphics.create_pen(0, 0, 255)
    RED = graphics.create_pen(255, 0, 0)
    LT_RED = graphics.create_pen(128, 0, 0)
    YELLOW = graphics.create_pen(255, 255, 0)
    
    print("Initialized")
    return True

def draw_playfield(debug_mode=True) -> bool:
    graphics.set_pen(BLUE)
    graphics.rectangle(0, 0, 32, 32)

    graphics.set_pen(BLACK)
    graphics.rectangle(1, 1, 30, 30)

    graphics.set_pen(RED)
    graphics.pixel(food_location[0], food_location[1])
    return True

def draw_snake(debug_mode=True):
    global snake_data
    if snake_data is None:
        return False
    graphics.set_pen(YELLOW)
    last_data = snake_data[0]
    for data in snake_data:        
        graphics.line(data[0], data[1], last_data[0], last_data[1])
        graphics.pixel(data[0], data[1])
        last_data = data
    return True

def sub_list_items(a, b):
    return [a[0] - b[0], a[1] - b[1]]

def move_a_towards_b(a, b, step_size=1.0, debug=False):
    global grow_snake
    
    if grow_snake > 0:
        grow_snake -= 1
        return a

    a = a[:]  # Create a copy of a to avoid modifying the original list
    difference_vector = [b_i - a_i for a_i, b_i in zip(a, b)]
    magnitude = math.sqrt(sum([component ** 2 for component in difference_vector]))
    
    if magnitude == 0:
        if debug:
            print("Equal")
        return -1
    
    direction_vector = [component / magnitude for component in difference_vector]
    a = [a_i + direction_vector_i * step_size for a_i, direction_vector_i in zip(a, direction_vector)]
    a = [round(coord) for coord in a]
    
    if debug:
        print(f'Moving to: {a}')
    
    return a

def is_point_on_line_segments(vertexes, point):
    n = len(vertexes)
    
    for i in range(n - 2):
        p1, p2 = vertexes[i], vertexes[i + 1]
        
        if p1[0] == p2[0] and point[0] == p1[0] and min(p1[1], p2[1]) <= point[1] <= max(p1[1], p2[1]):
            return True
        elif p1[1] == p2[1] and point[1] == p1[1] and min(p1[0], p2[0]) <= point[0] <= max(p1[0], p2[0]):
            return True
            
    return False

def check_collision(debug=True):
    global snake_data, snake_heading
    
    if debug:
        print(f"Checking {snake_data[-1]} for wall")
    if snake_data[-1][0] > 30 or snake_data[-1][1] > 30 or snake_data[-1][0] < 1 or snake_data[-1][1] < 1:
        print(f"Hit the wall at {snake_data[-1]}")
        return "WALL"
    
    if snake_data[-1] == food_location:
        print(f"Hit the food at {food_location}")
        return "FOOD"
    
    if is_point_on_line_segments(snake_data, snake_data[-1]):
        print(f"Hit Self {snake_data[-1]}")
        return "SELF"
    
    return 0

def move_snake(debug=False):
    global snake_heading, snake_data
    
    snake_data[-1] = [snake_data[-1][0] + snake_heading[0], snake_data[-1][1] + snake_heading[1]]
    new_a = move_a_towards_b(snake_data[0], snake_data[1], 1.0, debug)
    if new_a == -1:
        snake_data.pop(0)
    else:
        snake_data[0] = new_a
    if debug:
        print(snake_data[0])

def check_controls(debug=False):
    global wheel, snake_heading
    if wheel.pressed(UP):
        if debug: print("UP")
        snake_data.append(snake_data[-1])
        snake_heading = [0, -1]
    if wheel.pressed(LEFT):
        if debug: print("LEFT")
        snake_data.append(snake_data[-1])
        snake_heading = [-1, 0]
    if wheel.pressed(RIGHT):
        if debug: print("RIGHT")
        snake_data.append(snake_data[-1])
        snake_heading = [1, 0]
    if wheel.pressed(DOWN):
        if debug: print("DOWN")
        snake_data.append(snake_data[-1])
        snake_heading = [0, 1]

def wait_restart():
    global wheel
    while True:
        if wheel.pressed(CENTRE):
            return True
        time.sleep(0.2)
    
def initialize_snake():
    global food_location, snake_data, snake_heading, grow_snake
    
    grow_snake = 0
    snake_data = [[15, 5], [18, 5], [18, 10], [15, 10], [15, 20], [19, 20], [19, 19]]
    snake_heading = [0, -1]
    food_location = new_food_location()

def display_self_fail():
    draw_playfield()
    graphics.set_pen(LT_RED)
    graphics.rectangle(1, 1, 30, 30)
    draw_snake()
    i75.update()

if __name__ == "__main__":
    debug = False

    initialize_snake()

    if debug:
        print("=== Snake RP2040 ===")

    if not initialize_i75(debug):
        print("Failure Setting Up Board; Exiting...")
        exit()
        
    cleari75(debug)
    
    print("Beginning Game Loop")
    print(f"Initial Snake Data: {snake_data}")
    
    while True:
        draw_playfield(debug)
        check_controls()
        draw_snake(debug)
        i75.update()
        move_snake(debug)
        result = check_collision(debug)
        if result in ["WALL", "SELF"]:
            display_self_fail()
            wait_restart()
            initialize_snake()
        elif result == "FOOD":
            grow_snake = 5
            food_location = new_food_location()

        if debug:
            print(snake_data)
        time.sleep(0.2)

    print("DONE")

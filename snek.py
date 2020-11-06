from luma.core.interface.serial import i2c, spi, pcf8574
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import sh1106
import RPi.GPIO as GPIO
import random

# Set these for your screen
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
SCREEN_X = 128
SCREEN_Y = 64

# Currently set for PTM switches. 
GPIO.setmode(GPIO.BCM)  
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# This is the current layout:
# Right: GPIO 20
# LEFT: GPIO 16
# DOWN: GPIO 12
# UP: GPIO 21


BLOCK_SIZE = 5

score = 0

class Food(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def set_pos(self,x,y):
        self.x = x
        self.y = y

class snake():
    def __init__(self):
        self.x = SCREEN_X/2
        self.y = SCREEN_Y/2
        self.tail = []
        self.direction = "R"
        self.speed = 2
    def move(self):
        if self.direction == "R":
            self.x += self.speed
        elif self.direction == "L":
            self.x -= self.speed
        elif self.direction == "U":
            self.y -= self.speed
        elif self.direction == "D":
            self.y += self.speed  
    def set_direction(self, direction):
        self.direction = direction   
    def set_pos(self,x,y):
        self.x = x
        self.y = y

def draw():
    with canvas(device, dither=True) as draw:
        draw.text((0, 0), f"Score:{score}", fill="white")
        # Draw Snake Head
        draw.rectangle((player.x, player.y, player.x+BLOCK_SIZE, player.y+BLOCK_SIZE), outline="white", fill="white")
        # Draw Snake Tail
        for seg in player.tail:
            draw.rectangle((seg[0], seg[1], seg[0]+BLOCK_SIZE, seg[1]+BLOCK_SIZE), outline="white", fill="white")
        # Draw Food
        draw.rectangle((food.x, food.y, food.x+BLOCK_SIZE, food.y+BLOCK_SIZE), outline="white", fill="red")
            
def game_over_screen():
    with canvas(device) as draw:
        draw.text((20, 15), "Game Over!", fill="white")
        draw.text((20, 25), f"Final Score: {score}", fill="white")
        draw.text((20, 45), f"L - Restart", fill="white")
        draw.text((20, 55), f"D - Exit", fill="white")

def main():
    global score
    global food
    global player
    game_over = False 
    while not game_over:
        if GPIO.input(20) and player.direction != "L":
            player.set_direction("R")
        elif GPIO.input(16) and player.direction != "R":
            player.set_direction("L")
        elif GPIO.input(21) and player.direction != "D":
            player.set_direction("U")
        elif GPIO.input(12) and player.direction != "U":
            player.set_direction("D")
        player.tail.append([player.x,player.y])
        if len(player.tail) > score:
            del player.tail[0]
        # Check food collision
        if (player.x < food.x+BLOCK_SIZE and player.x+BLOCK_SIZE > food.x and 
            player.y < food.y+BLOCK_SIZE and player.y+BLOCK_SIZE > food.y):
            food.set_pos(random.randrange(BLOCK_SIZE,SCREEN_X-BLOCK_SIZE),random.randrange(BLOCK_SIZE+10,SCREEN_Y-BLOCK_SIZE))
            score+=2
            print("YUMMY")
        for tail in player.tail[:-1]:
            if tail[0] == player.x and tail[1] == player.y:
                game_over = True
        player.move()
        draw()
        
serial = i2c(port=1, address=0x3C)
device = sh1106(serial)
player = snake()
food = Food(random.randrange(BLOCK_SIZE,SCREEN_X-BLOCK_SIZE),random.randrange(BLOCK_SIZE+10,SCREEN_Y-BLOCK_SIZE))

main()
exit_game = False
while not exit_game:
    game_over_screen()
    time.sleep(2)
    if GPIO.input(16):
        score = 0
        food.set_pos(random.randrange(0,100),random.randrange(0,50))
        player.set_pos(SCREEN_X/2,SCREEN_Y/2)
        player.tail = []
        main()
    elif GPIO.input(12):
        exit_game = True

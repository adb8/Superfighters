from pygame import *
import threading
import time as t

init()
screen = display.set_mode((1200, 800))
clock = time.Clock()

small_font = font.Font("freesansbold.ttf", 30)
big_font = font.Font("freesansbold.ttf", 100)
sound = mixer.Sound("sounds/gun-sound.mp3")

window_icon = image.load("images/crate.png")
display.set_icon(window_icon)
display.set_caption("superfighters")

class Player:
    def __init__(self, x, color):
        self.x = x
        self.y = 100
        self.color = color
        self.health = 100
        self.velocity = 0

        self.firing_state = False
        self.firing_direction = None
        self.fired_from_x = None
        self.fired_from_y = None
        self.last_time_fired = None

plr1 = Player(1100, "green")
plr2 = Player(50, "red")
plrs = [plr1, plr2]

floor_array = []
game_running = True
PLAYER_LENGTH = 50
FRAMES = 60

def draw_map_contents():
    global floor_array
    screen.fill("gray")
    ground = draw.rect(screen, "black", Rect(0, 650, 1200, 200))
    floora = draw.rect(screen, "black", Rect(100, 550, 300, 5))
    floorb = draw.rect(screen, "black", Rect(800, 550, 300, 5))
    floorc = draw.rect(screen, "black", Rect(400, 450, 400, 5))
    floord = draw.rect(screen, "black", Rect(0, 350, 300, 5))
    floore = draw.rect(screen, "black", Rect(900, 350, 300, 5))
    floorf = draw.rect(screen, "black", Rect(0, 150, 200, 5))
    floorg = draw.rect(screen, "black", Rect(1000, 150, 200, 5))
    floorh = draw.rect(screen, "black", Rect(200, 250, 800, 5))
    floor_array = [ground, floora, floorb, floorc, floord, floore, floorf, floorg, floorh]

def prevent_map_escape():
    for player in plrs:
        if player.x > 1200 - PLAYER_LENGTH:
            player.x = 1200 - PLAYER_LENGTH
        if player.x < 0:
            player.x = 0

def draw_players():
    for player in plrs:
        player_rect = Rect(player.x, player.y, PLAYER_LENGTH, PLAYER_LENGTH)
        draw.rect(screen, player.color, player_rect)

def move_player_and_handle_collision(player, direction):
    if not game_running:
        return
    direction_multiplier = 1
    if direction == "left":
        direction_multiplier = -1
        
    HORIZONTAL_INCREMENT = 10
    player.x += HORIZONTAL_INCREMENT * direction_multiplier

    rect = Rect(player.x, player.y, PLAYER_LENGTH, PLAYER_LENGTH)
    for item in floor_array:
        if Rect.colliderect(rect, item):
            player.x -= HORIZONTAL_INCREMENT * direction_multiplier

def handle_horizontal_movement():
    if holding_d and not holding_a:
        move_player_and_handle_collision(plr2, "right")
    if holding_a and not holding_d:
        move_player_and_handle_collision(plr2, "left")
    if holding_right and not holding_left:
        move_player_and_handle_collision(plr1, "right")
    if holding_left and not holding_right:
        move_player_and_handle_collision(plr1, "left")

def start_jump_action(plr):
    if plr.velocity == 0:
        plr.velocity = -23

def handle_jump_motion():
    if not game_running:
        return
    ACCELERATION = 2

    for player in plrs:
        player.velocity += ACCELERATION
        player.y += player.velocity

        for item in floor_array:
            rect = Rect(player.x, player.y, PLAYER_LENGTH, PLAYER_LENGTH)
            if Rect.colliderect(item, rect):
                if player.velocity > 0:
                    player.y = item.top - PLAYER_LENGTH
                    player.velocity = 0

def firing_state_timeout(): # exits fire state after 500 ms
    for player in plrs:
        if player.last_time_fired != None:
            current_time = int(round(t.time() * 1000))
            if current_time - player.last_time_fired >= 500:
                player.firing_state = False

def handle_gunfire_and_damage(plr):
    if plr.firing_state: # handle fire state
        return
    plr.firing_state = True
    global game_running
    bullet_path_hitbox = None
    target_hitbox = None

    plr.fired_from_x = plr.x
    plr.fired_from_y = plr.y

    current_time = int(round(t.time() * 1000))
    plr.last_time_fired = current_time
    mixer.Sound.play(sound)

    if plr == plr1: # determine shooter, target
        shooter = plr1
        target = plr2
    else:
        shooter = plr2
        target = plr1

    if shooter.x < target.x:
        bullet_path_hitbox = Rect(shooter.x + PLAYER_LENGTH/2, shooter.y + 22, 1200, 6) # obtain hitboxes
        target_hitbox = Rect(target.x, target.y, PLAYER_LENGTH, PLAYER_LENGTH)
        shooter.firing_direction = "right"
    else:
        bullet_path_hitbox = Rect(0, shooter.y + 22, shooter.x + PLAYER_LENGTH/2, 6)
        target_hitbox = Rect(target.x, target.y, PLAYER_LENGTH, PLAYER_LENGTH)
        shooter.firing_direction = "left"

    if Rect.colliderect(bullet_path_hitbox, target_hitbox): # if collision...
        target.health -= 30
        if target.health <= 0:
            target.health = 0
            display_game_over_animation(target)
            game_running = False

def draw_bullet():
    for player in plrs: # find bullet color
        if player == plr1:
            color = (150, 200, 150)
        else:
            color = (200, 150, 150)

        if player.firing_state:
            if player.firing_direction == "right":
                bullet_rect = Rect(player.fired_from_x + PLAYER_LENGTH/2, player.fired_from_y + 22, 1200, 6)
                draw.rect(screen, color, bullet_rect) # bullet going right
            else:
                bullet_rect = Rect(0, player.fired_from_y + 22, player.fired_from_x + PLAYER_LENGTH/2, 6)
                draw.rect(screen, color, bullet_rect) # bullet going left

def render_health_on_screen():
    plr2_health = str(plr2.health)
    plr1_health = str(plr1.health)
    plr2_health = small_font.render("health: "+plr2_health, True, "red")
    plr1_health = small_font.render("health: "+plr1_health, True, "green")
    screen.blit(plr2_health, (60, 720))
    screen.blit(plr1_health, (980, 720))

def display_game_over_animation(loser):
    ENDING_ANIMATION_VELOCITY = -15
    ENDING_ANIMATION_ACCELERATION = 2
    def fall_animation(vel, acc):
        loser.y += vel
        vel += acc
        if window_running:
            threading.Timer(0.02, fall_animation, [vel, acc]).start()
    fall_animation(ENDING_ANIMATION_VELOCITY, ENDING_ANIMATION_ACCELERATION)

def display_game_over_announcement():
    if game_running:
        return
        
    if plr1.health == 0:
        ending_message = big_font.render("red wins!", True, "red")
        screen.blit(ending_message, (370, 50))
    elif plr2.health == 0:
        ending_message = big_font.render("green wins!", True, "green")
        screen.blit(ending_message, (300, 50))

draw_map_contents()

holding_right, holding_left, holding_d, holding_a = False, False, False, False
window_running = True

while window_running:
    for e in event.get():
        if e.type == QUIT:
            window_running = False
        if e.type == KEYDOWN:
            if e.key == K_d:
                holding_d = True
            if e.key == K_a:
                holding_a = True
            if e.key == K_RIGHT:
                holding_right = True
            if e.key == K_LEFT:
                holding_left = True
            if e.key == K_UP:
                start_jump_action(plr1)
            if e.key == K_w:
                start_jump_action(plr2)
            if e.key == K_SLASH:
                handle_gunfire_and_damage(plr1)
            if e.key == K_e:
                handle_gunfire_and_damage(plr2)
        if e.type == KEYUP:
            if e.key == K_d:
                holding_d = False
            if e.key == K_a:
                holding_a = False
            if e.key == K_RIGHT:
                holding_right = False
            if e.key == K_LEFT:
                holding_left = False

    handle_horizontal_movement()
    prevent_map_escape()
    handle_jump_motion()
    draw_map_contents()
    draw_bullet()
    firing_state_timeout()
    display_game_over_announcement()
    render_health_on_screen()
    draw_players()

    clock.tick(FRAMES)
    display.update()

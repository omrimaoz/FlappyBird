import pygame
import random
import sys


def draw_floor():
    screen.blit(floor_surface, (floor_x_pos, 569))
    screen.blit(floor_surface, (floor_x_pos + 394, 569))


def creat_pipe():
    global Random_Pipe_Pos_Old
    random_pipe_pos_new = random.choice(pipe_height)
    while random_pipe_pos_new == Random_Pipe_Pos_Old:
        random_pipe_pos_new = random.choice(pipe_height)
    Random_Pipe_Pos_Old = random_pipe_pos_new
    bottom_pipe = pipe_surface.get_rect(midtop=(450, random_pipe_pos_new))
    top_pipe = pipe_surface.get_rect(midbottom=(450, random_pipe_pos_new - 170))

    return bottom_pipe, top_pipe


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 570:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)


def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            death_sound.play()
            return False
    if bird_rect.top <= -100 or bird_rect.bottom >= 580:
        return False
    return True


def rotate_bird(bird):
    new_bird = pygame.transform.rotozoom(bird, -bird_movement * 3, 1)
    return new_bird


def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(68, bird_rect.centery))
    return new_bird, new_bird_rect


def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(198, 68))
        screen.blit(score_surface, score_rect)
    if game_state == 'game_over':
        score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(198, 68))
        screen.blit(score_surface, score_rect)

        high_score_surface = game_font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(198, 168))
        screen.blit(high_score_surface, high_score_rect)


def update_score(curr_score, curr_high_score):
    if curr_score > curr_high_score:
        new_high_score = curr_score
    else:
        new_high_score = curr_high_score
    return new_high_score


pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=120)
pygame.init()

# screen = pygame.display.set_mode((576, 1024))
screen = pygame.display.set_mode((394, 700))
clock = pygame.time.Clock()
game_font = pygame.font.Font('04B_19.ttf', 40)

# Game Variables
gravity = 0.35
bird_movement = 0
game_active = False
score = 0
high_score = 0

bg_surface = pygame.image.load('assets/background.png').convert()
bg_surface = pygame.transform.scale(bg_surface, (394, 700))

floor_surface = pygame.image.load('assets/base.png').convert()
floor_surface = pygame.transform.scale(floor_surface, (394, 131))
floor_x_pos = 0

bird_downflap = pygame.image.load('assets/bluebird-downflap.png').convert_alpha()
bird_midflap = pygame.image.load('assets/bluebird-midflap.png').convert_alpha()
bird_upflap = pygame.image.load('assets/bluebird-upflap.png').convert_alpha()
bird_downflap = pygame.transform.scale(bird_downflap, (40, 28))
bird_midflap = pygame.transform.scale(bird_midflap, (40, 28))
bird_upflap = pygame.transform.scale(bird_upflap, (40, 28))
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center=(68, 350))

BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

pipe_surface = pygame.image.load('assets/pipe.png').convert()
pipe_surface = pygame.transform.scale(pipe_surface, (60, 330))
pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)
pipe_height = [240, 355, 470]
Random_Pipe_Pos_Old = 260
pipe_index = 0

game_over_surface = pygame.image.load('assets/message.png').convert_alpha()
game_over_rect = game_over_surface.get_rect(center=(197, 350))

flap_sound = pygame.mixer.Sound('sound/sfx_wing.wav')
death_sound = pygame.mixer.Sound('sound/sfx_hit.wav')
score_sound = pygame.mixer.Sound('sound/sfx_point.wav')
while True:
    # image of player 1
    # background image
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = 0
                bird_movement -= 8
                flap_sound.play()
            if event.key == pygame.K_SPACE and game_active == False:
                game_active = True
                pipe_list.clear()
                bird_rect.center = (68, 350)
                bird_movement = 0
                score = 0
                pipe_index = 0

        if event.type == SPAWNPIPE:
            pipe_list.extend(creat_pipe())

        if event.type == BIRDFLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0
            bird_surface, bird_rect = bird_animation()

    screen.blit(bg_surface, (0, 0))

    if game_active:
        # Bird
        bird_movement += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_movement
        screen.blit(rotated_bird, bird_rect)
        game_active = check_collision(pipe_list)
        # Pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
        if len(pipe_list) != 0:
            if 60 < pipe_list[pipe_index].centerx < 70:
                score += 1
                pipe_index += 2
                score_sound.play()
        score_display('main_game')
    else:
        screen.blit(game_over_surface, game_over_rect)
        high_score = update_score(score, high_score)
        score_display('game_over')

    # Floor
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -394:
        floor_x_pos = 0

    pygame.display.update()
    clock.tick(120)

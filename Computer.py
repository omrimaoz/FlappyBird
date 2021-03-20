# imports
import neat
import os
import pygame
import random

pygame.font.init()

# GAME SETUP
WIN_WIDTH = 394
WIN_HEIGHT = 700
GEN = 0

# IMAGES
bird_downflap = pygame.image.load('assets/bluebird-downflap.png')
bird_midflap = pygame.image.load('assets/bluebird-midflap.png')
bird_upflap = pygame.image.load('assets/bluebird-upflap.png')

bird_downflap = pygame.transform.scale(bird_downflap, (40, 28))
bird_midflap = pygame.transform.scale(bird_midflap, (40, 28))
bird_upflap = pygame.transform.scale(bird_upflap, (40, 28))
BIRD_IMGS = [bird_downflap, bird_midflap, bird_upflap]

PIPE_IMG = pygame.image.load('assets/pipe.png')
PIPE_IMG = pygame.transform.scale(PIPE_IMG, (60, 330))

BG_IMG = pygame.image.load('assets/background.png')
BG_IMG = pygame.transform.scale(BG_IMG, (394, 700))

BASE_IMG = pygame.image.load('assets/base.png')
BASE_IMG = pygame.transform.scale(BASE_IMG, (394, 131))

# FONT
game_font = pygame.font.Font('04B_19.ttf', 40)


# Define properties of one bird in the game
class Bird:
    IMGS = BIRD_IMGS  # List of bird flaps images
    MAX_ROTATION = 25
    ROT_VEL = 3
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -9
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        d = self.vel + 0.50 * self.tick_count  # Accelerating speed
        if d >= 16:  # Speed limit
            d = 16
        if d < 0:
            d -= 2
        self.y = self.y + d  # Update vertical position
        if d < -2:  # Update tilt of the bird
            if self.tilt < self.MAX_ROTATION:  # Rotation limit
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -60:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # Change bird flaps images to create a fluent move
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # When free fall dont flap wings
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)  # Present details to screen

    # Return rectangle area around bird object
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


# Define properties of one pipe in the game
class Pipe:
    GAP = 170
    VEL = 5

    def __init__(self, x, before_height, counter):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.xGap = False
        self.before_height = before_height
        self.counter = counter
        self.set_height()

    def set_height(self):
        # Define different heights for the pipes
        if self.counter % 3 == 0:
            self.height = random.randrange(75, 320)
        elif self.before_height < 200:
            self.height = random.randrange(260, 320)
        else:
            self.height = random.randrange(75, 150)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL  # Pipes are moving to the left

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))  # Present details to screen
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))  # Present details to screen

    def collide(self, bird):
        # Define collision of the bird with a pipe
        bird_mask = bird.get_mask()  # Rectangle around bird current position
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)  # Rectangle around pipe current position
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)  # Rectangle around pipe current position

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False


# Define properties of base (surface) for the game
class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):  # Base moving to the left to create illusion of the bird moving forward in the game
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        # Draw 2 base images one after the other to create continuity of the surface while moving to the left
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


# Present real-time information of the game to the screen
# Score:
def score_display(game_state, win, score):
    if game_state == 'main_game':
        score_surface = game_font.render("Score: " + str(int(score)), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(270, 128))
        win.blit(score_surface, score_rect)


# Number of the generation in the AI algorithm
def gen_display(game_state, win, gen):
    if game_state == 'main_game':
        gen_surface = game_font.render("Generation: " + str(int(gen)), True, (255, 255, 255))
        gen_rect = gen_surface.get_rect(center=(250, 28))
        win.blit(gen_surface, gen_rect)


# Number of birds still alive from the start-up population
def size_display(game_state, win, size):
    if game_state == 'main_game':
        size_surface = game_font.render("Birds Alive: " + str(int(size)), True, (255, 255, 255))
        size_rect = size_surface.get_rect(center=(250, 78))
        win.blit(size_surface, size_rect)


# Function to define all the details making the game window
def draw_window(win, birds, pipes, base, score, gen, size):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    score_display("main_game", win, score)
    gen_display("main_game", win, gen)
    size_display("main_game", win, size)
    base.draw(win)

    # Draw all the birds alive in the population
    for bird in birds:
        bird.draw(win)

    # Update game window
    pygame.display.update()


# Main function to integrate game variables and methods
def main(genomes, config):
    # AI algorithm and game support variable
    global GEN
    GEN += 1  # Generation counter
    nets = []
    ge = []  # Generation list
    birds = []  # Birds list
    base = Base(570)  # Define base object
    pipes = [Pipe(500, 0, 0)]  # Define first pipe object (in a list of pipes)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    # initialize first bird and fitness properties
    for _, g in genomes:  # Genomes is a list of tuples so we need only the second value in the tuples
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(70, 330))
        g.fitness = 0
        ge.append(g)

    # Game loop
    run = True
    while run:
        clock.tick(90)

        # Define x to close game and game window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0  #
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        # On each bird of the population define:
        for x, bird in enumerate(birds):
            bird.move()  # Update bird location
            ge[x].fitness += 0.1  # Fit the bird object

            # Calculate when to jump
            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        add_score = False
        rem = []

        # On each pipe object define:
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1  # Subtract from fitness score
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                # Define condition to remove pipe from pipes (list)
                if not pipe.xGap and pipe.x - 130 < bird.x:
                    pipe.xGap = True
                    add_pipe = True
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_score = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()
        if add_score:
            score += 1
        if add_pipe:
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(500, pipes[-1].height, score))
        for r in rem:
            pipes.remove(r)

        # Bird collide with sky or surface (reminder - sky = 0)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 570 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        # Game window update
        base.move()
        draw_window(win, birds, pipes, base, score, GEN, len(birds))


# AI algorithm init and import configuration
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run main methode
    winner = p.run(main, 50)


# On running this module:
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)

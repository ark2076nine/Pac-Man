# CHANGES TO MAKE
# One of the ghosts isn't working properly, fix it
# Make sure when get the powerup, the ghosts run away from you
# Make the map a bit smaller
# Find a way to create a score counter

import pygame
import random
import math

pygame.init()

TILE_SIZE = 16
COLS = 28
ROWS = 31
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE + 40

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

MAZE_LAYOUT = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#O####.#####.##.#####.####O#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "######.##### ## #####.######",
    "######.##          ##.######",
    "######.## ###--### ##.######",
    "######.## #      # ##.######",
    "      .   #      #   .      ",
    "######.## #      # ##.######",
    "######.## ######## ##.######",
    "######.##          ##.######",
    "######.## ######## ##.######",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#O..##.......  .......##..O#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################"
]

class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.paused = False
        self.pellets_remaining = 0
        self.fright_timer = 0

game_state = GameState()

class Maze:
    def __init__(self):
        self.init_maze()

    def init_maze(self):
        self.grid = []
        self.pellets = []
        self.power_pellets = []

        for row, line in enumerate(MAZE_LAYOUT):
            grid_row = []
            for col, char in enumerate(line):
                grid_row.append(char)
                if char == ".":
                    self.pellets.append((col, row))
                elif char == "O":
                    self.power_pellets.append((col, row))
            self.grid.append(grid_row)

        game_state.pellets_remaining = len(self.pellets) + len(self.power_pellets)

    def is_wall(self, x, y):
        if y < 0 or y >= ROWS or x < 0 or x >= COLS:
            return False
        return self.grid[y][x] == "#"

    def is_door(self, x, y):
        if y < 0 or y >= ROWS or x < 0 or x >= COLS:
            return False
        return self.grid[y][x] == "-"

    def draw(self):
        for row in range(ROWS):
            for col in range(COLS):
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                tile = self.grid[row][col]

                if tile == "#":
                    pygame.draw.rect(screen, BLUE, (x, y, TILE_SIZE, TILE_SIZE))
                elif tile == "-":
                    pygame.draw.rect(screen, WHITE, (x + 2, y + TILE_SIZE // 2 - 1, TILE_SIZE - 4, 2))

        for px, py in self.pellets:
            pygame.draw.circle(
                screen,
                WHITE,
                (px * TILE_SIZE + TILE_SIZE // 2, py * TILE_SIZE + TILE_SIZE // 2),
                2
            )

        pulse = 4 + int(abs(math.sin(pygame.time.get_ticks() / 150)) * 2)
        for px, py in self.power_pellets:
            pygame.draw.circle(
                screen,
                WHITE,
                (px * TILE_SIZE + TILE_SIZE // 2, py * TILE_SIZE + TILE_SIZE // 2),
                pulse
            )

class Player:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.speed = 0.11
        self.mouth = 0
        self.mouth_dir = 1
        self.reset()

    def reset(self):
        self.pos_x = self.start_x + 0.5
        self.pos_y = self.start_y + 0.5
        self.dir_x = 1
        self.dir_y = 0
        self.next_dir_x = 1
        self.next_dir_y = 0
        self.powered = False
        self.power_timer = 0

    def can_move(self, x, y, maze):
        corners = [
            (x - 0.35, y - 0.35),
            (x + 0.35, y - 0.35),
            (x - 0.35, y + 0.35),
            (x + 0.35, y + 0.35),
        ]
        for px, py in corners:
            if maze.is_wall(int(px), int(py)) or maze.is_door(int(px), int(py)):
                return False
        return True

    def update(self, maze):
        if self.powered:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.powered = False
                game_state.fright_timer = 0

        nx = self.pos_x + self.next_dir_x * self.speed
        ny = self.pos_y + self.next_dir_y * self.speed
        if self.can_move(nx, ny, maze):
            self.dir_x = self.next_dir_x
            self.dir_y = self.next_dir_y

        nx = self.pos_x + self.dir_x * self.speed
        ny = self.pos_y + self.dir_y * self.speed
        if self.can_move(nx, ny, maze):
            self.pos_x = nx
            self.pos_y = ny

        if self.pos_x < -0.5:
            self.pos_x = COLS - 0.5
        elif self.pos_x > COLS - 0.5:
            self.pos_x = -0.5

        self.collect_pellets(maze)

        self.mouth += 0.12 * self.mouth_dir
        if self.mouth > 1:
            self.mouth = 1
            self.mouth_dir = -1
        elif self.mouth < 0:
            self.mouth = 0
            self.mouth_dir = 1

    def collect_pellets(self, maze):
        for pellet in maze.pellets[:]:
            if math.hypot(self.pos_x - (pellet[0] + 0.5), self.pos_y - (pellet[1] + 0.5)) < 0.45:
                maze.pellets.remove(pellet)
                game_state.score += 10
                game_state.pellets_remaining -= 1

        for pellet in maze.power_pellets[:]:
            if math.hypot(self.pos_x - (pellet[0] + 0.5), self.pos_y - (pellet[1] + 0.5)) < 0.45:
                maze.power_pellets.remove(pellet)
                game_state.score += 50
                game_state.pellets_remaining -= 1
                self.powered = True
                self.power_timer = 360
                game_state.fright_timer = 360

    def draw(self):
        px = int(self.pos_x * TILE_SIZE)
        py = int(self.pos_y * TILE_SIZE)
        r = int(TILE_SIZE * 0.45)

        pygame.draw.circle(screen, YELLOW, (px, py), r)

        angle = math.atan2(self.dir_y, self.dir_x)
        mouth_size = 0.75 * self.mouth + 0.15

        p1 = (px, py)
        p2 = (
            px + int(math.cos(angle + mouth_size) * r * 1.2),
            py + int(math.sin(angle + mouth_size) * r * 1.2),
        )
        p3 = (
            px + int(math.cos(angle - mouth_size) * r * 1.2),
            py + int(math.sin(angle - mouth_size) * r * 1.2),
        )

        pygame.draw.polygon(screen, BLACK, [p1, p2, p3])

class Enemy:
    def __init__(self, x, y, color, personality, release_delay=0):
        self.home_x = x
        self.home_y = y
        self.color = color
        self.personality = personality
        self.scatter_target = (x, y)
        self.speed = 0.09
        self.release_delay = release_delay
        self.reset()

    def reset(self):
        self.pos_x = self.home_x + 0.5
        self.pos_y = self.home_y + 0.5
        self.dir_x = 0
        self.dir_y = -1
        self.frightened = False
        self.eaten = False
        self.wait_timer = self.release_delay
        self.leaving_home = True

    def frighten(self):
        if not self.eaten:
            self.frightened = True
            self.dir_x *= -1
            self.dir_y *= -1

    def tile_pos(self):
        return int(self.pos_x), int(self.pos_y)

    def at_center(self):
        return (
            abs(self.pos_x - (int(self.pos_x) + 0.5)) < 0.08 and
            abs(self.pos_y - (int(self.pos_y) + 0.5)) < 0.08
        )

    def can_move(self, x, y, maze):
        tx, ty = int(x), int(y)

        if ty < 0 or ty >= ROWS or tx < 0 or tx >= COLS:
            return True

        if maze.is_wall(tx, ty):
            return False

        if maze.is_door(tx, ty):
            return self.eaten or self.leaving_home

        return True

    def get_target(self, player):
        if self.eaten:
            return (13.5, 11.5)

        if self.frightened:
            dx = self.pos_x - player.pos_x
            dy = self.pos_y - player.pos_y
            length = math.hypot(dx, dy) or 1
            return (
                self.pos_x + (dx / length) * 8,
                self.pos_y + (dy / length) * 8
            )

        if self.personality == "CHASER":
            return (player.pos_x, player.pos_y)
        if self.personality == "AMBUSHER":
            return (player.pos_x + player.dir_x * 4, player.pos_y + player.dir_y * 4)
        if self.personality == "FLANKER":
            return (player.pos_x - player.dir_y * 4, player.pos_y + player.dir_x * 4)

        return (player.pos_x, player.pos_y) if random.random() < 0.7 else self.scatter_target

    def choose_direction(self, player, maze):
        target = self.get_target(player)
        reverse = (-self.dir_x, -self.dir_y)
        options = []

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            if (dx, dy) == reverse:
                continue

            nx = self.pos_x + dx
            ny = self.pos_y + dy

            if self.can_move(nx, ny, maze):
                tx = int(nx)
                ty = int(ny)
                dist = (tx + 0.5 - target[0]) ** 2 + (ty + 0.5 - target[1]) ** 2
                options.append((dist, dx, dy))

        if not options:
            if self.can_move(self.pos_x + reverse[0], self.pos_y + reverse[1], maze):
                self.dir_x, self.dir_y = reverse
            return

        options.sort(key=lambda item: item[0], reverse=self.frightened and not self.eaten)
        _, self.dir_x, self.dir_y = options[0]

    def update(self, player, maze):
        if self.frightened and game_state.fright_timer <= 0:
            self.frightened = False

        if self.eaten:
            door_target_x, door_target_y = 13.5, 11.5
            if math.hypot(self.pos_x - door_target_x, self.pos_y - door_target_y) < 0.5:
                self.eaten = False
                self.frightened = False
                self.wait_timer = 20
                self.leaving_home = True
                self.pos_x = self.home_x + 0.5
                self.pos_y = self.home_y + 0.5
                self.dir_x = 0
                self.dir_y = -1

        move_speed = 0.06 if self.frightened else (0.15 if self.eaten else self.speed)

        if self.wait_timer > 0 and not self.eaten:
            self.wait_timer -= 1
            return

        # leave the ghost house by forcing upward movement through the door
        if self.leaving_home and not self.eaten:
            self.dir_x = 0
            self.dir_y = -1
            nx = self.pos_x
            ny = self.pos_y - move_speed

            if self.can_move(nx, ny, maze):
                self.pos_y = ny

            if self.pos_y <= 11.5:
                self.leaving_home = False
                self.pos_y = 11.5
            return

        if self.at_center():
            self.choose_direction(player, maze)

        nx = self.pos_x + self.dir_x * move_speed
        ny = self.pos_y + self.dir_y * move_speed

        if self.can_move(nx, ny, maze):
            self.pos_x = nx
            self.pos_y = ny
        else:
            if self.at_center():
                self.choose_direction(player, maze)

        if self.pos_x < -0.5:
            self.pos_x = COLS - 0.5
        elif self.pos_x > COLS - 0.5:
            self.pos_x = -0.5

    def draw(self):
        px = int(self.pos_x * TILE_SIZE)
        py = int(self.pos_y * TILE_SIZE)
        radius = int(TILE_SIZE * 0.42)

        color = BLUE if self.frightened and not self.eaten else self.color
        if self.eaten:
            color = WHITE

        pygame.draw.circle(screen, color, (px, py), radius)

        if not self.eaten:
            eye_r = 2
            pygame.draw.circle(screen, WHITE, (px - 4, py - 2), eye_r + 1)
            pygame.draw.circle(screen, WHITE, (px + 4, py - 2), eye_r + 1)
            pygame.draw.circle(screen, BLACK, (px - 4 + self.dir_x, py - 2 + self.dir_y), eye_r)
            pygame.draw.circle(screen, BLACK, (px + 4 + self.dir_x, py - 2 + self.dir_y), eye_r)

def check_collisions(player, enemies):
    for enemy in enemies:
        if math.hypot(player.pos_x - enemy.pos_x, player.pos_y - enemy.pos_y) < 0.7:
            if enemy.frightened and not enemy.eaten:
                enemy.eaten = True
                enemy.frightened = False
                game_state.score += 200
            elif not enemy.eaten:
                return True
    return False

def reset_positions(player, enemies):
    player.reset()
    for enemy in enemies:
        enemy.reset()
    game_state.fright_timer = 0

def lose_life(player, enemies):
    game_state.lives -= 1
    if game_state.lives <= 0:
        game_state.game_over = True
    else:
        reset_positions(player, enemies)

def next_level(maze, player, enemies):
    game_state.level += 1
    maze.init_maze()
    reset_positions(player, enemies)
    player.speed = min(0.14, player.speed + 0.005)
    for enemy in enemies:
        enemy.speed = min(0.12, enemy.speed + 0.004)

def update_timers():
    if game_state.fright_timer > 0:
        game_state.fright_timer -= 1

def draw_ui():
    y = ROWS * TILE_SIZE
    pygame.draw.rect(screen, BLACK, (0, y, WIDTH, 40))

    for i in range(game_state.lives):
        pygame.draw.circle(screen, RED, (20 + i * 18, y + 20), 6)

    for i in range(min(game_state.level, 8)):
        pygame.draw.circle(screen, BLUE, (WIDTH // 2 - 30 + i * 18, y + 20), 6)

    for i in range(min(game_state.score // 100, 10)):
        pygame.draw.circle(screen, YELLOW, (WIDTH - 20 - i * 18, y + 20), 6)

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    cx, cy = WIDTH // 2, HEIGHT // 2

    for i in range(6):
        pygame.draw.circle(screen, RED, (cx - 40 + i * 16, cy - 10), 6)

    for i in range(6):
        pygame.draw.circle(screen, YELLOW, (cx - 40 + i * 16, cy + 20), 4)

def make_enemies():
    enemies = [
        Enemy(13, 14, RED, "CHASER", 0),
        Enemy(14, 14, PINK, "AMBUSHER", 30),
        Enemy(15, 14, CYAN, "RANDOM", 60),
        Enemy(14, 15, ORANGE, "FLANKER", 90),
    ]
    enemies[0].scatter_target = (2, 2)
    enemies[1].scatter_target = (25, 2)
    enemies[2].scatter_target = (2, 28)
    enemies[3].scatter_target = (25, 28)
    return enemies

def main():
    maze = Maze()
    player = Player(14, 23)
    enemies = make_enemies()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    player.next_dir_x, player.next_dir_y = 0, -1
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    player.next_dir_x, player.next_dir_y = 0, 1
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    player.next_dir_x, player.next_dir_y = -1, 0
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    player.next_dir_x, player.next_dir_y = 1, 0
                elif event.key == pygame.K_p:
                    game_state.paused = not game_state.paused
                elif event.key == pygame.K_r and game_state.game_over:
                    game_state.reset()
                    maze.init_maze()
                    player = Player(14, 23)
                    enemies = make_enemies()

        if not game_state.game_over and not game_state.paused:
            player.update(maze)

            if player.powered:
                for enemy in enemies:
                    if not enemy.frightened and not enemy.eaten:
                        enemy.frighten()

            for enemy in enemies:
                enemy.update(player, maze)

            if check_collisions(player, enemies):
                lose_life(player, enemies)

            update_timers()

            if game_state.pellets_remaining == 0:
                next_level(maze, player, enemies)

        screen.fill(BLACK)
        maze.draw()
        player.draw()

        for enemy in enemies:
            enemy.draw()

        draw_ui()

        if game_state.game_over:
            draw_game_over()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
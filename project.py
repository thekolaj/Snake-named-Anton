"""Snake game made with pygame.

You are free to change resolution and cell number. The game is fully scalable and should
handle any reasonable combinations.

Adjust difficulty by tweaking speed settings.
"""
import pygame as pg
import random

# // Settings //
# Approximate pixel height and width of the window. See AREA for final dimensions.
DESIRED_APPROXIMATE_RESOLUTION = 1000
# Number of cells (horizontally) and (vertically -1). Min: 3, min recommended: 12
CELL_NUMBER = 16
# Starting speed in ms. Less is harder, more is easier
START_SPEED = 180
# How much game speed increases in ms. Less is easier, more is harder
SPEED_INTERVAL = 1
# Endgame speed in ms. Less is harder, more is easier
SPEED_LIMIT = 50
# A way to end the game. Once snake is half the field, I see no point in dragging it out.
# Since we add food with recursions, don't make it too big on bigger fields.
MAX_SCORE = CELL_NUMBER * CELL_NUMBER // 2
# Cells size will be essential for the rest of the game to look right.
CELL = DESIRED_APPROXIMATE_RESOLUTION // CELL_NUMBER
# Final AREA must be divisible by CELL_NUMBER. This handles that
AREA = CELL * CELL_NUMBER


class Snake:
    """Handles all the variable objects in the game.

    snake = Snake() resets the game.
    """
    def __init__(self):
        # Direction the snake will move on the next MOVEMENT event. Starts stationary.
        self.direction = (0, 0)
        # During testing noticed that it was possible to cheat the movement restrictions
        # by entering multiple keystrokes between events. This prevents you from going
        # back into yourself.
        self.last_move_direction = (0, 0)
        # For printing speed to scoreboard
        self.speed = START_SPEED
        # Did not want to control the speed of the game with frame rate.
        # This is the alternative that uses custom events.
        self.MOVEMENT = pg.USEREVENT
        pg.time.set_timer(self.MOVEMENT, START_SPEED)
        # Head always starts at roughly the middle.
        self.head = pg.Rect(
            CELL_NUMBER // 2 * CELL,
            (CELL_NUMBER // 2 - 1) * CELL,
            CELL, CELL)
        self.score = 0
        # Adding this here helps with the unlikely event of food spawning on the same
        # cell as the head at the beginning of the game.
        self.parts = [self.head.copy()]
        self.food = randomize(self.parts)
        self.eating_sound = pg.mixer.Sound("assets/pickup.ogg")
        # 0 to continue play. 1 for LOSS. 2 for WIN.
        self.game_over = 0

    def change_direction(self, key):
        """Selects new direction best on the key pressed. Supports WASD and arrow keys.

        :param key: pygame.event.key
        """
        if ((key == pg.K_w or key == pg.K_UP) and
                self.last_move_direction[1] != CELL):
            self.direction = (0, -CELL)
        if ((key == pg.K_s or key == pg.K_DOWN) and
                self.last_move_direction[1] != -CELL):
            self.direction = (0, CELL)
        if ((key == pg.K_a or key == pg.K_LEFT) and
                self.last_move_direction[0] != CELL):
            self.direction = (-CELL, 0)
        if ((key == pg.K_d or key == pg.K_RIGHT) and
                self.last_move_direction[0] != -CELL):
            self.direction = (CELL, 0)

    def move(self):
        """Moves the snake and checks for any collisions."""
        # The whole head can be replaced with snake.parts[0],
        # but I find it easier to keep track of like this.
        self.head.move_ip(self.direction)
        # Check the borders before finalizing head's position.
        self.head.topleft = warp_on_borders(*self.head.topleft)
        self.parts.insert(0, self.head.copy())
        # Replaced during movement, so it would stay consistent during MOVEMENT event.
        # Moved here from change direction, where it was possible to double change it
        # before movement triggered.
        self.last_move_direction = self.direction
        # Check if you reached the food.
        if self.head == self.food:
            self.eating_sound.play()
            self.food = randomize(self.parts)
            self.score += 1
            # Check the win condition
            if self.score == MAX_SCORE:
                self.game_over = 2
            # New speed is set after every time you score.
            self.speed = speed(self.score)
            pg.time.set_timer(self.MOVEMENT, speed(self.score))
        else:
            # The most elegant way I found to handle growing the snake.
            self.parts.pop()
        # Check for collision with snakes body. 3 is the first possible collision.
        # Must be done after you pop() the last part so as not to hit the ghost tail.
        if self.head in self.parts[3:]:
            self.game_over = 1


def randomize(parts):
    """Creates a new Rect that is not already part of the snake.

    :param parts: List of pygame.Rect()
    :return: pygame.Rect()
    """
    x = random.randrange(0, AREA, CELL)
    y = random.randrange(0, AREA - CELL, CELL)
    new_food_position = pg.Rect(x, y, CELL, CELL)
    if new_food_position in parts:
        new_food_position = randomize(parts)
    return new_food_position


def speed(score):
    """Calculate game speed.

    :param score: int
    :return: int
    """
    new_speed = START_SPEED - (score * SPEED_INTERVAL)
    if new_speed < SPEED_LIMIT:
        new_speed = SPEED_LIMIT
    return new_speed


def warp_on_borders(x, y):
    """Check if snake crossed the border of the area.

    :param x: int in x dimension
    :param y: int in y dimension
    :return: tuple(x, y)
    """
    if x < 0:
        x = AREA - CELL
    elif x >= AREA:
        x = 0
    elif y < 0:
        y = AREA - CELL * 2
    elif y >= AREA - CELL:
        y = 0
    return x, y


def main():
    """Game asset preparation. Main game loop. Draw everything to screen."""
    # Pygame stuff that can be prepared before the main loop goes here.
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode((AREA, AREA))
    pg.display.set_caption("Snake named Anton")
    scoreboard_font = pg.font.Font(None, int(CELL * 1.5))
    game_over_font = pg.font.Font(None, (AREA // 6))
    game_over_text = game_over_font.render("Game Over!", True, "white")
    game_over_win = game_over_font.render("YOU WIN!", True, "white")
    game_over_sound = pg.mixer.Sound("assets/Failure.ogg")
    game_over_position = game_over_text.get_rect(center=(AREA // 2, AREA // 2))
    score_bar = pg.Surface((AREA, CELL))
    play_area = pg.Surface((AREA, AREA - CELL))
    head = pg.transform.scale(pg.image.load("assets/anton1.png").convert_alpha(),
                              (CELL*1.5, CELL*1.5))
    food = pg.transform.scale(pg.image.load("assets/hotdog.png").convert_alpha(),
                              (CELL * 1.5, CELL * 1.5))
    snake = Snake()

    # Main game loop
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

            # Work through all keyboard presses
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                snake.change_direction(event.key)

            # Move Snake on event timer
            if event.type == snake.MOVEMENT:
                snake.move()

        # Draw score bar with score and speed.
        score_bar.fill(pg.Color("gray30"))
        score_text = scoreboard_font.render(
            f"Score: {snake.score}/{MAX_SCORE} Speed: {snake.speed}",
            True, "aquamarine4")
        score_bar.blit(score_text, (2, 2))
        screen.blit(score_bar, (0, 0))

        # Draw play area,snake and food
        play_area.fill("black")
        for part in snake.parts[1:]:
            pg.draw.rect(play_area, "blue3", part)
        play_area.blit(head, (snake.head.x - (CELL//4), snake.head.y - (CELL//4)))
        play_area.blit(food, (snake.food.x - (CELL // 4), snake.food.y - (CELL // 4)))
        screen.blit(play_area, (0, CELL))
        # Check if the game is over, and reset it.
        if snake.game_over:
            if snake.game_over == 1:
                screen.blit(game_over_text, game_over_position)
            elif snake.game_over == 2:
                screen.blit(game_over_win, game_over_position)
            game_over_sound.play()
            pg.display.flip()
            pg.time.wait(3000)
            pg.event.clear()
            snake = Snake()

        pg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()

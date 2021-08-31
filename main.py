import asyncio
import curses
import random
import time
import os

from curses_tools import read_controls, draw_frame, get_frame_size
from explosion import explode
from obstacle import Obstacle
from rocket import Rocket
from space_calendar import get_garbage_delay_tics, update_year, show_year, garbage_present, get_year
from space_garbage import fly_garbage, load_garbage_frame
from utils import sleep


TIC_TIMEOUT = 0.01
obstacles = []
coroutines = []


async def rocket_control(canvas):
    canvas.nodelay(True)
    y, x = canvas.getmaxyx()
    y //= 2
    x //= 2
    rocket = Rocket(canvas, x, y, 5)
    bullets = []
    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        rocket.update_speed(rows_direction, columns_direction)
        rocket.update()
        if space_pressed and get_year() >= 2020:
            coroutines.append(fire(canvas, rocket.y, rocket.x + 2))
        for obstacle in obstacles:
            if (rocket.y, rocket.x) in obstacle:
                rocket.destroy()
                coroutines.append(obstacle.explode())
                await explode(canvas, rocket.y + 5, rocket.x + 2)
                return
        await sleep(1)


async def fire(canvas, start_row, start_column, rows_speed=-0.5, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await sleep(1)

    canvas.addstr(round(row), round(column), 'O')
    await sleep(1)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 1 < row < max_row and 1 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await sleep(1)
        canvas.addstr(round(row), round(column), ' ')
        for obstacle in obstacles:
            if (row, column) in obstacle:
                await obstacle.explode()
                return
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, pause, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(pause)

        canvas.addstr(row, column, symbol)
        await sleep(pause)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(pause)

        canvas.addstr(row, column, symbol)
        await sleep(pause)


async def fly_garbage(canvas, column, garbage_frame, delay=10):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    obstacle = Obstacle(canvas, column, garbage_frame, 1)
    obstacles.append(obstacle)

    while obstacle.active:
        obstacle.update()
        await sleep(delay)
    obstacles.remove(obstacle)


async def fill_orbit_with_garbage(canvas):
    h, w = canvas.getmaxyx()
    garbage_names = ['duck', 'hubble', 'lamp', 'trash_large', 'trash_small', 'trash_xl']
    garbage_frames = [load_garbage_frame(name) for name in garbage_names]

    while True:
        if garbage_present():
            frame = random.choice(garbage_frames)
            frame_width = max(map(len, frame.splitlines()))
            coroutines.append(
                fly_garbage(
                    canvas,
                    random.randint(1, w - frame_width),
                    frame
                )
            )
        await sleep(get_garbage_delay_tics())


async def show_gameover(canvas):
    gameover = """
       _____                         ____
      / ____|                       / __ \\
     | |  __  __ _ _ __ ___   ___  | |  | |_   _____ _ __
     | | |_ |/ _` | '_ ` _ \ / _ \ | |  | \ \ / / _ \ '__|
     | |__| | (_| | | | | | |  __/ | |__| |\ V /  __/ |
      \_____|\__,_|_| |_| |_|\___|  \____/  \_/ \___|_|

                      Press Escape to exit
                                                          """
    for coroutine in coroutines[:]:
        if coroutine.__name__ in ['fill_orbit_with_garbage', 'update_year']:
            coroutines.remove(coroutine)

    h, w = canvas.getmaxyx()
    frame_h, frame_w = get_frame_size(gameover)
    y, x = (h - frame_h) // 2, (w - frame_w) // 2

    while True:
        draw_frame(canvas, y, x, gameover)
        pressed_key_code = canvas.getch()
        if pressed_key_code == 27:
            return
        await sleep(1)


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    h, w = canvas.getmaxyx()
    coroutines.extend(
        blink(
            canvas,
            random.randint(1, h - 2),
            random.randint(1, w - 2),
            random.randint(5, 40),
            random.choice('*+.:')
        ) for c in range(50)
    )

    coroutines.append(rocket_control(canvas))
    coroutines.append(fill_orbit_with_garbage(canvas))
    coroutines.append(update_year())
    coroutines.append(show_year(canvas))
    while True:
        for coroutine in coroutines[:]:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
                if coroutine.__name__ == 'rocket_control':
                    coroutines.append(show_gameover(canvas))
                if coroutine.__name__ == 'show_gameover':
                    return
        
        canvas.border()
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)

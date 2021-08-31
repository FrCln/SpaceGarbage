from itertools import zip_longest
from functools import cache

from curses_tools import draw_frame
from utils import sleep

raw_digits = """\
   __      ___       ____      _  _      _____       __      ______     ___       ___       ___
  /_ |    |__ \     |___ \    | || |    | ____|     / /     |____  |   / _ \     / _ \     / _ \\
   | |       ) |      __) |   | || |_   | |__      / /_         / /   | (_) |   | (_) |   | | | |
   | |      / /      |__ <    |__   _|  |___ \    | '_ \       / /     > _ <     \__, |   | | | |
   | |     / /_      ___) |      | |     ___) |   | (_) |     / /     | (_) |      / /    | |_| |
   |_|    |____|    |____/       |_|    |____/     \___/     /_/       \___/      /_/      \___/ """

cols = list(zip_longest(*raw_digits.splitlines(), fillvalue=' '))
digits = ['\n'.join(''.join(line)[:8] for line in zip(*cols[i : i + 10])) for i in range(0, 100, 10)]
digits.insert(0, digits.pop())


PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}

_year = 1957


@cache
def create_year_frame(year):
    result = '\n'.join(''.join(line) for line in zip(*(digits[int(i)].splitlines() for i in str(year))))
    if year in PHRASES:
        result += '\n' + PHRASES[year].center(32)
    return result


def get_garbage_delay_tics():
    if _year < 1961:
        return 150
    elif _year < 1969:
        return 200
    elif _year < 1981:
        return 140
    elif _year < 1995:
        return 100
    elif _year < 2010:
        return 80
    elif _year < 2020:
        return 60
    else:
        return 20


async def update_year():
    global _year
    while True:
        await sleep(150)
        _year += 1


async def show_year(canvas):
    while True:
        frame = create_year_frame(_year)
        draw_frame(canvas, 1, 1, frame)
        await sleep(1)
        draw_frame(canvas, 1, 1, frame, negative=True)


def garbage_present():
    return _year >= 1961

def get_year():
    return _year

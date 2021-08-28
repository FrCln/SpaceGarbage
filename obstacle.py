from curses_tools import draw_frame
from explosion import explode


class Obstacle:
    def __init__(self, canvas, init_x, frame, speed):
        self.canvas = canvas
        self.x = init_x
        self.y = 0
        self.frame = frame
        self.height = len(frame.splitlines())
        self.width = max(map(len, frame.splitlines()))
        self.speed = speed
        self.active = True
        self.exploded = False

    def __repr__(self):
        return f'<Obstacle at {self.y}, {self.x}>'

    def __contains__(self, coords_yx):
        return self.y <= coords_yx[0] <= self.y + self.height and self.x <= coords_yx[1] <= self.x + self.width

    def update(self):
        draw_frame(self.canvas, self.y, self.x, self.frame, negative=True)

        if not self.exploded:
            self.y += self.speed
            draw_frame(self.canvas, self.y, self.x, self.frame)
            if self.y > self.canvas.getmaxyx()[0]:
                self.active = False

    async def explode(self):
        self.exploded = True
        await explode(self.canvas, self.y + self.height // 2, self.x + self.width // 2)
        self.active = False

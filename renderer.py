import curses
from controller import Controller
from engine import Map, Event, TileType
from entities import PlayerEntity

class Renderer:
    tile_render_map = {
        TileType.EMPTY: " ",  # EMPTY space
        TileType.FILL: "█",  # Filled space (rock)
        TileType.ENEMY: "e",  # Enemy
        TileType.KEY: "+",  # Key
        TileType.GOLD: "$",  # Gold
        TileType.PLAYER: "P",
    }
    _infoscr_h = 6

    def __init__(self, controller: Controller, map: Map, player: PlayerEntity):
        # Note: curses coordinate system is (y,x)
        self.stdscr = curses.initscr()
        self._map = map
        self._player = player
        self._controller = controller
        # Below len(str) used for axes labeling spacing
        self.mapscr = curses.newwin(self._map.size.h+len(str(self._map.size.h)), self._map.size.w+1+len(str(self._map.size.w)), 0, 0)
        self.infoscr = curses.newwin(self._infoscr_h, self._map.size.w, self._map.size.h, 0)
        curses.noecho()
        curses.cbreak()
        self.mapscr.keypad(True)

    def render_step(self):
        self.clear()
        self.render()
        key = self.mapscr.getkey()
        input_response = self._controller.handle_input(key)
        if input_response:
            print(f"IR: {input_response}")
            if input_response.event != Event.NULL:
                self._map.move_entity(input_response.from_pos, input_response.to_pos)
                self._map.handle_event(input_response.event, input_response.to_tile)
            self._map.entities_step()

                
    def clear(self):
        self.mapscr.clear()
        self.infoscr.clear()

    def shutdown(self):
        self.clear()
        curses.nocbreak()
        self.mapscr.keypad(False)
        curses.echo()
        curses.endwin()
        quit()

    def _get_infoscr_text(self):
        return [
            f"HP: {self._player.health}",
            f"Strength: {self._player.strength}",
            f"Keys: {self._player.keys}",
            f"Gold: {self._player.gold}",
        ]

    def render(self):
        # Render map
        for i, y in enumerate(self._map.state):
          line = "".join(map(lambda tile: self.tile_render_map[tile.type], y))
          self.mapscr.addstr(i, 0, line)
        texts = self._get_infoscr_text()
        # Divider
        self.infoscr.addstr(0, 0, "-"*self._map.size.w)
        for i in range(0, len(texts)):
            self.infoscr.addstr(i+1, 0, texts[i])
        self.mapscr.refresh()
        self.infoscr.refresh()

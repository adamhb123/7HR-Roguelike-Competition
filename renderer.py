import curses
from controller import Controller
from engine import Rect, Tile, Map, Event, TileType, Size
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

    def render_loop(self):
        while True:
            self.clear()
            self.render()
            key = self.mapscr.getkey()
            print(key)
            input_response = self._controller.handle_input(key)
            print(input_response)
            if input_response and input_response.event != Event.NULL:
                self._map.move_entity(input_response.from_pos, input_response.to_pos)
                self._map.handle_event(input_response.event, input_response.to_tile, input_response.to_pos)
                self._map.entities_step()
                
    def clear(self):
        self.mapscr.clear()
        self.infoscr.clear()

    def shutdown(self):
        curses.nocbreak()
        self.mapscr.keypad(False)
        curses.echo()
        curses.endwin()

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
          # print(y[0].type)
          # print(self.tile_render_map[y[0].type])
          line = "".join(map(lambda tile: self.tile_render_map[tile.type], y))
          self.mapscr.addstr(i, 0, line)
        texts = self._get_infoscr_text()
        # Divider
        self.infoscr.addstr(0, 0, "-"*self._map.size.w)
        for i in range(0, len(texts)):
            self.infoscr.addstr(i+1, 0, texts[i])
        self.mapscr.refresh()
        self.infoscr.refresh()

def test_renderer():
    map = Map(Size(72, 15))
    map.generate_rooms(1000,(2,5),(2,5))
    map._place_entity_randomly(Tile(TileType.PLAYER, PlayerEntity(100,10)))
    player = PlayerEntity(100, 10)
    controller = Controller(map, player)
    renderer = Renderer(controller, map, player)
    renderer.render_loop()
    

test_renderer()
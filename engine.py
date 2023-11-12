import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple
from entities import Entity

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Size:
    w: int
    h: int

@dataclass
class Rect:
    """Rect object for representing rectangles by Position and Size.

    Used to represent rooms in the game.
    """
    position: Position
    size: Size
    def __repr__(self):
        return f"[RECT] x: {self.position.x} y: {self.position.y} w: {self.size.w} h: {self.size.h}"
    def collides(self, rect: "Rect" | List["Rect"], padding: int=1) -> bool | List[bool]:
        if type(rect) is list:
            return any([self.collides(r) for r in rect])
        return (
            self.position.x - padding < rect.position.x + rect.size.w
            and self.position.x + self.size.w + padding > rect.position.x
            and self.position.y - padding < rect.position.y + rect.size.h
            and self.position.y + self.size.h + padding > rect.position.y
        )
    
class Event(Enum):
    """Event Enum
    
    Describes an event in-game.
    """
    NULL=-1
    STEP=0
    BATTLE=1
    PICKUP=2

class TileType(Enum):
    """TileType Enum

    Describes a Tile object's "type" i.e. what it represents in-game.
    """
    EMPTY=0
    FILL=1
    WALL=2
    ENEMY=3
    KEY=4
    GOLD=5
    PLAYER=6
    @staticmethod
    def to_int(tile_type: 'TileType'):
        return tile_type.value

@dataclass
class Tile:
    """Tile object

    Used for representing tiles
    
    Instance Attributes:
        type (TileType) - Type of Tile
        entity (Optional[Entity]) - Optional Entity attribute, used as a container of any information relevant to the Tile. Defaults to None.
    """
    type: TileType
    entity: Optional[Entity]=None

EmptyTileSingleton = Tile(TileType.EMPTY)
FillTileSingleton = Tile(TileType.FILL)

class Map:
    def __init__(self, size: Size):
        self.size = size
        self.rooms: List[Rect] = []
        self.reset_state()

    def reset_state(self):
        self.state = [[FillTileSingleton for x in range(0, self.size.w)] for y in range(0, self.size.h)]

    def entities_step(self):
        entities = self._find_tiles(TileType.ENEMY)
        # Calculate shortest path for enemies, move them along path


    def handle_event(self, event: Event, tile: TileType, tile_pos: Position):
        if event == Event.BATTLE:
            pass
        elif event == Event.PICKUP:
            pass
    def time_step(self, player_pos: Position, to_tile: TileType | int, to: Position):
        self._map.move_entity(player_pos.x, player_pos.y, to.x, to.y)
        self.entities_step()

    def _update_rooms(self):
        for room in self.rooms:
            """# Place horizontal walls
            print(self.state)
            for x in range(room.x, room.x + room.w):
                self.state[room.y][x] = Tile.WALL.value
                self.state[room.y+room.h][x] = Tile.WALL.value
            # Place vertical walls
            for y in range(room.y, room.y+room.h):
                self.state[y][room.x] = Tile.WALL.value
                self.state[y][room.x+room.w] = Tile.WALL.value"""
            # Carve room
            for y in range(room.position.y, room.position.y+room.size.h):
                for x in range(room.position.x, room.position.x+room.size.w):
                    self.state[y][x] = EmptyTileSingleton

    def _place_room(self, position: Position, size: Size):
        new_room = Rect(position, size)
        if self.rooms and new_room.collides(self.rooms):
            #print(f"Can't place room: {new_room}")
            return False
        self.rooms.append(new_room)
        print(new_room)
        self._update_rooms()
        return True
    
    def _find_tiles(self, tile_type: TileType) -> List[Position]:
        locations: List[Position] = []
        for y in range(0,len(self.state)):
            for x in range(0,len(self.state[0])):
                if self.state[y][x].type == tile_type:
                    locations.append(Position(x,y))
        return locations

    
    def _place_entity(self, position: Position, entity_tile: Tile):
        if self.get_tile_at(position) == EmptyTileSingleton:
            self.state[position.y][position.x] = entity_tile
            return True
        return False

    def _place_entity_randomly(self, entity_tile: Tile, max_attempts: int = 10000):
        for _ in range(max_attempts):
            if self._place_entity(Position(random.randint(0,self.size.w), random.randint(0, self.size.h)), entity_tile):
                return True
        return False

    def _place_room_randomly(self, size: Size, outer_padding: int = 1):
        x = random.randint(outer_padding, self.size.w - size.w - outer_padding)
        y = random.randint(outer_padding, self.size.h - size.h - outer_padding)
        self._place_room(Position(x,y), size)
    
    def get_tile_at(self, position: Position):
        return self.state[position.y][position.x]
    
    def move_entity(self, from_position: Position, to_position: Position):
        self.state[to_position.y][to_position.x] = self.state[from_position.y][from_position.x]
        self.state[from_position.y][from_position.x] = EmptyTileSingleton

    def generate_rooms(self, n_attempts: int, width_range: Tuple[int, int], height_range: Tuple[int, int]):
        for _ in range(0, n_attempts):
            self._place_room_randomly(Size(random.randint(width_range[0], width_range[1]),
                            random.randint(height_range[0], height_range[1])))

    def generate_corridors(self):
        pass

        

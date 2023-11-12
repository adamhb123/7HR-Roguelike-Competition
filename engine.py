import random
from dataclasses import dataclass
from enum import Enum
import time
from typing import List, Optional, Tuple
from entities import EnemyEntity, Entity

@dataclass
class Position:
    x: int
    y: int
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

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
    def __eq__(self, other: 'Rect'):
        # Positions should be enough for equality, as Rects should not overlap in our usecase
        return self.position.x == other.position.x and self.position.y == other.position.y
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
        player_pos = self._find_tiles(TileType.PLAYER)[0]
        # Calculate shortest path for enemies, move them along path
        for enemy_pos in entities:
            new_pos = Position(enemy_pos.x, enemy_pos.y)
            dist_x = player_pos.x - enemy_pos.x
            dist_y = player_pos.y - enemy_pos.y
            if abs(dist_x) > abs(dist_y):
                if dist_x > 0:
                    new_pos.x += 1
                elif dist_x < 0:
                    new_pos.x -= 1
            else:
                if dist_y > 0:
                    new_pos.y += 1
                elif dist_y < 0:
                    new_pos.y -= 1
            if new_pos == player_pos:
                enemy = self.state[enemy_pos.y][enemy_pos.x]
                self.handle_event(Event.BATTLE, enemy, enemy_pos)
            self.move_entity(enemy_pos, new_pos)
            

    def handle_event(self, event: Event, tile: Tile, tile_pos: Position):
        # Here, we assume that the event is between the PLAYER and some other TILE
        # The other tile is provided using the tile_type and tile_pos and variables
        player_pos = self._find_tiles(TileType.PLAYER)[0]
        player = self.state[player_pos.y][player_pos.x]
        if event == Event.BATTLE:
            # tile = enemy
            while player.entity.health > 0 and tile.entity.health > 0:
                if random.random() > .5:
                    player.entity.attack(tile.entity)
                else:
                    tile.entity.attack(player.entity)
            if player.entity.health <= 0:
                return -1
            elif tile.entity.health <= 0:
                print(tile)
                #self.state[tile_pos.y][tile_pos.x] = EmptyTileSingleton
                player.entity.gold += tile.entity.drop()
        elif event == Event.PICKUP:
            print("EVENT PICKUP: ", tile)
            print("IS KEY? ", tile.type == TileType.KEY)
            if tile.type == TileType.KEY:
                player.entity.keys += 1
                print(f"PE KEYS: {player.entity.keys}")
            elif tile.type == TileType.GOLD:
                player.entity.gold += 1

        

    def time_step(self, player_pos: Position, to_tile: TileType | int, to: Position):
        self._map.move_entity(player_pos.x, player_pos.y, to.x, to.y)
        self.entities_step()

    def _carve(self, position: Position):
        if self.get_tile_at(position).type == TileType.FILL:
            self.state[position.y][position.x] = EmptyTileSingleton


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
                    self._carve(Position(x,y))

    def _place_room(self, position: Position, size: Size):
        new_room = Rect(position, size)
        if self.rooms and new_room.collides(self.rooms):
            #print(f"Can't place room: {new_room}")
            return False
        self.rooms.append(new_room)
        # print(new_room)
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
            if self._place_entity(Position(random.randint(0,self.size.w-1), random.randint(0, self.size.h-1)), entity_tile):
                return True
        return False

    def _place_room_randomly(self, size: Size, outer_padding: int = 1):
        x = random.randint(outer_padding, self.size.w - size.w - outer_padding)
        y = random.randint(outer_padding, self.size.h - size.h - outer_padding)
        self._place_room(Position(x,y), size)
    
    def get_tile_at(self, position: Position):
        return self.state[position.y][position.x]
    
    def move_entity(self, from_position: Position, to_position: Position):
        to_tile = self.get_tile_at(to_position)
        if to_tile.type != TileType.PLAYER:
            print(to_tile.type)
            self.state[to_position.y][to_position.x] = self.state[from_position.y][from_position.x]
            self.state[from_position.y][from_position.x] = EmptyTileSingleton

    def generate_rooms(self, n_attempts: int, width_range: Tuple[int, int], height_range: Tuple[int, int]):
        for _ in range(0, n_attempts):
            self._place_room_randomly(Size(random.randint(width_range[0], width_range[1]),
                            random.randint(height_range[0], height_range[1])))

    def generate_corridors(self, debug_render_step_func):
        rooms = sorted(self.rooms, key=lambda room: room.position.y)
        for i in range(len(rooms)):
            for j in range(len(rooms)):
                i=0
                room_a, room_b = rooms[i], rooms[j]
                if room_a != room_b:
                    h_check = room_a.position.x + room_a.size.w < room_b.position.x or room_b.position.x + room_b.size.w < room_a.position.x
                    v_check = room_a.position.y + room_a.size.h < room_b.position.y or room_b.position.y + room_b.size.h < room_a.position.y
                   #  print(room_a, room_b, v_check, h_check)
                    if v_check and h_check:
                        direction = random.randint(0,1)
                    elif v_check:
                        direction = 0
                    elif h_check:
                        direction = 1
                    else:
                        continue
                    if direction == 0: # Then vertical
                        # Pick random y coordinate between rooms
                        #y = random.randint(room_a.position.)
                        if room_a.position.y > room_b.position.y:
                           room_a, room_b = room_b, room_a
                        # print(room_a, room_b)
                        y = random.randint(room_a.position.y + room_a.size.h, room_b.position.y)
                        point_a = Position(room_a.position.x + random.randint(0, room_a.size.w),
                                        room_a.position.y + room_a.size.h)
                        point_b = Position(room_b.position.x + random.randint(0, room_b.size.w), room_b.position.y)
                        while point_a.y != y:
                            # print(point_a.y, y)
                            self._carve(point_a)
                            point_a.y += 1
                        while point_b.y != y:
                            # print(point_b.y, y)
                            self._carve(point_b)
                            point_b.y -= 1
                    elif direction == 1: # Then horizontal
                        if room_a.position.x > room_b.position.x:
                            room_a, room_b = room_b, room_a
                        # Pick random x coordinate between rooms
                        x = random.randint(room_a.position.x + room_a.size.w, room_b.position.x)
                        point_a = Position(room_a.position.x + room_a.size.w,
                                           room_a.position.y + random.randint(0, room_a.size.h))
                        point_b = Position(room_b.position.x, room_b.position.y + random.randint(0, room_b.size.h))
                        while point_a.x != x:
                            self._carve(point_a)
                            point_a.x += 1
                        while point_b.x != x:
                            self._carve(point_b)
                            point_b.x -= 1
                debug_render_step_func()
                
    def generate_enemies(self, n: int):
        for i in range(0, n):
            enemy = EnemyEntity(10, 10, (2,5))
            self._place_entity_randomly(Tile(TileType.ENEMY, enemy))

        

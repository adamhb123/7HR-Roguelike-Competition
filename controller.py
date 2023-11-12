from dataclasses import dataclass
from typing import Optional, Tuple
from engine import Map, Position, Tile, Event, TileType
from entities import PlayerEntity

key_to_direction = {
    "w" : 0, # Up
    "d" : 1, # Right
    "s" : 2, # Down
    "a" : 3  # Left
}

@dataclass
class InputResponse:
    event: Event
    to_tile: Tile
    from_pos: Position
    to_pos: Position


class Controller:
    def __init__(self, map: Map, player: PlayerEntity):
        self._map = map
        self._player = player

    def _check_valid_move(self, start_pos: Position, direction: int) -> InputResponse:
        """Checks if a move from start_pos in direction is valid.

        Args:
            start_pos (Position): _description_
            direction (int): _description_

        Returns:
            InputResponse: Contains various information about the move (see InputResponse class for details)
        """
        to = Position(start_pos.x, start_pos.y)
        # Movement checks
        if direction == 0: # UP
            to.y = start_pos.y-1
        elif direction == 1: # RIGHT
            to.x = start_pos.x+1
        elif direction == 2: # DOWN
            to.y = start_pos.y+1
        elif direction == 3: # LEFT
            to.x = start_pos.x-1

        tile = self._map.get_tile_at(to)

        if tile.type == TileType.EMPTY:
            event = Event.STEP
        elif tile.type == TileType.ENEMY:
            event = Event.BATTLE
        elif tile.type == TileType.GOLD or tile.type == TileType.KEY:
            event = Event.PICKUP
        else: # Wall hit
            event = Event.NULL
            to = start_pos # If we hit a wall, move nowhere
        return InputResponse(event, tile, start_pos, to)
        
    def handle_input(self, key: str) -> Optional[InputResponse]:
        player_pos = self._map._find_tiles(TileType.PLAYER)[0]
        if key in key_to_direction:
            return self._check_valid_move(player_pos, key_to_direction[key])
        
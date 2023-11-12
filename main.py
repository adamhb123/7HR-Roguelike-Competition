from controller import Controller
from engine import Map, Size
from entities import PlayerEntity
from renderer import Renderer


def main():
    map = Map(Size(72, 15))
    player = PlayerEntity(100,10)
    controller = Controller(map, player)
    renderer = Renderer(controller, map, player)
    map.renderer = renderer
    map.initialize_game(player)

if __name__=="__main__":
    main()

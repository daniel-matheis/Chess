"""
Main
"""

import pygame as p
from chess import engine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

"""Initialize global dict of images"""
def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))

"""Main"""
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False

    # print(gs.board)
    load_images()
    running = True
    square_selected = ()
    player_clicks = [] # 2 tuples w/ (x,y) coordinates

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                file = location[0]//SQ_SIZE
                rank = location[1]//SQ_SIZE
                if square_selected == (rank, file):
                    square_selected = ()
                    player_clicks = []
                else:
                    square_selected = (rank, file)
                    player_clicks.append(square_selected)
                if len(player_clicks) == 2:
                    move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                    print(move.write_chess_notation())
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            gs.make_move(valid_moves[i])
                            move_made = True
                            square_selected = ()
                            player_clicks = []
                    if not move_made:
                        player_clicks = [square_selected]
            # Key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u: # undo move
                    gs.undo_move()
                    move_made = True
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_gamestate(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

"""Draws all tiles and pieces"""
def draw_gamestate(screen, gs):
    draw_board(screen)
    draw_pieces(screen, gs.board)

"""Draw the squares/tiles on the board"""
def draw_board(screen):
    colors = [p.Color('white'), p.Color('grey')]
    for r in range(DIMENSION):
        for f in range (DIMENSION):
            color = colors[((r+f) % 2)]
            p.draw.rect(screen, color, p.Rect(f*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""Draws the pieces using the current GameState.board"""
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for f in range(DIMENSION):
            piece = board[r][f]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(f*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == '__main__':
    main()
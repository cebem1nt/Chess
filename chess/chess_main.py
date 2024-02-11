import pygame as p
import chess_engine
import chess_bot

p.init()
WIDTH = HEIGHT = 600
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION 
MAX_FPS = 15
IMAGES = {}

colors = {
    'default':[(240, 217, 181), (181, 135, 99)],
    'additional': [(236, 236, 236), (193, 193, 142)]
}

selected_theme = 'maestro'
selected_color = 'additional'

players = {
    'white': 'H',
    'black': 'H'
}

def load_images(): 
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
    for piece in pieces:
        image_path = f'images/{selected_theme}/{piece}.png'
        original_image = p.image.load(image_path)
        scaled_image = p.transform.smoothscale(original_image, (SQUARE_SIZE, SQUARE_SIZE))
        IMAGES[piece] = scaled_image

def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    game_state = chess_engine.Game_state()
    valid_moves = game_state.get_all_possible_moves()
    move_made = False
    game_over = False

    load_images()
    is_running = True
    sq_selected = ()
    player_clicks = []
    current_turn = 'H' if players['white'] == 'H' else 'B'

    while is_running:
        for event in p.event.get():
            if event.type == p.QUIT:
                is_running = False

            elif event.type == p.MOUSEBUTTONDOWN:
                if not game_over and current_turn == 'H':
                    location = p.mouse.get_pos()
                    column = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE

                    if sq_selected == (row, column):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, column)
                        player_clicks.append(sq_selected)

                    if len(player_clicks) == 2:
                        move = chess_engine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                draw_game_state(screen, game_state, game_state, valid_moves, sq_selected)
                                p.display.flip()
                                print(valid_moves[i].get_chess_notation(game_state))
                                if players['white'] == 'H' and players['black'] == 'H':
                                    current_turn = 'H'
                                else:
                                    current_turn = 'B'
                                sq_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
                     
            if event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    game_state.undo_move()
                    move_made = True
                    game_over = False
                elif event.key == p.K_r:
                    game_over = False
                    game_state = chess_engine.Game_state()
                    valid_moves = game_state.get_all_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False

            if move_made:
                valid_moves = game_state.get_all_valid_moves()
                move_made = False

            if not game_over and current_turn == 'B':
                bot_move = chess_bot.find_best_move(game_state, valid_moves)
                if bot_move == None:
                    bot_move = chess_bot.random_move(valid_moves)
                game_state.make_move(bot_move)
                draw_game_state(screen, game_state, game_state, valid_moves, sq_selected)
                p.display.flip()
                move_made = True
                print(bot_move.get_chess_notation(game_state))
                if players['black'] == 'B' and players['white'] == 'B':
                    current_turn = 'B'
                else: 
                    current_turn = 'H'

            draw_game_state(screen, game_state, game_state, valid_moves, sq_selected)

            if game_state.checkmate:
                game_over = True
                if game_state.white_move:
                    draw_text(screen, 'Black won')
                    print('#') 
                else:
                    draw_text(screen, 'White won')
            elif game_state.stalemate:
                game_over = True
                draw_text(screen, 'Stalemate')
                print('1/2')

            clock.tick(MAX_FPS)
            p.display.flip()

def draw_game_state(screen, game_state, gs, valid_moves, sq_selected):
    draw_board(screen)
    draw_pieces(screen, game_state.board)
    higlight_sqares(screen, gs, valid_moves, sq_selected)

def higlight_sqares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_move else 'b'):
            for move in valid_moves:
                if move.start_row == r and move.start_column == c:
                    square_center = (
                            move.end_column * SQUARE_SIZE + SQUARE_SIZE // 2,
                            move.end_row * SQUARE_SIZE + SQUARE_SIZE // 2
                        )
                    if not move.is_capture:
                        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE), p.SRCALPHA)
                        p.draw.circle(s, (128, 128, 128, 50), (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 7)
                        screen.blit(s, (square_center[0] - SQUARE_SIZE // 2, square_center[1] - SQUARE_SIZE // 2))
                    else:
                        outer_radius = SQUARE_SIZE // 2
                        inner_radius = outer_radius // 1.2
                        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE), p.SRCALPHA)
                        p.draw.circle(s, (128, 128, 128, 50), (SQUARE_SIZE // 2, SQUARE_SIZE // 2), outer_radius)
                        p.draw.circle(s, (0, 0, 0, 0), (SQUARE_SIZE // 2, SQUARE_SIZE // 2), inner_radius)
                        screen.blit(s, (square_center[0] - SQUARE_SIZE // 2, square_center[1] - SQUARE_SIZE // 2))

def draw_board(screen):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[selected_color][((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(column*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_text(screen, text):
    font = p.font.SysFont("arial", 32, True, False)
    text_obj = font.render(text, 0, p.Color('Black'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_obj.get_width()/2, HEIGHT/2 - text_obj.get_height()/2)
    screen.blit(text_obj, text_location)

if __name__ == '__main__':
    main()
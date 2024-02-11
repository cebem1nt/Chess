import random

piece_scores = {'K': 0,'Q': 10,'R': 5,'B': 3,'N': 3,'P': 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2

def random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]

def find_best_move(gs, valid_moves):
    global next_move
    random.shuffle(valid_moves)
    next_move = None
    alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_move else -1)
    return next_move

def find_move_minmax(gs, valid_moves, depth, white_move):
    global next_move
    if depth == 0:
        return score_board(gs.board)
    
    if white_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_all_valid_moves()
            score = find_move_minmax(gs, next_moves, depth-1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score
    
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_all_valid_moves()
            score = find_move_minmax(gs, next_moves, depth-1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score

def find_move_nega_max(gs, valid_moves, depth, turn_mult):
    global next_move
    if depth == 0:
        return turn_mult*score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_all_valid_moves()
        score = -find_move_nega_max(gs, next_moves, depth-1, -turn_mult)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()

    return max_score

def alpha_beta(gs, valid_moves, depth, alpha, beta, turn_mult):
    global next_move
    if depth == 0:
        return turn_mult*score_board(gs)
    
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_all_valid_moves()
        score = -alpha_beta(gs, next_moves, depth-1, -beta, -alpha, -turn_mult)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score

#a positive score is good for white, a negative is good for black
def score_board(gs):
    if gs.checkmate and gs.white_move:
        return -CHECKMATE
    elif gs.checkmate and not gs.white_move:
        return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    score = 0
    for row in gs.board:
        for sqare in row:
            if sqare[0] == 'w':
                score += piece_scores[sqare[1]]
            elif sqare[0] == 'b':
                score -= piece_scores[sqare[1]]
    return score
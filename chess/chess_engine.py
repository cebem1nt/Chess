class Game_state():
    def __init__(self):

        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]

        self.piece_functions = {
            'P' : self.get_pawn_moves,
            'R' : self.get_rook_moves,
            'N' : self.get_knight_moves,
            'B' : self.get_bishop_moves,
            'Q' : self.get_queen_moves,
            'K' : self.get_king_moves
        }

        self.white_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.en_passant_pos = ()
        self.en_passant_pos_log = [self.en_passant_pos]
        self.current_castling_rights = Castle_rights(True, True, True, True)
        self.castle_rights_log = [Castle_rights(self.current_castling_rights.wks, self.current_castling_rights.wqs,
                                  self.current_castling_rights.bks, self.current_castling_rights.bqs)]
        

    def make_move(self, move):
        self.board[move.start_row][move.start_column] = '--'
        self.board[move.end_row][move.end_column] = move.moved_piece
        self.move_log.append(move)

        if move.moved_piece == 'wK':
            self.white_king_location = (move.end_row, move.end_column)
        elif move.moved_piece == 'bK':
            self.black_king_location = (move.end_row, move.end_column)

        self.white_move = not self.white_move

        #pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_column] = move.moved_piece[0] + 'Q'

        #en passant
        if move.is_en_passant_move:
            self.board[move.start_row][move.end_column] = '--' 
            self.en_passant_pos = ()

        #en passant tracking   
        if move.moved_piece[1] == 'P' and abs(move.start_row - move.end_row) == 2:
            self.en_passant_pos = ((move.start_row + move.end_row)//2, move.start_column)
        else:
            self.en_passant_pos = ()

        self.en_passant_pos_log.append(self.en_passant_pos)

        #castling
        if move.is_castling:
            if move.end_column - move.start_column == 2: #kingside castle
                self.board[move.end_row][move.end_column-1] = self.board[move.end_row][move.end_column+1]
                self.board[move.end_row][move.end_column+1] = '--'

            else: #queenside castle
                self.board[move.end_row][move.end_column+1] = self.board[move.end_row][move.end_column-2]
                self.board[move.end_row][move.end_column-2] = '--'
                
        #castling tracking
        self.update_castle_righs(move)
        self.castle_rights_log.append(Castle_rights(self.current_castling_rights.wks, self.current_castling_rights.wqs, 
                                                    self.current_castling_rights.bks, self.current_castling_rights.bqs))

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_column] = move.moved_piece
            self.board[move.end_row][move.end_column] = move.captured_piece

            if move.moved_piece == 'wK':
                self.white_king_location = (move.start_row, move.start_column)
            elif move.moved_piece == 'bK':
                self.black_king_location = (move.start_row, move.start_column)

            #undoing en passant
            if move.is_en_passant_move:
                self.board[move.end_row][move.end_column] = '--'
                self.board[move.start_row][move.end_column] = move.captured_piece
                
            self.en_passant_pos_log.pop()
            self.en_passant_pos = self.en_passant_pos_log[-1]

            #castling undoind
            self.castle_rights_log.pop()
            new_rights = self.castle_rights_log[-1]
            self.current_castling_rights = Castle_rights(new_rights.wks, new_rights.wqs,
                                                         new_rights.bks, new_rights.bqs)

            #undo castle move
            if move.is_castling:
                if move.end_column - move.start_column == 2: #kingside
                    self.board[move.end_row][move.end_column+1] = self.board[move.end_row][move.end_column-1]
                    self.board[move.end_row][move.end_column-1] = '--'
                else: #queenside
                    self.board[move.end_row][move.end_column-2] = self.board[move.end_row][move.end_column+1]
                    self.board[move.end_row][move.end_column+1] = '--'

            self.white_move = not self.white_move
            self.checkmate = False
            self.stalemate = False

    def update_castle_righs(self, move):
        if move.moved_piece == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False

        elif move.moved_piece == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False

        if move.moved_piece == 'wR':
            if move.start_row == 7 and move.start_column == 0:
                self.current_castling_rights.wqs = False
            else:
                self.current_castling_rights.wks = False

        elif move.moved_piece == 'bR':
            if move.start_row == 0 and move.start_column == 7:
                self.current_castling_rights.bqs = False
            else:
                self.current_castling_rights.bks = False

        if move.captured_piece == 'wR':
            if move.end_row == 7 and move.end_column == 0:
                self.current_castling_rights.wqs = False
            else:
                self.current_castling_rights.wks = False

        elif move.captured_piece == 'bR':
            if move.end_row == 0 and move.end_column == 0:
                self.current_castling_rights.bqs = False
            else:
                self.current_castling_rights.bks = False

    def get_all_valid_moves(self):
        tmp_en_passant_pos = self.en_passant_pos
        tmp_castling_rights = Castle_rights(self.current_castling_rights.wks, self.current_castling_rights.wqs,
                                            self.current_castling_rights.bks, self.current_castling_rights.bqs)
        moves = self.get_all_possible_moves()
        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            self.white_move = not self.white_move

            if self.in_check():
                moves.remove(moves[i])

            self.white_move = not self.white_move
            self.undo_move()
            
        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
                return moves
            else:
                self.stalemate = True
                return moves
        else:
            self.checkmate = False
            self.stalemate = False

        if self.white_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        self.en_passant_pos = tmp_en_passant_pos
        self.current_castling_rights = tmp_castling_rights
        return moves

    def in_check(self):
        if self.white_move:
            return self.sq_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.sq_under_attack(self.black_king_location[0], self.black_king_location[1])


    def sq_under_attack(self, r, c):
        self.white_move = not self.white_move
        opp_moves = self.get_all_possible_moves()
        self.white_move = not self.white_move
        for move in opp_moves:
            if move.end_row == r and move.end_column == c:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for row in range(8):
            for column in range(8):
                turn = self.board[row][column][0]
                if (turn == 'w' and self.white_move) or (turn == 'b' and not self.white_move):
                    piece = self.board[row][column][1]
                    self.piece_functions[piece](row, column, moves)      

        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_move:
            if self.board[r-1][c] == '--': #1 sqare white forward move
                moves.append(Move((r, c), (r-1, c), self.board))

                if r == 6 and self.board[r-2][c] == '--': #2 squares white forward move
                    moves.append(Move((r, c), (r-2, c), self.board))

            if c-1 >= 0: #left capture
                if self.board[r-1][c-1][0] == 'b': 
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.en_passant_pos:
                    moves.append(Move((r, c), (r-1, c-1), self.board, en_passant=True))

            if c+1 <= 7: #right capture
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.en_passant_pos:
                    moves.append(Move((r, c), (r-1, c+1), self.board, en_passant=True))

        else:
            if self.board[r+1][c] == '--': #1 square black forward move
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == '--': #2 squares black forward move
                    moves.append(Move((r, c), (r+2, c), self.board))
            
            if c-1 >= 0: #left capture
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.en_passant_pos:
                    moves.append(Move((r, c), (r+1, c-1), self.board, en_passant=True))
                
            if c+1 <= 7: #right capture
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.en_passant_pos:
                    moves.append(Move((r, c), (r+1, c+1), self.board, en_passant=True))


    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.white_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]

                    if end_piece == '--':
                        moves.append(Move((r,c), (end_row, end_col), self.board))

                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                        break
                    else:
                        break

                else:
                    break

    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.white_move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]

                    if end_piece == '--':
                        moves.append(Move((r,c), (end_row, end_col), self.board))

                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                        break
                    else:
                        break

                else:
                    break

    def get_knight_moves(self, r, c, moves):
        directions = ((-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2))
        ally_color = 'w' if self.white_move else 'b'
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r,c), (end_row, end_col), self.board))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        ally_color = 'w' if self.white_move else 'b'
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r,c), (end_row, end_col), self.board))

    def get_castle_moves(self, r, c, moves):
        if self.sq_under_attack(r, c): 
            return
        
        if (self.white_move and self.current_castling_rights.wks) or (not self.white_move and self.current_castling_rights.bks):
            self.get_ks_castle(r, c, moves)

        if (self.white_move and self.current_castling_rights.wqs) or (not self.white_move and self.current_castling_rights.bqs):
            self.get_qs_castle(r, c, moves)

    def get_ks_castle(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.sq_under_attack(r, c+1) and not self.sq_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, castling=True))

    def get_qs_castle(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.sq_under_attack(r, c-1) and not self.sq_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, castling=True))

class Castle_rights():
    def __init__(self, wks, wqs, bks, bqs): #white king and queen sides, black king and queen sides
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs


class Move():
    ranks_to_rows = { "1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0 }
    
    files_to_cols = { "a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7 }

    rows_to_ranks = {v:k for k, v in ranks_to_rows.items()}
    
    cols_to_files = {v:k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, en_passant=False, castling=False):

        self.start_row = start_sq[0]
        self.start_column = start_sq[1]

        self.end_row = end_sq[0]
        self.end_column = end_sq[1]

        self.moved_piece = board[self.start_row][self.start_column]
        self.captured_piece = board[self.end_row][self.end_column]

        self.is_pawn_promotion = (self.moved_piece == 'wP' and self.end_row == 0) or (self.moved_piece == 'bP' and self.end_row == 7)
        self.promotion_choice = ''

        self.is_en_passant_move = en_passant
        self.is_castling = castling
        self.is_capture = (self.captured_piece != '--') or (self.is_en_passant_move)

        if self.is_en_passant_move:
            self.captured_piece = 'wP' if self.moved_piece == 'bP' else 'bP'

        self.move_id = self.start_row * 1000 + self.start_column * 100 + self.end_row * 10 + self.end_column

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self, gs):
        check = gs.in_check()
        res = ''
        if self.is_castling:
            if self.end_column < self.start_column:
                res = 'O-O-O'
            else:
                res = 'O-O'
        else:
            start = self.get_rank_file(self.start_row, self.start_column)
            end = self.get_rank_file(self.end_row, self.end_column)
            if self.moved_piece[1] == 'P':
                if self.is_capture:
                    res = f'{start[0]}x{end}'
                else:
                    res = end
            elif self.is_capture:
                res = f'{self.moved_piece[1]}x{end}'
            else:
                res = self.moved_piece[1] + end

        if check:
            return res + '+'
        else:
            return res
        
    def get_rank_file(self, row, column):
        return self.cols_to_files[column] + self.rows_to_ranks[row]
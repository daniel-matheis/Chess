"""
Current State, Valid Moves, Storing Info like Move Log
"""
class GameState:
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

        self.move_functions = {
            'p': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'N': self.get_knight_moves,
            'B': self.get_bishop_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves
        }

        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassant_possible = () # coordinates for the square
        self.current_castling_right = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                               self.current_castling_right.wqs, self.current_castling_right.bqs)]


    def make_move(self, move):
        self.board[move.start_rank][move.start_file] = '--'
        self.board[move.end_rank][move.end_file] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        # update king's position
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_rank, move.end_file)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_rank, move.end_file)
        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_rank][move.end_file] = move.piece_moved[0] + 'Q'
        # en-passant
        if move.is_enpassant_move:
            self.board[move.start_rank][move.end_file] = '--'
        # update enpassant_possible
        if move.piece_moved[1] == 'p' and abs(move.start_rank - move.end_rank) == 2:
            self.enpassant_possible = ((move.start_rank + move.end_rank)//2, move.start_file)
        else:
            self.enpassant_possible = ()
        # castle move
        if move.is_castle_move:
            # print(move.start_rank, move.start_file)
            # print(move.end_rank, move.end_file)
            if move.end_file - move.start_file == 2:
                self.board[move.end_rank][move.end_file-1] = self.board[move.end_rank][move.end_file+1] # moves the rook
                self.board[move.end_rank][move.end_file+1] = '--' # remove the old rook
            else: # queenside castle move
                self.board[move.end_rank][move.end_file+1] = self.board[move.end_rank][move.end_file-2] # moves the rook
                self.board[move.end_rank][move.end_file-2] = '--' # remove the old rook
        # update castling rights - if it's a king or rook move
        self.update_castling_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                                   self.current_castling_right.wqs, self.current_castling_right.bqs))


    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_rank][move.start_file] = move.piece_moved
            self.board[move.end_rank][move.end_file] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # update king's position
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_rank, move.start_file)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_rank, move.start_file)

            if move.is_enpassant_move:
                self.board[move.end_rank][move.end_file] = '--' # leave landing square blank
                self.board[move.start_rank][move.end_file] = move.piece_captured
                self.enpassant_possible = (move.end_rank, move.end_file)

            if move.piece_moved[1] == 'p' and abs(move.start_rank - move.end_rank) == 2:
                self.enpassant_possible = ()

            # undo castling rights
            self.castle_rights_log.pop() # remove castling rights from undone move
            new_rights = self.castle_rights_log[-1]
            self.current_castling_right = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)
            # self.current_castling_right.wks = self.castle_rights_log[-1].wks
            # self.current_castling_right.wqs = self.castle_rights_log[-1].wqs
            # self.current_castling_right.bks = self.castle_rights_log[-1].bks
            # self.current_castling_right.bqs = self.castle_rights_log[-1].bqs


            # undo castle move - put rook back
            if move.is_castle_move:
                if move.end_file - move.start_file == 2: # kingside castle move
                    self.board[move.end_rank][move.end_file+1] = self.board[move.end_rank][move.end_file-1]
                    self.board[move.end_rank][move.end_file-1] = '--'
                else: # queenside castle move
                    self.board[move.end_rank][move.end_file-2] = self.board[move.end_rank][move.end_file+1]
                    self.board[move.end_rank][move.end_file+1] = '--'

    def update_castling_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_rank == 7:
                if move.start_file == 0:
                    self.current_castling_right.wqs = False
                elif move.start_file == 7:
                    self.current_castling_right.wks = False
        elif move.piece_moved == 'bR':
            if move.start_rank == 0:
                if move.start_file == 0:
                    self.current_castling_right.bqs = False
                elif move.start_file == 7:
                    self.current_castling_right.bks = False


    def get_valid_moves(self):
        # for log in self.castle_rights_log:
        #     print(log.wks, log.wqs, log.bks, log.bqs)
        temp_enpassant_possible = self.enpassant_possible # save to temp because all moves calculated will change original
        temp_castle_rights = CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                          self.current_castling_right.wqs, self.current_castling_right.bqs)
        moves = self.get_all_possible_moves()

        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()
        if len(moves) == 0: # either checkmate or stalemate
            if self.in_check():
                self.checkmate = True
                print('CHECKMATE')
            else:
                self.stalemate = True
                print('STALEMATE')


        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        self.enpassant_possible = temp_enpassant_possible # bring original back from temp save
        self.current_castling_right = temp_castle_rights
        return moves
        #
        # else:
        #     self.checkmate = False
        #     self.stalemate = False

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, r, f):
        self.white_to_move = not self.white_to_move # switch to opponent's point of view
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move # switch turns / point of view back
        for move in opponent_moves:
            if move.end_rank == r and move.end_file == f:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for f in range(len(self.board[r])):
                turn_color = self.board[r][f][0]
                if (turn_color == 'w' and self.white_to_move) or (turn_color == 'b' and not self.white_to_move):
                    piece = self.board[r][f][1]
                    self.move_functions[piece](r, f, moves)
        return moves

    def get_pawn_moves(self, r, f, moves):
        if self.white_to_move:
            if self.board[r-1][f] == '--':
                moves.append(Move((r, f), (r-1, f), self.board))
                if r == 6 and self.board[r-2][f] == '--':
                    moves.append(Move((r, f), (r-2, f), self.board))

            if f-1 >= 0:
                if self.board[r-1][f-1][0] == 'b':
                    moves.append(Move((r, f), (r-1, f-1), self.board))
                elif (r-1, f-1) == self.enpassant_possible:
                    moves.append(Move((r, f), (r-1, f-1), self.board, is_enpassant_move=True))

            if f+1 < len(self.board[0]):
                if self.board[r-1][f+1][0] == 'b':
                    moves.append(Move((r, f), (r-1, f+1), self.board))
                elif (r-1, f+1) == self.enpassant_possible:
                    moves.append(Move((r, f), (r-1, f+1), self.board, is_enpassant_move=True))

        else: # black moves
            if self.board[r + 1][f] == '--':
                moves.append(Move((r, f), (r + 1, f), self.board))
                if r == 1 and self.board[r + 2][f] == '--':
                    moves.append(Move((r, f), (r + 2, f), self.board))

            if f-1 >= 0:
                if self.board[r+1][f-1][0] == 'w':
                    moves.append(Move((r, f), (r+1, f-1), self.board))
                elif (r+1, f-1) == self.enpassant_possible:
                    moves.append(Move((r, f), (r+1, f-1), self.board, is_enpassant_move=True))

            if f+1 < len(self.board[0]):
                if self.board[r+1][f+1][0] == 'w':
                    moves.append(Move((r, f), (r+1, f+1), self.board))
                elif (r+1, f+1) == self.enpassant_possible:
                    moves.append(Move((r, f), (r+1, f+1), self.board, is_enpassant_move=True))

    def get_rook_moves(self, r, f, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8): # max 7 squares moved
                end_rank = r + d[0] * i
                end_file = f + d[1] * i
                if 0 <= end_rank < 8 and 0 <= end_file < 8: # on board
                    end_piece = self.board[end_rank][end_file]
                    if end_piece == '--': # empty square
                        moves.append(Move((r, f), (end_rank, end_file), self.board))
                    elif end_piece[0] == enemy_color: # enemy piece on square
                        moves.append(Move((r, f), (end_rank, end_file), self.board))
                        break
                    else:
                        break # friendly piece on square -> invalid
                else: # off board
                    break

    def get_knight_moves(self, r, f, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for m in knight_moves:
            end_rank = r + m[0]
            end_file = f + m[1]
            if 0 <= end_rank < 8 and 0 <= end_file < 8:
                end_piece = self.board[end_rank][end_file]
                if end_piece[0] == enemy_color or end_piece[0] == '-': # not a friendly piece on the square
                    moves.append(Move((r, f), (end_rank, end_file), self.board))

    def get_bishop_moves(self, r, f, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1, 8):  # max 7 squares moved
                end_rank = r + d[0] * i
                end_file = f + d[1] * i
                if 0 <= end_rank < 8 and 0 <= end_file < 8:  # on board
                    end_piece = self.board[end_rank][end_file]
                    if end_piece == '--':  # empty square
                        moves.append(Move((r, f), (end_rank, end_file), self.board))
                    elif end_piece[0] == enemy_color:  # enemy piece on square
                        moves.append(Move((r, f), (end_rank, end_file), self.board))
                        break
                    else:
                        break  # friendly piece on square -> invalid
                else:  # off board
                    break

    def get_queen_moves(self, r, f, moves):
        self.get_rook_moves(r, f, moves)
        self.get_bishop_moves(r, f, moves)

    def get_king_moves(self, r, f, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (1, -1), (1, 0), (1, 1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for i in range(8):
            end_rank = r + king_moves[i][0]
            end_file = f + king_moves[i][1]
            if 0 <= end_rank < 8 and 0 <= end_file < 8:
                end_piece = self.board[end_rank][end_file]
                if end_piece[0] == enemy_color or end_piece[0] == '-':  # not a friendly piece on the square
                    moves.append(Move((r, f), (end_rank, end_file), self.board))
        # self.get_castle_moves(r, f, moves)


    def get_castle_moves(self, r, f, moves):
        if self.square_under_attack(r, f):
            return # can't castle when in check
        if (self.white_to_move and self.current_castling_right.wks) or (not self.white_to_move and self.current_castling_right.bks):
            self.get_kingside_castle_moves(r, f, moves)
        if (self.white_to_move and self.current_castling_right.wqs) or (not self.white_to_move and self.current_castling_right.bqs):
            self.get_queenside_castle_moves(r, f, moves)


    def get_kingside_castle_moves(self, r, f, moves):
        if self.board[r][f+1] == '--' and self.board[r][f+2] == '--':
            if not self.square_under_attack(r, f+1) and not self.square_under_attack(r, f+2):
                moves.append(Move((r, f), (r, f+2), self.board, is_castle_move=True))


    def get_queenside_castle_moves(self, r, f, moves):
        if self.board[r][f-1] == '--' and self.board[r][f-2] == '--' and self.board[r][f-3] == '--':
            if not self.square_under_attack(r, f-1) and not self.square_under_attack(r, f-2):
                moves.append(Move((r, f), (r, f-2), self.board, is_castle_move=True))

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):
        self.start_rank = start_sq[0]
        self.start_file = start_sq[1]
        self.end_rank = end_sq[0]
        self.end_file = end_sq[1]
        self.piece_moved = board[self.start_rank][self.start_file]
        self.piece_captured = board[self.end_rank][self.end_file]

        self.is_pawn_promotion = (self.piece_moved =='wp' and self.end_rank == 0) or (self.piece_moved == 'bp' and self.end_rank == 7)
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'
        self.is_castle_move = is_castle_move

        self.move_id = self.start_rank * 1000 + self.start_file * 100 + self.end_rank * 10 + self.end_file

    """Overriding equals method"""
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False


    def write_chess_notation(self):
        return self.get_rank_file(self.start_rank, self.start_file) + self.get_rank_file(self.end_rank, self.end_file)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

# COMP30024 Artificial Intelligence, Semester 1 2019
# Solution to Project Part A: Searching

# Authors: Hong Ngoc Do and Teun Petersen

import sys
import json
import queue as Q

def main():
    with open(sys.argv[1]) as file:
        data = json.load(file)

        #determine colour
        # 0 = red, 1 = blue, 2 = green; red + x, blue + y, green + z
        if data["colour"] == "red":
            colour = 0
        elif data["colour"] == "blue":
            colour = 1
        elif data["colour"] == "green":
            colour = 2

        #convert to cubic coordinates
        positions = tuple([(p[0], -p[0] - p[1], p[1]) for p in data["pieces"]])
        blocks = [(p[0], -p[0] - p[1], p[1]) for p in data["blocks"]]


        path = aStar(positions, colour, blocks)

        #printing
        bdict = {}
        for p in path:
            print(moveFormat(p[2], p[0], p[1]))
            bdict[(p[2][0], p[2][2])] = p[1]

        for b in data["blocks"]:
            bdict[tuple(b)] = "block"
        print_board(bdict, "", True)


def axial2cube(p):
    #convert axial to cube coordinates
    return (p[0], -p[0] - p[1], p[1])


def cube2axial(p):
    #convert cube to axial coordinates
    return (p[0], p[2])


def heuristic(state, move, colour):
    #compute heuristic for move in a certain state
    h = 0
    for piece in state[1]:
        if piece == move[2]:
            h += heuristicPerPiece(move[0], colour)
        else:
            h += heuristicPerPiece(piece, colour)
    return h


def heuristicPerPiece(point, colour):
    # if position empty (node exited heuristic =0)
    if not point:
        return 0

    destination = getGoalPosition(colour)
    # moves to end zone + one for exiting
    return abs(point[colour] - destination[colour]) / 2 + 1


def aStar(start_pos, colour, board_dict):
    # A* search algorithm
    q = Q.PriorityQueue()
    # Queue's element = (costSoFar+heurisitc, [currentPositions], [arrayOfMoves])
    q.put((0, start_pos, []))
    # dictionary keeping track of quickest routes to states
    costSoFar = {start_pos: 0}

    while not q.empty():
        state = q.get()

        # expand all moves for this state
        possibleMoves = getPossibleMoves(state[1], board_dict, colour)

        # break if no moves possible all pieces gone through exit
        if not possibleMoves:
            # print(state[2])
            return state[2]

        # calculating priorities for all moves and adding them to the queue
        for move in possibleMoves:

            # Path length at new state
            newCost = costSoFar[state[1]] + 1

            # Positions at new state
            newPosList = list(state[1])
            newPosList.remove(move[2])
            newPosList.append(move[0])
            newPosTuple = tuple(sorted(newPosList))

            # Add to queue if new state or if route is more efficient than previous known routes
            if newPosTuple not in costSoFar or costSoFar[newPosTuple] > newCost:
                costSoFar[newPosTuple] = newCost

                #f = c + h
                priority = newCost + heuristic(state, move, colour)

                # pathSoFar = path so far + new path
                pathSoFar = list(state[2])
                pathSoFar.append(move)

                #add new state to queue
                q.put((priority, newPosTuple, pathSoFar))


def getGoalPosition(colour):
    # returns position of goal
    if (colour == 0):
        return (3, 0, 0)
    if (colour == 1):
        return (0, 3, 0)
    if (colour == 2):
        return (0, 0, 3)


def getGoal(statePos, colour):
    return statePos[colour] == 3


def moveFormat(point1, point2, action):
    # returns formatted string for the output
    if action == "EXIT":
        return "EXIT from " + str(cube2axial(point1)) + "."
    else:
        return action + " from " + str(cube2axial(point1)) + " to " + str(cube2axial(point2)) + "."


def exitFormat(point):
    return "EXIT from " + point + ". \n"


def getPossibleMoves(positions, board_dict, colour):
    feasible_moves = []
    blocked = list(board_dict)
    for p in positions:
        blocked.append(p)

    for start_pos in positions:

        # if no starting position (after exit)
        if not start_pos:
            continue

        # all directions a piece can move in
        directions = [(1, -1, 0), (1, 0, -1), (0, 1, -1), (-1, 1, 0), (-1, 0, 1), (0, -1, 1)]
        moves = [((start_pos[0] + d[0], start_pos[1] + d[1], start_pos[2] + d[2]), "MOVE", start_pos) for d in
                 directions]

        # if space is occupied add jump
        for i, m in enumerate(moves):
            if m[0] in blocked:
                jumppos = (moves[i][0][0] + directions[i][0], moves[i][0][1] + directions[i][1],
                           moves[i][0][2] + directions[i][2])
                moves[i] = (jumppos, "JUMP", start_pos)



        # check if all moves still on board and not blocked
        for mv in moves:
            m = mv[0]
            if max((m[0], m[1], m[2])) <= 3 and min((m[0], m[1], m[2])) >= -3:
                if m not in blocked:
                    feasible_moves.append(mv)

        #If in endzone add exit action
        if start_pos[colour] == 3:
            feasible_moves.append(((), "EXIT", start_pos))

    return feasible_moves


def print_board(board_dict, message="", debug=False, **kwargs):
    """
    Helper function to print a drawing of a hexagonal board's contents.

    Arguments:

    * `board_dict` -- dictionary with tuples for keys and anything printable
    for values. The tuple keys are interpreted as hexagonal coordinates (using
    the axial coordinate system outlined in the project specification) and the
    values are formatted as strings and placed in the drawing at the corres-
    ponding location (only the first 5 characters of each string are used, to
    keep the drawings small). Coordinates with missing values are left blank.

    Keyword arguments:

    * `message` -- an optional message to include on the first line of the
    drawing (above the board) -- default `""` (resulting in a blank message).
    * `debug` -- for a larger board drawing that includes the coordinates
    inside each hex, set this to `True` -- default `False`.
    * Or, any other keyword arguments! They will be forwarded to `print()`.
    """

    # Set up the board template:
    if not debug:
        # Use the normal board template (smaller, not showing coordinates)
        template = """# {0}
#           .-'-._.-'-._.-'-._.-'-.
#          |{16:}|{23:}|{29:}|{34:}|
#        .-'-._.-'-._.-'-._.-'-._.-'-.
#       |{10:}|{17:}|{24:}|{30:}|{35:}|
#     .-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
#    |{05:}|{11:}|{18:}|{25:}|{31:}|{36:}|
#  .-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-.
# |{01:}|{06:}|{12:}|{19:}|{26:}|{32:}|{37:}|
# '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#    |{02:}|{07:}|{13:}|{20:}|{27:}|{33:}|
#    '-._.-'-._.-'-._.-'-._.-'-._.-'-._.-'
#       |{03:}|{08:}|{14:}|{21:}|{28:}|
#       '-._.-'-._.-'-._.-'-._.-'-._.-'
#          |{04:}|{09:}|{15:}|{22:}|
#          '-._.-'-._.-'-._.-'-._.-'"""
    else:
        # Use the debug board template (larger, showing coordinates)
        template = """# {0}
#              ,-' `-._,-' `-._,-' `-._,-' `-.
#             | {16:} | {23:} | {29:} | {34:} |
#             |  0,-3 |  1,-3 |  2,-3 |  3,-3 |
#          ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#         | {10:} | {17:} | {24:} | {30:} | {35:} |
#         | -1,-2 |  0,-2 |  1,-2 |  2,-2 |  3,-2 |
#      ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
#     | {05:} | {11:} | {18:} | {25:} | {31:} | {36:} |
#     | -2,-1 | -1,-1 |  0,-1 |  1,-1 |  2,-1 |  3,-1 |
#  ,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-.
# | {01:} | {06:} | {12:} | {19:} | {26:} | {32:} | {37:} |
# | -3, 0 | -2, 0 | -1, 0 |  0, 0 |  1, 0 |  2, 0 |  3, 0 |
#  `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#     | {02:} | {07:} | {13:} | {20:} | {27:} | {33:} |
#     | -3, 1 | -2, 1 | -1, 1 |  0, 1 |  1, 1 |  2, 1 |
#      `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' `-._,-'
#         | {03:} | {08:} | {14:} | {21:} | {28:} |
#         | -3, 2 | -2, 2 | -1, 2 |  0, 2 |  1, 2 | key:
#          `-._,-' `-._,-' `-._,-' `-._,-' `-._,-' ,-' `-.
#             | {04:} | {09:} | {15:} | {22:} |   | input |
#             | -3, 3 | -2, 3 | -1, 3 |  0, 3 |   |  q, r |
#              `-._,-' `-._,-' `-._,-' `-._,-'     `-._,-'"""

    # prepare the provided board contents as strings, formatted to size.
    ran = range(-3, +3 + 1)
    cells = []
    for qr in [(q, r) for q in ran for r in ran if -q - r in ran]:
        if qr in board_dict:
            cell = str(board_dict[qr]).center(5)
        else:
            cell = "     "  # 5 spaces will fill a cell
        cells.append(cell)

    # fill in the template to create the board drawing, then print!
    board = template.format(message, *cells)
    print(board, **kwargs)


# when this module is executed, run the `main` function:
if __name__ == '__main__':
    main()

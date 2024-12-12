from collections import deque
start = (1,1)
directions = [(-1, 0, "Up"), (1, 0, "down"), (0, -1, "left"), (0, 1, "right")]
instructions = []
def print_maze():
    for row in wallmaze:
        print(' '.join(row))
 
def journy(start, end, maze): #define function shortest_path( starting value in the list of lists (x,y) and the end value in the lol (x,y) and then the maze it is tasked with finding.
    paths = [] #   define paths as a list
    visited = set() #create a set for visitied coords in the maze
    rows = len(maze) #initiate the rows and colomns of the maze
    cols = len(maze[0])
    instructions.clear()
    def bfs(start, end):
        queue = deque() # this means that it is a double ended queue, this is good for bfs because of its "efficency of popping elemenst from the front of the queue {POPPING~~~}
        queue.append((start, [start]))  # it initialized by adding the starting position 'start'. the second part of the tuple is a list [start] that keeps track of the path taken so far , this starts with only the start position.
        visited.add(start)# this adds any visited positions to the set, preventing it from repeating steps and forming an infinite loop

        while queue: # main loop in the bfs algorithem and it runs for as long as there are elements in the queue. que stores position and path taken to it  
            curr, path = queue.popleft() # curr = pos on grid and path is path too it (list of coords listing from start to curr) both curr and path are queue.poplefted, meaning they are removed from the queue
            if curr == end: # means that if the current coord is the end coord then you are at the end of the maze
                paths.append(path) # if you have found the end of the maze then save the list of coordinated that got you there to the list of paths. 
            else:
                i, j = curr # if you have not reached the end then change the curr coords to the values i&j representing x&y in the maze.

                for dx, dy, direction in directions:# ittereates over the diretions list containint the tuples fro positble movments up down ect. each direction if representide as change in coords dx &dy.
                    new_i, new_j = i + dx, j + dy

                    if 0 <= new_i < rows and 0 <= new_j < cols and (new_i, new_j) not in visited and maze[new_i][new_j] == " ": # this checks if the new coords is within the bounds of the maze by no of rows and colmns & if the new position have not been visited before and that the value found there is " "( not "#" witch would represent a wall)
                        visited.add((new_i, new_j))# add the coords to the visited list 
                        queue.append(((new_i, new_j), path + [(new_i, new_j)])) # the new position and the updated path are added to the queue. this positoin and the path to it allow for bfs to track the shortest route

    bfs(start, end) ##calls for a bfs between the two coordinates
    
    if paths: # it checks if there are any paths found between start and finish.
        min_path_index = min(range(len(paths)), key=lambda i: len(paths[i])) #
        shortest_path = paths[min_path_index] #retreves the list of coordingates corisponding to the path of shortest distance and assignes it to variable
        shortest_path_global = shortest_path
        
        # Provide step-by-step instructions       
        for i in range(1, len(shortest_path)):
            prev = shortest_path[i - 1]
            curr = shortest_path[i]
            for dx, dy, direction in directions:
                if (curr[0] - prev[0], curr[1] - prev[1]) == (dx, dy):
                    instructions.append(direction)

        # Print the instructions
        print("Instructions to complete the maze:")
        for instruction in instructions:
            print(instruction)
                 
        for i in shortest_path:
            maze[i[0]][i[1]] = "X" # this goes through all coord values in the list and changes there value in the maze to an x to indicate that that is the path taken 
        print(shortest_path)
        print_maze()
        for i in shortest_path:
            maze[i[0]][i[1]] = " "
        
def turn_right():
    global orientation
    right_turns = {"u" : "r", "r" : "d", "d" : "l", "l" : "u"}
    orientation = right_turns[orientation]
def turn_left():
    global orientation
    left_turns = {"u": "l", "l": "d", "d": "r", "r": "u"}    
    orientation = left_turns[orientation]
def turn_away():
    global orientation
    away_turns = {"u": "d", "d": "u", "r": "l", "l": "r"}
    orientation = away_turns[orientation]
def move_forward():
    global i, j, orientation
    moves = {
        "u" : (i-1, j),
        "d" : (i+1, j),
        "r" : (i, j+1),
        "l" : (i, j-1)
    }
    new_i, new_j = moves[orientation]
    if wallmaze[new_i][new_j] == " ":
        i, j = new_i, new_j
    else:
        print("Cannot move forward; a wall is blocking the way.")
    
def get_sensors():
    # Take sensor input
    try:
        frnt_snsr = int(input('front sensor (0 or 1):  '))
        rght_snsr = int(input('right sensor (0 or 1):  '))
        lft_snsr = int(input('left sensor (0 or 1):  '))
        return frnt_snsr, rght_snsr, lft_snsr
    except ValueError:
        print('Invalid input. Defaulting to NO walls.')
        frnt_snsr = rght_snsr = lft_snsr = 0
        return 0, 0, 0

def add_walls(i, j, orientation, maze, north=False, east=False, south=False, west=False):

    frnt_snsr, rght_snsr, lft_snsr = get_sensors()
    
    #determining the sensors according to the orientation. u : Up. d : down. r : right. l : left.
    if orientation == "u":
        # Convert to boolean values for walls
        north = bool(frnt_snsr)
        east = bool(rght_snsr)
        west = bool(lft_snsr)
        south = False
        if north == True:
            maze[i-1][j] = "#"
        if west == True:
            maze[i][j-1] = "#"
        if east == True:
            maze[i][j+1] = "#"
    elif orientation == "d":
        north = False
        east = bool(lft_snsr)
        west = bool(rght_snsr)
        south = bool(frnt_snsr)
        if south == True:
            maze[i+1][j] = "#"
        if east == True:
            maze[i][j+1] = "#"
        if west == True:
            maze[i][j-1] = "#"
        
    elif orientation == "r":
        north = bool(lft_snsr)
        east = bool(frnt_snsr)
        west = False
        south = bool(rght_snsr)
        if east == True:
            maze[i][j+1] = "#"
        if north == True:
            maze[i-1][j] = "#"
        if south == True:
            maze[i+1][j] = "#"
    elif orientation == "l":
        north = bool(rght_snsr)
        east = False
        west = bool(frnt_snsr)
        south = bool(lft_snsr)
        if west == True:
            maze[i][j-1] = "#"
        if south == True:
            maze[i+1][j] = "#"
        if north == True:
            maze[i-1][j] = "#"
    else:
        print("Invalid input. No walls set.")
   
    # Loop to allow input from the user to update the maze

wallmaze = [
    ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", " ", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#"],
    ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],            
]

(i, j) = start
orientation = "d"
print("Current position:", (i, j))
print("orientation is: " + orientation)
print_maze()
add_walls(i, j, orientation, wallmaze)
print_maze()
journy((i,j), (13,13), wallmaze)

while True:
    
    if orientation == "u":
        if instructions[0] == "up":
            move_forward()
        elif instructions[0] == "down":
            turn_away()
            move_forward()
        elif instructions[0] == "left":
            turn_left()
            move_forward()
        elif instructions[0] == "right":
            turn_right()
            move_forward()
    elif orientation == "d":
        if instructions[0] == "down":
            move_forward()
        elif instructions[0] == "up":
            turn_away()
            move_forward()
        elif instructions[0] == "right":
            turn_left()
            move_forward()
        elif instructions[0] == "left":
            turn_right()
            move_forward()
    elif orientation == "l":
        if instructions[0] == "left":
            move_forward()
        elif instructions[0] == "right":
            turn_away()
            move_forward()
        elif instructions[0] == "down":
            turn_left()
            move_forward()
        elif instructions[0] == "up":
            turn_right()
            move_forward()
    elif orientation == "r":
        if instructions[0] == "right":
            move_forward()
        elif instructions[0] == "left":
            turn_away()
            move_forward()
        elif instructions[0] == "down":
            turn_right()
            move_forward()
        elif instructions[0] == "up":
            turn_left()
            move_forward()
           
    print("New Orientation is: " + orientation)
    print("Current position:", (i, j))
    add_walls(i, j, orientation, wallmaze)
    print_maze()
    wallmaze[i][j] = "0"
    print_maze()
    wallmaze[i][j] = " "
    journy((i,j), (12,12), wallmaze)

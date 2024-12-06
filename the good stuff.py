from collections import deque

def journy(start, end, maze): #define function shortest_path( starting value in the list of lists (x,y) and the end value in the lol (x,y) and then the maze it is tasked with finding.
    paths = [] #   define paths as a list
    visited = set() #create a set for visitied coords in the maze
    rows = len(maze) #initiate the rows and colomns of the maze
    cols = len(maze[0])
    
    # Directions for moving up, down, left, and right
    directions = [(-1, 0, "Up"), (1, 0, "Down"), (0, -1, "Left"), (0, 1, "Right")]#define the directions that corispond to positional change differences within the maze (ie up = (-1,0)

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
        instructions = [] # initialised an empty list ro store the step by step directions
        
        for i in shortest_path:
            maze[i[0]][i[1]] = "X" # this goes through all coord values in the list and changes there value in the maze to an x to indicate that that is the path taken 
        for row in maze:
            print(' '.join(row))
        print(shortest_path)
        
# Example Maze
maze = [
    ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
    ["#", " ", " ", " ", " ", " ", "#", " ", " ", " ", "#", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#", " ", "#"],
    ["#", " ", "#", " ", "#", "#", "#", "#", "#", " ", "#", " ", "#", " ", "#", "#", "#", "#", "#", "#", "#", " ", "#", " ", "#"],
    ["#", " ", "#", " ", " ", " ", "#", " ", " ", " ", "#", " ", "#", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#", " ", "#"],
    ["#", " ", "#", "#", "#", " ", "#", " ", "#", "#", "#", " ", "#", "#", "#", "#", "#", "#", "#", " ", "#", " ", " ", " ", "#"],
    ["#", " ", " ", " ", "#", " ", " ", " ", "#", " ", "#", " ", "#", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#", " ", "#"],
    ["#", "#", "#", " ", "#", "#", "#", " ", "#", " ", "#", " ", "#", " ", "#", "#", "#", "#", "#", "#", "#", " ", "#", " ", "#"],
    ["#", " ", "#", " ", " ", " ", "#", " ", " ", " ", "#", " ", "#", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#", " ", "#"],
    ["#", " ", "#", "#", "#", " ", "#", "#", "#", " ", "#", " ", "#", "#", "#", "#", "#", "#", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", "#", " ", " ", " ", "#", " ", " ", " ", "#", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#", " ", "#"],
    ["#", " ", "#", "#", "#", "#", "#", " ", "#", "#", "#", "#", "#", "#", "#", " ", "#", "#", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", " ", " ", "#", " ", " ", " ", "#", " ", "#", " ", " ", " ", "#", " ", "#", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", "#", "#", " ", "#", " ", " ", " ", "#", " ", "#", " ", "#", "#", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", " ", " ", "#", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#", " ", " ", " ", "#", " ", "#", " ", "#"],
    ["#", " ", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", " ", "#", "#", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", "#", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#", " ", " ", " ", " ", " ", "#", " ", " ", " ", "#", " ", "#"],
    ["#", " ", "#", " ", "#", "#", "#", "#", "#", "#", "#", " ", "#", "#", "#", " ", "#", " ", "#", "#", "#", "#", "#", " ", "#"],
    ["#", " ", "#", " ", " ", " ", " ", " ", " ", " ", "#", " ", " ", " ", "#", " ", "#", " ", " ", " ", " ", " ", "#", " ", "#"],
    ["#", " ", "#", "#", "#", "#", "#", "#", "#", " ", "#", "#", "#", " ", "#", "#", "#", " ", "#", "#", "#", " ", "#", " ", "#"],
    ["#", " ", "#", " ", " ", " ", "#", " ", "#", " ", " ", " ", "#", " ", " ", " ", " ", " ", "#", " ", "#", " ", "#", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", " ", "#", "#", "#", " ", "#", "#", "#", "#", "#", " ", "#", " ", "#", "#", "#", " ", "#"],
    ["#", " ", "#", " ", "#", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#"],
    ["#", " ", "#", " ", "#", " ", "#", "#", "#", "#", "#", "#", "#", " ", "#", "#", "#", "#", "#", "#", "#", " ", "#", " ", "#"],
    ["#", " ", " ", " ", "#", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "#", " ", "#"],
    ["#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#", "#"],
    
    
]

journy((1,23), (13,13), maze)# 13,13 should be good enough for the center of the maze. shoudlnt be an issue if its is not the coord closes to the center however.                                                                                           
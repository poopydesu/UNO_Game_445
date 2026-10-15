#!/usr/bin/env python
# coding: utf-8

# ### CS445 - AI - Fall 2026
# ### Maze 2D Search Problem - HW#2 --- Implement similar to Lab#3
# ### Dr. Trung T. Nguyen
# ### This Python code formulates the maze search problem.

import matplotlib.pyplot as plt
from matplotlib import colors
from collections import deque

# define the MazeNode class
class MazeNode:
    def __init__(self, state, parent, depth, cost, key):
        self.state = state    # current state
        self.parent = parent  # the parent node
        self.depth = depth    # the depth value
        self.cost = cost      # path cost so far
        self.key = key        # the key
    def __eq__(self, other):
        return self.state == other.state
    def __lt__(self, other):
        return self.state < other.state

# define Maze2DProblem class that formulate the maze searching problem with required methods
class Maze2Dproblem:
    def __init__(self, grid, start, goal):
        """Initialize internal variables. The grid is a 2D matrix. Each tile can have the following values
        0: Empty tile, 1: Wall, 2: start tile, 3: goal tile, 4: tiles in the path from start to goal
        """
        self.grid = grid                        # the grid represent the maze cells data
        self.grid[start[0]][start[1]] = 2       # start tile
        self.grid[goal[0]][goal[1]] = 3         # goal tile
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.initial_state = start              # the initial tile coordinate (xS,yS)
        self.goal_state = goal                  # the goal tile coordinate (xE,yE)
        self.goal_node = None                   # game node default as None
        self.nodes_expanded = 0                 # number of expanded nodes so far
        self.max_search_depth = 0               # the maximum search depth
        self.max_frontier_size = 0              # the maximum size of queue (frontier)
    
    def draw(self, showPath=False):
        """Draw the maze using matplotlib - white is empty tile and black for wall
            green -> start tile, red -> goal tile, orange -> tile in the path
        """
        fig, ax = plt.subplots()
        if not showPath:
            cmap = colors.ListedColormap(['white','black', 'green', 'red'], N=4)
        else:
            cmap = colors.ListedColormap(['white','black', 'green', 'red', 'orange'], N=5)
        im = ax.imshow(self.grid, cmap=cmap)
        plt.show()
        
    def move(self, curPos, direction):
        """Return new tile position if valid move
           curPos: is the current cell position - a tuple of (x,y)
           direction: the direction we try to move to: 1 - UP, 2-DOWN, 3-LEFT, 4-RIGHT
           This method should return the new cell position if the moving action is valid
           For example, if the curPos=(x,y) and direction=1 (UP) is valid => return (x-1,y)
        """
        # TODO 1: implement this method below
        x, y = curPos
        if direction == 1:    # Up
            new_x, new_y = x - 1, y
        elif direction == 2:  # Down
            new_x, new_y = x + 1, y
        elif direction == 3:  # Left
            new_x, new_y = x, y - 1
        elif direction == 4:  # Right
            new_x, new_y = x, y + 1
        else:
            return None

        if 0 <= new_x < self.rows and 0 <= new_y < self.cols:
            if self.grid[new_x][new_y] != 1:  # 1 represents wall
                return (new_x, new_y)

        return None
    
    def expand(self, node):
        """Expand the given node to new new neighbor nodes by trying all possible moves"""
        self.nodes_expanded += 1
        neighbors = list()
        # Test UP
        neighbors.append(MazeNode(self.move(node.state, 1), node, node.depth + 1, node.cost + 1, 0))
        # Test DOWN
        neighbors.append(MazeNode(self.move(node.state, 2), node, node.depth + 1, node.cost + 1, 0))
        # Test Left
        neighbors.append(MazeNode(self.move(node.state, 3), node, node.depth + 1, node.cost + 1, 0))
        # Test RIGHT
        neighbors.append(MazeNode(self.move(node.state, 4), node, node.depth + 1, node.cost + 1, 0))
        # get the list of possible neighbor nodes after trying to move in fourth direction
        nodes = [neighbor for neighbor in neighbors if neighbor.state]
        return nodes 
    
    def backtrace(self):
        """Backtrace the path from goal node to initial node to get the list of moves"""
        path = list()
        current_node = self.goal_node
        while self.initial_state != current_node.parent.state:
            path.insert(0, current_node.parent.state)
            current_node = current_node.parent
        return path
    
    def bfs(self):
        """Perform BFS from the initial cell to goal cell"""
        # 1. Create the root node starting at the initial coordinate
        root = MazeNode(self.initial_state, parent=None, depth=0, cost=0, key=0)

        # 2. Track visited coordinates to prevent revisiting tiles/infinite loops
        explored = {self.initial_state}

        # 3. Initialize FIFO queue (the frontier) with the root node
        queue = deque([root])

        # 4. Search loop: continue while there are unvisited nodes in the frontier
        while queue:
            # Track peak frontier size for performance metrics
            self.max_frontier_size = max(self.max_frontier_size, len(queue))

            # Pop the oldest node from the front of the queue (FIFO)
            node = queue.popleft()

            # Goal test: check if current node is the target location
            if node.state == self.goal_state:
                self.goal_node = node
                return queue  # Return remaining frontier upon success

            # Expand current node by generating valid orthogonal neighbors
            for neighbor in self.expand(node):
                # Only process neighbors that haven't been visited or enqueued yet
                if neighbor.state not in explored:
                    explored.add(neighbor.state)  # Mark neighbor as visited
                    queue.append(neighbor)        # Add to the end of the queue

        return None  # Return None if frontier empties without reaching goal
    
    def astar(self):
        # TODO 3: implement this method below
        explored = set()     # Set of processed/expanded state coordinates
        heap = []             # Min-heap priority queue storing (f_score, tie_breaker, node)
        heap_entry = {}       # Maps state (x, y) -> best tuple entry in heap for quick updates
        counter = 0           # Unique integer sequence to break priority ties in min-heap

        # 1. Calculate heuristic f = g + h = 0 + h(start) for initial state
        initial_f_score = self.h(self.initial_state)
        root = MazeNode(self.initial_state, parent=None, depth=0, cost=0, key=initial_f_score)

        # 2. Create priority queue entry: tuple ordering sorts by f_score, then tie-breaker
        entry = (initial_f_score, counter, root)
        heapq.heappush(heap, entry)
        heap_entry[root.state] = entry

        # 3. Search loop: continue while priority queue contains unexpanded nodes
        while heap:
            # Track peak frontier size for performance metrics
            self.max_frontier_size = max(self.max_frontier_size, len(heap))

            # Pop node with the lowest f_score f(n) = g(n) + h(n)
            _, _, curr_node = heapq.heappop(heap)

            # Skip node if we've already expanded a shorter path to this state
            if curr_node.state in explored:
                continue

            # Mark current state as permanently expanded
            explored.add(curr_node.state)

            # Goal test: check if lowest cost node pulled is the destination
            if curr_node.state == self.goal_state:
                self.goal_node = curr_node
                return heap  # Return remaining frontier upon success

            # Generate neighbors for valid moves (Up, Down, Left, Right)
            for neighbor in self.expand(curr_node):
                # Skip if state is already in closed list (fully expanded)
                if neighbor.state in explored:
                    continue

                # Compute f_score = g(n) [accumulated cost] + h(n) [estimated distance to goal]
                neighbor.key = neighbor.cost + self.h(neighbor.state)

                counter += 1  # Increment sequence counter for unique heap comparison
                entry = (neighbor.key, counter, neighbor)

                # Add neighbor if unseen, or update if a lower f_score path is found
                if neighbor.state not in heap_entry or neighbor.key < heap_entry[neighbor.state][0]:
                    heap_entry[neighbor.state] = entry
                    heapq.heappush(heap, entry)

        return None  # Return None if no solution path exists
        return None

# create a sample maze
grid = [[1,1,0,1,0,0,1,1,0,1,0,0],
        [0,0,0,0,1,0,0,0,0,0,0,0],
        [0,0,1,0,0,0,1,1,1,0,1,0],
        [0,0,0,1,0,0,1,0,1,0,1,0],
        [0,1,0,1,1,0,1,0,1,0,0,0],
        [0,1,0,0,1,0,0,0,0,0,1,0]]

# create a maze problem and draw the initial state
maze = Maze2Dproblem(grid, (1,0), (4,10))
maze.draw()
    
# try BFS or A* to search and draw the solution
frontier = maze.bfs()
#frontier = maze.astar()
if frontier is None:
    print('No solution found!!!')
else:
    path = maze.backtrace()
    for move in path:
        maze.grid[move[0]][move[1]] = 4
    maze.draw(True)


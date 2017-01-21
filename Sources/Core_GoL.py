# -*- coding: utf-8 -*-
import Tkinter as tk
from os import getcwd
from os.path import join
import random
import ast

configuration = {"colors": ["white", "black", "red", "blue"]}
configuration["rules"] = [{"born": 3, "lower": 2, "upper": 3} for x in range(len(configuration["colors"]))]

color_list = ["white", "black", "red", "blue", "dark green", "orange", "purple", "pink", "yellow", "peach puff",
              "firebrick", "royal blue", "chocolate", "turquoise", "gold", "sienna", "green", "deep pink", "cyan"]


def keypress(event):
    if not (str.isalnum(event.char) or event.char == "\b"):
        return 'break'


def generate_empty_grid(size, nei=False):
    """
    This function generates an empty square grid (i.e. made only of 0's). The size of the grid is chosen by the user.
    :param nei: Boolean to check if the grid generated needs to be a triple nested to represent the empty grid of
    neighbour count.
    :param size: the length of the grid's sides. (width = height)
    :return: A 2D list containing only 0's representing the initial state (no live cell).
    """
    empty_grid = [[0] * size for _ in range(size)]
    # For loop because simply multiplying a list to reproduce it would cause python to consider all sub-lists to be the
    # same item and any modification would apply to all the sub-lists.
    if nei:
        for width in range(0, len(empty_grid)):
            for height in range(0, len(empty_grid[width])):
                empty_grid[width][height] = [0] * len(configuration["colors"])
                # Iterates over lines and columns to generate a list of 0's from each cell. This list is as long as
                # the number of colors there are in configuration. This will allow to store different neighbours.
    return empty_grid


def get_neighbour(state):
    """
    This function calculates the number of live neighbours for each cell on the grid.
    :param state: This is the list containing all the states live/dead of the cells
    :return: A list with the same structure as the input list is returned. However, instead of representing the state
    (0/1), the values represent the number of living neighbours for each cell.
    """
    count_neigh = generate_empty_grid(len(state), True)
    # Generates an empty grid for neighbour counting, same size as the game grid.

    for i in range(0, len(state)):
        # Iterates over each line of the game grid
        for j in range(len(state[i])):
            # Iterates over each column within the line of the game grid
            for x in range(i - 1, i + 2):
                # Iterates vertically over each neighbour of the current cell.
                if 0 <= x < len(state):
                    # Prevents the iterations from exiting the upper and lower borders of the game grid.
                    for y in range(j - 1, j + 2):
                        # Iterates horizontally over neighbours of the current cell.
                        if 0 <= y < len(state[x]) and not (state[x][y] == 0 or (x == i and y == j)):
                            # Prevents the iterations from exiting the left and right borders of the game grid.
                            # Adding 1 neighbour to the count if the neighbour is alive and not on the
                            # same position as the cell in game grid (cannot be a neighbour of itself).
                            count_neigh[i][j][state[x][y]] += 1
                            # The count is added to the corresponding color. (for example if the color of the
                            # neighbouring cell is red, its state is 2. It will then add a count to the index 2 in the
                            # list for the cell in [i][j] in neighbour count.
    return count_neigh


def process_changes(count_neigh, grid, hybridization=False):
    """
    This function processes the new number of live cells in the grid, based on a set of rules. The modifications are
    directly applied on the input grid.
    :param hybridization: blabla
    :param count_neigh: This is a 2D list containing the number of live neighbours for each cell. This list is obtained
    with the get_neighbour(state) function.
    :param grid: This is the grid containing all the states of the cells (0/1). The modifications are directly applied
    on this list.
    :return: The returned grid is simply the same list that has been used as an input, after modifications.
    (0/1), the values represent the number of living neighbours for each cell.
    """
    for i in range(0, len(grid)):
        # Iterating over lines in the grid.
        for j in range(0, len(grid[i])):
            # Iterating over columns in a line of the grid.
            result_neighbor = [0] * len(configuration["colors"])
            # Generates a temporary list containing booleans for each colors, indicating if the cell should be of that
            # color at the next iteration.
            for x in range(1, len(configuration["colors"])):
                # Iterating over colors.
                if not grid[i][j] == x and count_neigh[i][j][x] == configuration["rules"][x]["born"]:
                    # If the cell is not of tht color, and the number of surrounding cell of that color is equal to the
                    # number required for birth.
                    result_neighbor[x] = 1
                    # It should become (be born) that color on the next iteration.

                elif (configuration["rules"][x]["lower"] <= count_neigh[i][j][x] <= configuration["rules"][x]["upper"]) \
                        and grid[i][j] == x:
                    # Else, if the cell is of that color and it has enough neighbouts of the same color to survive, and
                    # less than the overpopulation limit.
                    result_neighbor[x] = 1
                    # It should stay of that color (survive) in the next iteration.

                else:
                    result_neighbor[x] = 0
                    # Otherwise, it should not be of that color in the next iteration.
            for index in range(1, len(configuration["colors"])):
                # Iterating over colors
                if hybridization:
                    # If in hybridization mode
                    if index > 2 and result_neighbor[index] and result_neighbor[index - 2]:
                        # If the color has a higher index than 2 and there is more than 0 neighbours of that color as
                        # well as more than 0 neighbours of the color with an index inferior by 2
                        grid[i][j] = index - 1
                        # The cell will take the color with an index between the two colors.(hybridization)
                    elif result_neighbor[index]:
                        # Else, the cell will
                        grid[i][j] = index
                else:
                    # If in competition mode.
                    if result_neighbor[index]:
                        # If there are neighbours of this color
                        grid[i][j] = index
                        # The cell will become the color of the last index.
                if not sum(result_neighbor):
                    grid[i][j] = 0
                    # If there are not any neighbours of any colors, the cell will die/stay empty.
    return grid


class MainWindow(tk.Frame):  # creates the main window
    """
    This class contains all the elements of the game. It consists of a window made of two frames: the game frame and the
    options frame.
    """
    var_hybrid = False
    # This variable defines if the cells are hybridizing or in competition.
    seed_store = {}  # Dictionary containing the save for all the seeds in the text file.
    game_grid = []
    game_state = False  # Safety
    game_to_stop = False  # Variable used to stop an ongoing simulation
    win_open = {"op": False, "sw": False}  # Boolean used to know if the Windows are open (Seeds or Settings).
    ite_incre = 0  # Number defining the current iteration
    options_label = [0] * len(configuration["colors"])
    # Will contain the frames of the configuration["colors"] names that will be displayed next to the options.
    options_born = [0] * len(configuration["colors"])
    # List stocking the frames of the minimum number of similar neighbours required to be born for each color
    options_lower = [0] * len(configuration["colors"])
    # List stocking the frames the minimum number of similar neighbours required to for each cell color to survive.
    options_upper = [0] * len(configuration["colors"])
    # List stocking the frames the number of similar neighbours above which the cell dies of overpopulation.
    label_title = [0] * len(configuration["rules"][1])

    # Serves to stock the labels informing the user about the options described above.

    def __init__(self, *args, **kwargs):
        """
        This function is run automatically whenever the MainWindow class is called. This is the constructor.
        :param args: Optional arguments
        :param kwargs: Optional named arguments that have not been named in advance such as f(a=7).
        :return: Creates the interface when called.
        """
        tk.Frame.__init__(self, *args, **kwargs)
        # Main frame generated on class call
        self.options_frame = tk.Frame(self)
        # Frame containing all the game options
        self.options_frame.grid(sticky="w", column=1, row=1)
        self.game_frame = tk.Frame(self, width=600, height=600)
        self.game_frame.grid(sticky="w", column=1, row=2)
        # .grid manages the placement of the option frame, placing it on an invisible grid. The same method will be used
        # for all widgets in the class.
        self.value = tk.StringVar(self)
        self.value.set(str.upper(configuration["colors"][1]))
        # Default value generation for the OptionMenu in the options_frame.
        """
        Creation of every buttons in options_frame
        """
        self.button_create = tk.Button(self.options_frame, cursor="hand2", text="Create Grid",
                                       command=self.create).grid(row=1, column=2)
        # Button to create the Grid, the function used will take the value in self.size_entry as the size of the grid.
        self.button_stop = tk.Button(self.options_frame, cursor="hand2", text="Stop Simulation",
                                     command=self.stop).grid(sticky="e", row=1, column=6)
        # If a simulation is running, this button stops it.
        self.button_start = tk.Button(self.options_frame, cursor="hand2", text="Start Simulation",
                                      command=self.iterate_sim).grid(row=1, column=5)

        """
        Creation of the rest of the widgets
        Labels serve to inform the user
        Entries allow the user to insert data
        Spinbox allows the user to select a value from a predefined set of values.
        """
        self.lab_grid_size = tk.Label(self.options_frame,
                                      text="Size of the Grid :")  # Entry To choose the size of the grid wanted
        self.lab_grid_size.grid(sticky="e", row=1)

        self.size_entry = tk.Entry(self.options_frame, bd=2, width=5)
        # Entry To choose the desired size of the grid.
        self.size_entry.grid(row=1, column=1)
        self.size_entry.insert(0, 60)
        self.lab_time = tk.Label(self.options_frame,
                                 text="Iteration time (ms):")
        self.lab_time.grid(sticky="e", row=2, column=3)
        self.time_entry = tk.Entry(self.options_frame, bd=2, width=4)
        # Entry To choose the time between iterations in milliseconds.
        self.time_entry.grid(row=2, column=4, sticky="w")
        self.time_entry.insert(0, 25)
        # Default value is 25ms

        self.n_ite = tk.DoubleVar(self.options_frame)
        # Number of iterations wanted
        self.lab_iterations = tk.Label(self.options_frame, text="Iterations :")
        self.lab_iterations.grid(sticky="w", row=1, column=3)

        self.slider_size = tk.Scale(self.options_frame, variable=self.n_ite, from_=1, to=400, sliderlength=20,
                                    orient="horizontal")
        self.slider_size.grid(row=1, column=4)
        # Slider to chose the grid size

        self.drop_menu_cell_type = tk.OptionMenu(self.options_frame, self.value,
                                                 *[string.upper() for string in configuration["colors"]])
        self.drop_menu_cell_type.grid(row=2, column=1, columnspan=2, sticky="w")
        self.label_cell_color = tk.Label(self.options_frame, text="Cell Color :")
        self.label_cell_color.grid(row=2, column=0, sticky="w")
        # Creates a dropdown menu to chose cell color.

        self.label_cell_n_color = tk.Label(self.options_frame, text="N of Colors :")
        self.label_cell_n_color.grid(row=2, column=4, sticky="e")
        self.spinbox_cell_n_color = tk.Spinbox(self.options_frame, width=4, from_=1, to=len(color_list))
        self.spinbox_cell_n_color.grid(row=2, column=5, sticky="w")
        # Creates a spinbox to chose the total number of colors to be used.

        self.button_cell_n_color = tk.Button(self.options_frame, cursor="hand2", text="Change",
                                             command=lambda: self.change_color())
        self.button_cell_n_color.grid(row=2, column=5, sticky="e")
        # Changes updates the number of colors based on the value currently displayed in the spinbox at the moment it is
        # pushed.
        self.spinbox_cell_n_color.delete(0, "end")
        self.spinbox_cell_n_color.insert(0, 3)
        # Default number of colors is 4.
        self.label_hybrid = tk.Label(self.options_frame, text="Hybrid:").grid(row=2, column=6, sticky="w")
        self.checkbox_hybrid = tk.Checkbutton(self.options_frame, command=lambda: self.change_hybrid())
        self.checkbox_hybrid.grid(row=2, column=6, sticky="e")
        # This check box will allow hybridization between color if checked. Otherwise the colors will just compete
        # following a priority order (their order in the list); for example if an empty tile is surrounded by 3 black
        # cells and 3 red cells, it will become red becomes red is the color number 2 while black is number 1 (2>1).

        self.load_seeds()
        # Now that most widgets have been generated on the main window, the seeds are loaded from a text file into the
        # dictionary.
        """
        Creation of the Custom Seeds FileMenu
        """
        self.menu_bar = tk.Menu(self.options_frame)
        # Fancy Menu Bar
        self.seeds_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.refresh_seeds_menu()
        self.menu_bar.add_cascade(label="Seeds", menu=self.seeds_menu)
        # First tab allows to select predefined seeds.
        """
        Creation of the Custom options Filemenu
        """
        self.options_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.options_menu.add_separator()
        self.options_menu.add_command(label="Settings", command=lambda: self.window_options())
        # Opens a new window in which the user can change the birth/survival rules for each cell type
        self.options_menu.add_separator()
        self.menu_bar.add_cascade(label="Options", menu=self.options_menu)

        root.config(menu=self.menu_bar)
        # Adds the menu to the mainwindow

        """
        Creation of the credits
        """
        self.credit_frame = tk.Frame(self)
        self.credit_frame.grid(sticky="sw", column=1, row=3)
        self.label_credits = tk.Label(self.credit_frame, text=u"Julien Dénéréaz, Cyril Matthey-Doret and Cédric Leroux| 2016").grid(row=0,
                                                                                                              column=0)

        self.create()

    def change_hybrid(self):
        """
        This method changes the hybrid value. This boolean variable defines if cells can hybridize or not.
        reminder: hybridization is when an empty cell can become both a cell of color x and a cell of color x+2 and
        instead becomes a cell of color x+1.
        """
        self.var_hybrid = not self.var_hybrid

    def iterate_sim(self):
        """
        This command goes through each iteration while calculating the next generation and apply the changes to the
        grid. It is called when the user presses the button 'Start Simulation'.
        """
        if not self.game_state:
            self.save_seed({"AutoSave": self.game_grid})
            # At the moment the user starts a simulation, an autosave of the current grid is generated. This feature
            # allows the user to retrieve a seed that generated an interesting pattern.

        if self.game_to_stop and self.game_state:
            # The method will not do anything if the user pressed the 'Stop' button (game_to_stop = True)
            # while the game is running (game_state = True). It will stop the game from running.
            self.game_to_stop = False
            self.game_state = False
            return
        self.game_state = True
        # Game is running.
        if self.ite_incre < int(self.n_ite.get()):
            # If the current iteration has not reached the desired maximum number chosen with the slider.
            if not self.ite_incre:
                # If we are at iteration 0, we need to create the file data.txt
                graph_file = open(join(getcwd(),"data.txt"), 'w')
                graph_file.write("Iteration")
                graph_file.close()
                graph_file = open(join(getcwd(), "data.txt"), 'a')
                # After writing "Iteration" in this data.txt, we add every name of colors in the current simulation
                for color in range(1, len(configuration["colors"])):
                    graph_file.write(" " + str.upper(configuration["colors"][color].replace(" ", "")))
                graph_file.write("\n")
                graph_file.close()
            graph_file = open(join(getcwd(), "data.txt"), 'a')
            graph_file.write(str(self.ite_incre + 1))
            for color in range(1, len(configuration["colors"])):
                n = 0
                for i in range(0, len(self.game_grid)):
                    # Iterates over each line of the game grid
                    for j in range(0, len(self.game_grid[i])):
                        if self.game_grid[i][j] == color:
                            n += 1
                graph_file.write(" " + str(n))
            graph_file.write("\n")
            # Before closing the file, we create the table showing the population of each color. We add a line at each
            # iteration of the simulation
            graph_file.close()
            self.game_grid = process_changes(get_neighbour(self.game_grid), self.game_grid, self.var_hybrid)
            # Calculates number of neighbours and process the changes. This line only works with nested lists.
            self.update_grid()
            # Apply changes to the canvas.
            self.ite_incre += 1
            # Sets current iteration as iteration n+1
            self.after(int(self.time_entry.get()), self.iterate_sim)
            # Wait before next iteration, the time is taken from the current value entered in the entry in milliseconds.
        else:
            # If the iteration number (self.ite_incre) has reached nmax (self.nite)
            self.ite_incre = 0
            # Iteration number is reset
            self.game_state = False
            # Game stops running

    def create(self):
        """
        This command is called when the user push the "Create grid" button. It will get the size of the grid.
        It generates a new, empty grid of states and a corresponding canvas grid.
        """
        self.stop()
        # If a simulation is running, it will be stopped.
        try:
            gridsize = int(self.size_entry.get())
            # Takes the value entered in the "Grid size" entry as the value of the grid size.
        except ValueError:
            # If user is not very smart and enter something else than a number an appropriate error message is displayed
            # in the console and the grid is not created.
            self.alert("Please enter an Integer !")
            return
        self.game_grid = []
        self.game_grid = generate_empty_grid(gridsize)
        # Creation of the list containing state of every cells (all empty by default).
        self.game_frame.destroy()
        # Clean the previous grid by removing the frame.
        self.game_frame = tk.Frame(self)
        self.game_frame.grid(sticky="w", column=1, row=2)
        # Creates a new frame in the mainwindow. This frame is placed below the option frame and will only contain the
        # game grid.
        self.canvas_grid = tk.Canvas(self.game_frame, width=10 * gridsize, height=10 * gridsize, highlightthickness=0,
                                     relief="ridge", bg="white")
        # The canvas size will be 10 times that of the grid size. This unit is in pixel, meaning each cell will be 10X10
        self.canvas_grid.pack()
        self.update_grid()
        # Filling the frame with a white canvas that will act as the grid.
        self.canvas_grid.bind("<Button 1>", self.get_coord)
        # This line allows to capture the coordinates when the user clicks somewhere on the canvas. <Button 1> refers
        # to the mouse left click.
        self.canvas_grid.bind("<B1-Motion>", self.get_coord)
        # This line allows to capture the coordinates when the user click-draw somewhere on the canvas. <B1-Motion>
        # refers to the mouse left click being pressed and mouse moving.

    def get_coord(self, event):
        """
        Gets the mouse coordinates when the user clicks the canvas and transforms them into rows/columns in the game
        grid.
        :param event: a tkinter object with x and y coordinates.
        """
        if int(event.x / 10) >= len(self.game_grid) or int(event.y / 10) >= len(self.game_grid):
            return
        # Because of the canvas generation, there is 1 line/column dead pixel on the right and on the bottom of the
        # canvas, so we need to check if it's clicked in this dead line/column pixel
        self.toggle(int(event.x / 10), int(event.y / 10))
        # The canvas coordinates span from 0 to 10 times the number of rows or columns. Each cell is 10X10 pixel large.
        # The coordinates on which the user clicks are here transformed into rows and column by dividing the mouse
        # coordinates by 10. For example, if the user clicks on (49, 13) (pixel units), the integer division will
        # transform the pixels into rows columns by rounding to the inferior integer = (4, 1).

    def toggle(self, row, column):
        """
        This method allows to change the canvas background every time it is called. The row and column targeted will be
        transformed in pixels, and the area will change background corresponding to the value in the "Cell type" spinbox
        at the moment this function is called (when the user clicks the canvas).
        :param row: Row of the grid to be changed.
        :param column: Column of the grid to be changed.
        """
        if self.game_state:
            return
        # If a simulation is currently running, toggle will do nothing, meaning it will have no effect when the user
        # clicks on the canvas.
        self.game_grid[row][column] = configuration["colors"].index(str.lower(self.drop_menu_cell_type.cget("text")))
        self.canvas_grid.create_rectangle(row * 10, column * 10,
                                          10 + (row * 10), 10 + (column * 10), outline="",
                                          fill=str.lower(self.drop_menu_cell_type.cget("text")))
        # Otherwise, it will change the state of the cell on which the function is called to the value selected in the
        # cell type drop menu. It will also change the color of the corresponding canvas area to the color matching the
        # index of the string of the drop menu.

    def random_seed(self, grid):
        """
        Generates random states for every cell in the current grid.
        :param grid: Grid of state.
        """
        for i in range(0, len(grid)):
            # Iterating over lines in the grid.
            for j in range(0, len(grid[i])):
                # Iterating over columns in a line of the grid.
                grid[i][j] = random.randint(0, len(configuration["colors"]) - 1)
                # Every cell in the grid is assigned a random state in the colour list.
        self.update_grid()
        # The randomized grid is passed to the update_grid method to apply changes to the canvas.

    def update_grid(self):
        """
        This method updates the color of the canvas grid  using the values in the grid of states.
        :return: The updated canvas.
        """
        self.canvas_grid.delete(tk.ALL)
        # Deletes all rectangles existing on the canvas.
        for i in range(0, len(self.game_grid)):
            for j in range(0, len(self.game_grid[i])):
                # Loops through lines and columns of the grid of states.
                if configuration["colors"][self.game_grid[i][j]] != "white":
                    self.canvas_grid.create_rectangle(10 * i, 10 * j, (10 * i) + 10, (10 * j) + 10, outline="",
                                                      fill=configuration["colors"][self.game_grid[i][j]])
                    # For each cell, creates a rectangle on the canvas, with a color corresponding to the state in the
                    # game grid.

    def import_seed(self, seed_name):
        """
        This method applies the seed chosen by the user to both the grid of states and the canvas grid.
        :param seed_name: The name of the seed to import
        """
        self.load_seeds()
        self.size_entry.delete(0, "end")
        # Deletes the current value in the entry defining the size of the grid.
        self.size_entry.insert(0, len(self.seed_store[seed_name]["seed"]))
        # Insert a new value corresponding to the length of the grid of the desired seed in the same entry.
        self.create()
        # An empty grid of states and a corresponding grid of buttons is generated using the value in self.size_entry.
        self.game_grid = self.seed_store[seed_name]["seed"]
        configuration["rules"] = self.seed_store[seed_name]["rules"]
        configuration["colors"] = self.seed_store[seed_name]["colors"]
        self.update_colors()
        # The empty grid of states is replaced by the grid of the seed
        self.update_grid()
        # The buttons are updated according to the new grid of states.

    def save_seed(self, my_seed):
        """
        This method should save the seed on which it is called into the text file and create a new command in the seed
        menu of the main window, allowing the user to import it.
        :param my_seed: a dictionary with a single entry. The key is the name of the seed, the value is its state grid.
        """
        self.load_seeds()
        for name in my_seed:
            if not str(name) == "AutoSave":
                if str(name) in self.seed_store:
                    # If the seed already exists in the seed_store dictionary, it is not saved again, but displays an
                    # alert message instead.
                    self.alert("This name already exists !")
                    return
            if str(name) == "":
                self.alert("Emtpy String !")
                # Displays another alert message if the name is empty
                return
            self.seed_store[str(name)] = {"colors": configuration["colors"], "rules": configuration["rules"],
                                          "seed": my_seed[name]}
            # If none of those case happened, the function proceeds normally and adds the seed to the seed_store
            # dictionary. Note if this is an autosave, it will erase the previous autosave.
        self.write_file()
        self.refresh_seeds_menu()
        # Writing the new seed into the seeds.txt file and refreshing the dropdown menu.

        if self.win_open["sw"]:
            self.sw.destroy()
            # Closes the seed management window
            self.win_open["sw"] = False
            # Declares it is closed

    def load_seeds(self):
        """
        This method loads the seeds from the text file and stores it in the seed_store dictionary.
        """
        try:
            seed_file = open(join(getcwd(), "seeds.txt"), 'r')
            # Tries to open the file called seeds.txt in the same directory as the program in read mode.
            seed_string = seed_file.read()
            # Reads the file content and assigns it to a variable as a string.
            self.seed_store = ast.literal_eval(seed_string)
            # This function detects the dictionary structure in the file and converts the string into a dictionary
            # object. This dictionary object is stored in the seed_store.
            seed_file.close()

        except IOError:
            # Calls this method, creating a new file.
            seed_file = open(join(getcwd(), "seeds.txt"), 'w')
            # In case there was no file called seeds.txt in the directory, a new empty file is created.
            seed_file.close()
            self.restore_seed()
            # This function call will rewrite the new file from a backup file.

    def restore_seed(self):
        """
        This method retrieves the original seeds from the backup file and stores this data inside a dictionary. It then
        calls another method to rewrite the seeds.txt file from this dictionary.
        :return:
        """
        default_file = open(join(getcwd(), "default.txt"), 'r')
        default_string = default_file.read()
        # Storing the original seeds in the backup file as a string.
        self.seed_store = ast.literal_eval(default_string)
        # Transforming the string into a dictionary.
        default_file.close()
        self.write_file()
        # Rewrite seeds.txt with the content of the seed_store dictionary.
        try:
            self.refresh_seeds_menu()
            # Updates the options in the seeds_menu with the new seeds.
        except:
            self.do_nothing()
        if self.win_open["sw"]:
            self.sw.destroy()
            # If the seeds management window is open, it is closed.
        self.win_open["sw"] = False
        # States the seeds management window is closed.
        self.load_seeds()

    def remove_seed(self, seed_name):
        """
        Removes a seed from the seedstore dictionary and rewrite the seeds.txt file from the dictionary, thereby
        removing that seed from the file as well.
        :param seed_name: The name of the seed to be removed.
        """
        del self.seed_store[str(seed_name)]
        self.write_file()

    def write_file(self):
        """
        Writes the seed_store dictionary into the seeds.txt file.
        """
        seed_file = open(join(getcwd(), "seeds.txt"), 'w')
        seed_file.write(str(self.seed_store))
        seed_file.close()

    def refresh_seeds_menu(self):
        """
        Refreshes the options in the seeds menu, based on the current content of the seed_store dictionary.
        """
        self.seeds_menu.delete(0, self.seeds_menu.index("end"))
        # Removes all options in the menu.
        self.seeds_menu.add_separator()
        self.seeds_menu.add_command(label="Manage seeds", command=lambda: self.seed_window())
        self.seeds_menu.add_separator()
        self.seeds_menu.add_command(label="Random Seed Generation", command=lambda: self.random_seed(self.game_grid))
        self.seeds_menu.add_separator()
        for name in self.seed_store:
            self.seeds_menu.add_command(label=str(name), command=lambda s=name: self.import_seed(s))
        self.seeds_menu.add_separator()

    def seed_window(self):
        """
        This method creates a new window containing options to change the rules of birth/survival. It is called when the
        user pushes the "Settings" button in the "options" menu.
        """
        if not (self.win_open["sw"] or self.win_open["op"]):
            # If the seed_window or the seeds management windows are not already open.
            self.win_open["sw"] = True
            # States the seed window is open.
            self.sw = tk.Toplevel()
            # Opens the seed window
            self.sw.title("Seed manager")
            self.sw.protocol('WM_DELETE_WINDOW', self.close_option)
            # If the window is closed using the red cross on the top right, the close option method is called.
            self.lab_seedlist = tk.Label(self.sw, text="List of seeds").grid(column=0, row=0)
            self.lab_newseed = tk.Label(self.sw, text="Enter your seed name: ").grid(column=1, row=0)
            self.entry_newseed = tk.Entry(self.sw, bd=2, width=10)
            self.entry_newseed.bind("<KeyPress>", keypress)
            # Only lets the user enters letters and numbers
            self.entry_newseed.grid(column=2, row=0)
            self.button_save = tk.Button(self.sw, text="Save seed",
                                         command=lambda: self.save_seed({str(self.entry_newseed.get()): self.game_grid}
                                                                        )).grid(column=2, row=1)
            self.button_reset = tk.Button(self.sw, text="Restore seeds",
                                          command=lambda: self.restore_seed()).grid(column=2, row=2)
            self.list_to_remove = [[0] * 2 for _ in range(len(self.seed_store))]
            # List of seeds to remove 0 means "do not remove", 1 means "remove"
            i = 0
            for n in self.seed_store:
                self.list_to_remove[i][0] = tk.IntVar()
                # If the checkboxes are checked, their value will be 1, if left unchecked, it will be 0
                self.list_to_remove[i][1] = n
                tk.Checkbutton(self.sw, text=str(n), variable=self.list_to_remove[i][0]).grid(row=i + 1, column=0,
                                                                                              sticky='w')
                i += 1
                self.check_rmseed = tk.Button(self.sw, text="Remove seed",
                                              command=lambda: self.ite_removal(self.list_to_remove)) \
                    .grid(row=len(self.seed_store) + 2, column=0)
                # This button will remove the checked seeds and refresh the seed management window.

    def ite_removal(self, rm_list):
        """
        Takes a list of seeds names associated with 1 or 0 values. Every seed that has its name associated with a
        non-zero value is removed from the seed_store dictionary and the seeds.txt file.
        :param rm_list: List of seeds to be removed.
        """
        for k in range(len(rm_list)):
            if rm_list[k][0].get():
                self.remove_seed(rm_list[k][1])
        self.sw.destroy()
        self.win_open["sw"] = False
        self.seed_window()
        self.refresh_seeds_menu()

    def stop(self):
        """
        This method changes causes the game to stop at the next iteration (iterate_sim())if a simulation is running.
        """
        if self.game_state:
            self.game_to_stop = True
            self.ite_incre = 0

    def window_options(self):
        """
        Opens a new window containing various widgets for the user to change the birth/survival rules individually for
        each cell type.
        """
        if not (self.win_open["op"] or self.win_open["sw"]):
            # If the option window and the seeds management window are closed, the method proceeds normally. Otherwise
            # it does nothing. This avoids having multiple instances of the option windows opened at the same time.
            self.win_open["op"] = True
            # States the option window is opened
            self.wo = tk.Toplevel()
            # Opens the option window
            self.wo.title("Settings")
            self.wo.protocol('WM_DELETE_WINDOW', self.close_option)
            # In case the user closes the window with the red cross on the top right, the close_option method is called.
            # this allows to declare the window is closed.
            self.label_title_color = tk.Label(self.wo, text="Cell Types").grid(column=1, row=0)
            self.label_title[0] = tk.Label(self.wo, text="Born").grid(column=2, row=0)
            self.label_title[1] = tk.Label(self.wo, text="Lower").grid(column=3, row=0)
            self.label_title[2] = tk.Label(self.wo, text="Upper").grid(column=4, row=0)
            # Generates labels to inform the user on what the widgets do.
            for x in range(1, len(configuration["colors"])):
                # Iterates over colors, creating 3 spinboxes for each color.
                self.options_label[x] = tk.Label(self.wo, text=str.upper(configuration["colors"][x]) + " :") \
                    .grid(column=1, row=x, padx=4, pady=5, sticky="w")
                self.options_born[x] = tk.Spinbox(self.wo, from_=1, to=8, width=5)
                self.options_born[x].grid(column=2, row=x, padx=4, pady=5)
                self.options_born[x].delete(0, "end")
                self.options_born[x].insert(0, configuration["rules"][x]["born"])
                self.options_lower[x] = tk.Spinbox(self.wo, from_=1, to=8, width=5)
                self.options_lower[x].grid(column=3, row=x, padx=4, pady=5)
                self.options_lower[x].delete(0, "end")
                self.options_lower[x].insert(0, configuration["rules"][x]["lower"])
                self.options_upper[x] = tk.Spinbox(self.wo, from_=1, to=8, width=5)
                self.options_upper[x].grid(column=4, row=x, padx=4, pady=5)
                self.options_upper[x].delete(0, "end")
                self.options_upper[x].insert(0, configuration["rules"][x]["upper"])
                # Stores spinbox values in lists that will be used to define new rules. The default values of the
                # spinboxes are those in the current configuration dictionary.
            self.button_save = tk.Button(self.wo, text="Save and Close", command=lambda: self.close_option(True)) \
                .grid(column=2, columnspan=2, row=len(configuration["colors"]) + 1)
            # This button allows to save all rules into the configuration dictionary.

    def close_option(self, save=False):
        """
        This method will close any open option window and declare it is closed.
        :param save: If this parameter is set to True, the method will save the options values before closing the
        window.
        """
        if save:
            try:
                for x in range(1, len(configuration["colors"])):
                    if not int(self.options_lower[x].get()) <= int(self.options_upper[x].get()):
                        self.alert("Lower value has to be smaller than Upper value !")
                        return
                    configuration["rules"][x]["born"] = int(self.options_born[x].get())
                    configuration["rules"][x]["lower"] = int(self.options_lower[x].get())
                    configuration["rules"][x]["upper"] = int(self.options_upper[x].get())
                    # For each color, the rules are updated in the configuration dictionary.
            except ValueError:
                self.alert("Please enter an Integer !")
                # Error message in case there is a non numeric value in one of the spinboxes.
                return
        if self.win_open["op"]:
            self.wo.destroy()
            self.win_open["op"] = False
        if self.win_open["sw"]:
            self.sw.destroy()
            self.win_open["sw"] = False
            # Closes the option windows in case they are open, and declares they are closed.

    def change_color(self):
        """
        This method is called when the user pushes the "change" button. It will update the list of colors in the
        configuration dictionary, according to the current value in the spinbox_cell_n_color spinbox.
        """
        try:
            int(self.spinbox_cell_n_color.get())
        except:
            self.alert("Please enter an Integer !")
            return
        if not (self.win_open["sw"] or self.win_open["op"]) and 1 <= int(self.spinbox_cell_n_color.get()) <= len(
                color_list) - 1:
            # The function will only proceed if all optional windows are closed and there are at least 2 colors, but not
            # more than the size of the color list in the spinbox.
            configuration["colors"] = color_list[0:int(self.spinbox_cell_n_color.get()) + 1]
            configuration["rules"] = [{"born": 3, "lower": 2, "upper": 3} for length in
                                      range(len(configuration["colors"]))]
            # The configuration dictionary is updated from the value in the spinbox.
            self.update_colors()
            self.create()
        elif int(self.spinbox_cell_n_color.get()) < 1:
            self.alert("Not enough Colors Selected !")
        else:
            self.alert("Too many Colors Selected !")

    def update_colors(self):
        """
        Updates the lengths of the list containing values for the different spinboxes for birth/survival rules. Also
        updates the dropdown menu listing the colors in the mainwindow.
        """
        self.options_label = [0] * len(configuration["colors"])
        self.options_born = [0] * len(configuration["colors"])
        self.options_lower = [0] * len(configuration["colors"])
        self.options_upper = [0] * len(configuration["colors"])
        self.label_title = [0] * len(configuration["rules"][1])
        self.drop_menu_cell_type.destroy()
        self.value.set(str.upper(configuration["colors"][1]))
        self.drop_menu_cell_type = tk.OptionMenu(self.options_frame, self.value,
                                                 *[string.upper() for string in configuration["colors"]])
        self.drop_menu_cell_type.grid(row=2, column=1, columnspan=2, sticky="w")
        # Refreshes the lists and the dropdown menu according to the new colors.

    def alert(self, message):
        """
        This method is used to open windows with warning/error messages in various situations.
        :param message: The content of the message to be displayed.
        """
        try:
            self.alert_win.destroy()
        except:
            self.do_nothing()
        self.alert_win = tk.Toplevel()
        # Opens the window
        self.alert_win.title("")
        self.label_alert1 = tk.Label(self.alert_win, text="Alert :", font="-weight bold").pack(pady=5)
        self.label_alert2 = tk.Label(self.alert_win, text=message).pack(pady=5)
        self.button_alert = tk.Button(self.alert_win, text="OK", command=lambda: self.alert_win.destroy(), width=10,
                                      height=1)
        # The OK button closes the window.
        self.button_alert.pack(pady=5)

    def quitt(self):
        """
        This function closes the main window and exits the program.
        """
        root.destroy()

    def do_nothing(self):
        # Used for debugging/unfinished widgets
        pass


if __name__ == "__main__":
    # When the program itself is started directly (not a function called as a module).
    root = tk.Tk()
    root.wm_title("Game of Life")
    # Title on the program bar.
    main = MainWindow(root)
    # Main is an instance of MainWindow.
    main.grid(row=1, column=1, padx=10, pady=10)
    root.mainloop()
    # Gets the window running.

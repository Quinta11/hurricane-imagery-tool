from matplotlib.colors import LinearSegmentedColormap

def create_cmap(name, colors, nodes=None):
    if nodes is None:
        nodes = [i / (len(colors) - 1) for i in range(len(colors))]
    return LinearSegmentedColormap.from_list(name, list(zip(nodes, colors)))

cmaps = {
    "rbtop3": create_cmap("rbtop3", 
                          ["purple", "pink", "white", "black", "red", "yellow", "lightgreen", "blue", "lightblue", "white", "black"], 
                          [0.0, 0.077, 0.077, 0.154, 0.231, 0.308, 0.385, 0.462, 0.538, 0.538, 1.0]),
    "quinir": create_cmap("quinir", 
                          ["sienna", "orange", "khaki", "saddlebrown", "goldenrod", "lightgoldenrodyellow", "lightseagreen", "paleturquoise", "lightsteelblue", "royalblue", "black"], 
                          [0.0, 0.077, 0.077, 0.154, 0.231, 0.308, 0.385, 0.462, 0.538, 0.538, 1.0]),
    "swir": create_cmap("swir", 
                          ["white", "black"], 
                          [0.0, 1.0]),
    "xmas": create_cmap("xmas", 
                          ["yellow", "white", "#F5E9C4", "#AB2929", "white", "#df8080", "#0C4A0B", "#611028", "black", "white", "black"], 
                          [0.0, 0.077, 0.077, 0.154, 0.231, 0.308, 0.385, 0.462, 0.538, 0.538, 1.0]),
    "usrg": create_cmap("usrg", 
                          ["#ffffff", "#000000", "#800080", "#FFBDBD", "#E80000", "#ffff00", "#008000", "#003300", "#000080", "#0000FF", "#00ffff", "#EAEAEA", "#b9b9b9", "#000000", "#000000"], 
                          [0/155, 10/155, 15/155, 20/155, 30/155, 44/155, 52/155, 57/155, 65/155, 65/155, 75/155, 85/155, 95/155, 130/155, 155/155]),

}
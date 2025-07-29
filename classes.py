import json
import enum
import numpy as np
class StarSize(enum.IntEnum):
    O = 0
    B = 1
    A = 2
    F = 3
    G = 4
    K = 5
    M = 6

class Star:

    def __init__(
            self, 
            name:str="Sol", 
            x:int=0, 
            y:int=0, 
            id:int=1, 
            color:tuple[int, int, int]=(255, 255, 255), 
            colorHex:str="#FFFFFF", 
            radius:float=1.0
        ):
        self.name : str = name
        self.x : int = x
        self.y : int = y
        self.id : int = id
        self.color : tuple[int, int, int] = color
        self.colorHex : str = colorHex
        self.radius : float = radius
    
    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        my_dict = {}

        for attributeName in dir(self):
            if attributeName.endswith("__"):
                continue

            attribute = getattr(self, attributeName)
            if callable(attribute):
                continue

            my_dict[attributeName] = getattr(self, attributeName)
        return my_dict


class System:

    def __init__(self, name:str="Solar System", id:int=1, stars:list[Star]=None, warp_connections:list[int]=None, x:int=0, y:int=0):
        if stars is None:
            stars = []
        if warp_connections is None:
            warp_connections = []
        self.name = name
        self.id = id
        self.stars = stars
        self.warp_connections = warp_connections
        self.x = x
        self.y = y
        self.maxConnections = 6
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    def to_dict(self):
        my_dict = {}

        for attributeName in dir(self):
            if attributeName.endswith("__"):
                continue  
            if attributeName == "maxConnections":
                continue

            attribute = getattr(self, attributeName)
            if callable(attribute):
                continue

            my_dict[attributeName] = getattr(self, attributeName)
        
        # also, we need to turn stars into a dictionary as well.
        for index, star in enumerate(my_dict["stars"]):
            my_dict["stars"][index] = star.to_dict()
        
        return my_dict
    
    def distance(self, other:"System"):
        return np.sqrt(((self.x - other.x) ** 2)+ ((self.y - other.y) ** 2))
    
    def connect(self, other:"System"):
        if self.id in other.warp_connections or other.id in self.warp_connections:
            return
        self.warp_connections.append(other.id)
        other.warp_connections.append(self.id)


def distance(x1, y1, x2, y2):
    return np.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))


# credit to @AymericG on stackoverflow from this post: https://stackoverflow.com/questions/21977786/star-b-v-color-index-to-apparent-rgb-color
def bv2rgb(bv):
    if bv < -0.40: bv = -0.40
    if bv > 2.00: bv = 2.00

    r = 0.0
    g = 0.0
    b = 0.0

    if  -0.40 <= bv<0.00:
        t=(bv+0.40)/(0.00+0.40)
        r=0.61+(0.11*t)+(0.1*t*t)
    elif 0.00 <= bv<0.40:
        t=(bv-0.00)/(0.40-0.00)
        r=0.83+(0.17*t)
    elif 0.40 <= bv<2.10:
        t=(bv-0.40)/(2.10-0.40)
        r=1.00
    
    if  -0.40 <= bv<0.00:
        t=(bv+0.40)/(0.00+0.40)
        g=0.70+(0.07*t)+(0.1*t*t)
    elif 0.00 <= bv<0.40:
        t=(bv-0.00)/(0.40-0.00)
        g=0.87+(0.11*t)
    elif 0.40 <= bv<1.60:
        t=(bv-0.40)/(1.60-0.40)
        g=0.98-(0.16*t)
    elif 1.60 <= bv<2.00:
        t=(bv-1.60)/(2.00-1.60)
        g=0.82-(0.5*t*t)
    if  -0.40 <= bv<0.40:
        t=(bv+0.40)/(0.40+0.40)
        b=1.00
    elif 0.40 <= bv<1.50:
        t=(bv-0.40)/(1.50-0.40)
        b=1.00-(0.47*t)+(0.1*t*t)
    elif 1.50 <= bv<1.94:
        t=(bv-1.50)/(1.94-1.50)
        b=0.63-(0.6*t*t)
    

    return (round(r * 255), round(g * 255), round(b * 255))

# thank you stackoverflow! https://stackoverflow.com/questions/3380726/converting-an-rgb-color-tuple-to-a-hexidecimal-string
def rgb_to_hex(color:tuple[int, int, int]):
    return '#%02x%02x%02x' % color

if __name__ == "__main__":
    # tests star color
    '''
    import tkinter as tk

    root = tk.Tk()
    root.geometry("800x800")

    canvas = tk.Canvas(root, width=800, height=800)
    canvas.pack()

    for i, bv in enumerate(range(-4, 20, 1)):
        colorTuple = bv2rgb(bv/10)
        colorString = rgb_to_hex(colorTuple)
        canvas.create_rectangle(30 * i, 0, 30 * (i+1), 800, fill=colorString, outline=colorString)
    
    root.mainloop()
    '''
    # tests JSON
    '''
    mySystem = System("BigSystem", [])
    myStar = Star("Sol", 0, 0, 1, (255, 255, 255), "#FFFFFF", 1.0)
    mySecondStar = Star("Alpha", 1, 1, 2, (255, 0, 0), "#FF0000", 0.5)
    mySystem.stars = [myStar, mySecondStar]
    
    systemDict = json.loads(mySystem.to_json())
    for index, starString in enumerate(systemDict["stars"]):
        systemDict["stars"][index] = json.loads(starString)
    print(systemDict)
    '''
    # tests distance for System
    '''
    system1 = System(x=0, y=0)
    system2 = System(x=np.sqrt(2)/2, y=np.sqrt(2)/2)
    print(system1.distance(system2))
    '''

    

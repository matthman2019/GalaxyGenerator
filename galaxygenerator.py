import tkinter as tk
from random import uniform, randint, seed, shuffle
import random
from namegenerator import generate_random_name, weighted_randint, random_from_list
from classes import bv2rgb, rgb_to_hex, Star, StarSize, System, distance
import numpy as np
import json

# seed
universeSeed = 41
seed(universeSeed)

GALAXYRADIUS = 500
GALAXYCENTER = (0, 0)
SECTORDISTANCE = 20
SYSTEMAMOUNT = 4000
MAXCONNECTIONLENGTH = 25

# tkinter setup
root = tk.Tk()
root.geometry("810x810")
root.title("The Galaxy")
root.config(bg="black")
frame = tk.Frame(root, width=800, height=800)
frame.pack(expand=True, fill="both")
canvas = tk.Canvas(frame, width=1000, height=1000, bg='black', scrollregion=(-1000, -1000, 1000, 1000))
# we don't pack canvas yet!
scrollX = tk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
scrollX.pack(side="bottom", fill="x")
scrollY = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollY.pack(side='right', fill='y')
nameLabel = tk.Label(root, text="Names will be shown here!")
nameLabel.place(x=0, y=0)
# thanks, gemini!
def zoom(event, amount):
    canvas.scale("all", canvas.canvasx(event.x), canvas.canvasy(event.y), amount, amount)
canvas.pack(expand=True, fill='both')
canvas.bind("<Button-4>", lambda event: zoom(event, 1.01))
canvas.bind("<Button-5>", lambda event: zoom(event, 0.99))

canvas.configure(xscrollcommand=scrollX.set, yscrollcommand=scrollY.set)


# used to give stars individual ids
nextStarID = 1
def make_star(position:tuple[int, int]=(0, 0)) -> Star:
    global nextStarID
    starName = generate_random_name()
    harvardSpectral:StarSize = StarSize(weighted_randint((0, 0.001), (1, 0.05), (2, 0.149), (3, 0.1), (4, 0.15), (5, 0.25), (6, 0.3)))
    starColor = 0
    starSize = 0
    match harvardSpectral:
        case StarSize.O:
            starColor = bv2rgb(uniform(-0.4, -0.2))
            starSize = uniform(6.6, 10)
        case StarSize.B:
            starColor = bv2rgb(uniform(-0.2, 0.0))
            starSize = uniform(1.8, 6.6)
        case StarSize.A:
            starColor = bv2rgb(uniform(0.0, 0.3))
            starSize = uniform(1.4, 1.8)
        case StarSize.F:
            starColor = bv2rgb(uniform(0.3, 0.6))
            starSize = uniform(1.15, 1.4)
        case StarSize.G:
            starColor = bv2rgb(uniform(0.6, 0.9))
            starSize = uniform(0.96, 1.15)
        case StarSize.K:
            starColor = bv2rgb(uniform(0.9, 1.4))
            starSize = uniform(0.7, 0.96)
        case StarSize.M:
            starColor = bv2rgb(uniform(1.4, 2.0))
            starSize = uniform(0.3, 0.96)
        case _:
            raise Exception("Bad harvardSpectral! Make sure it is of type StarSize!")
    
    starColorHex = rgb_to_hex(starColor)

    id = nextStarID
    nextStarID += 1
    
    return Star(starName, position[0], position[1], id, starColor, starColorHex, starSize)

nextSystemID = 1
def make_system() -> System:
    global nextSystemID
    # make system's position
    x = float('inf')
    y = float('inf')
    while np.sqrt((x ** 2)+(y ** 2)) > GALAXYRADIUS:
        x = uniform(-GALAXYRADIUS, GALAXYRADIUS)
        y = uniform(-GALAXYRADIUS, GALAXYRADIUS)
    stars:list[Star] = []
    starAmount = weighted_randint((1, 0.4), (2, 0.5), (3, 0.09), (4, 0.01))
    systemName = None
    systemID = nextSystemID
    nextSystemID += 1
    for i in range(starAmount): 
        starToAppend = make_star((x, y))
        stars.append(starToAppend)
        if systemName is None:
            systemName = starToAppend.name
    
    stars.sort(key=lambda star: star.radius)
    return System(systemName, systemID, stars, [], x, y)

nameDict = {}
systemList:list[System] = []

# no sectors are used in the making of this galaxy.
# this can result in clumps!
def make_galaxy_with_no_sectors():
    global MAXCONNECTIONLENGTH, GALAXYCENTER, GALAXYRADIUS, SYSTEMAMOUNT
    
    print("Generating systems...")
    for i in range(4000):
        system = make_system()
        systemList.append(system)
    
            

    print("Making connections...")
    # make system connections
    for systemID, system in enumerate(systemList):
        totalConnections = weighted_randint((1, 0.1), (2, 0.15), (3, 0.4), (4, 0.3), (5, 0.05))
        system.maxConnections = totalConnections
        # totalConnections = ((GALAXYRADIUS - distance(system.x, system.y, GALAXYCENTER[0], GALAXYCENTER[1])) // 100) + 1
        currentConnections = len(system.warp_connections)
        # don't make more warp connections than we need to
        if currentConnections >= totalConnections:
            continue
        
        # get systems close to us (using taxicab distance)
        # if there aren't enough systems in MAXCONNECTIONLENGTH distance,
        # then add 5 to rangeBoost (increasing connectionRange) and try again.
        closeSystems:list[System] = []
        rangeBoost = 0
        while len(closeSystems) - currentConnections < totalConnections:
            # create a list of all systems closest to us
            for connectingSystem in systemList:
                connectionRange = MAXCONNECTIONLENGTH + rangeBoost
                if ((not (connectingSystem.x < system.x - connectionRange or
                    connectingSystem.x > system.x + connectionRange or
                    connectingSystem.y > system.y + connectionRange or
                    connectingSystem.y < system.y - connectionRange))
                    and connectingSystem != system
                    and len(connectingSystem.warp_connections) < connectingSystem.maxConnections + 1):
                    closeSystems.append(connectingSystem)
            
            rangeBoost += 5
            if rangeBoost > 1000:
                print("Hey we might have a problem", systemID)
        
        # shuffle(closeSystems)
        closeSystems.sort(key=lambda closeSystem: system.distance(closeSystem), reverse=False)
        while currentConnections < totalConnections:
            systemConnectingTo = closeSystems.pop()
            if systemConnectingTo in system.warp_connections:
                continue
            currentConnections += 1
            systemConnectingTo.warp_connections.append(system.id)
            system.warp_connections.append(systemConnectingTo.id)
            canvas.create_line(system.x, system.y, systemConnectingTo.x, systemConnectingTo.y, fill="blue")

            if len(closeSystems) == 0:
                break

    print("Drawing to screen...")
    for system in systemList:
        star = system.stars[0]
        x = system.x
        y = system.y

        canvasSize = np.ceil(star.radius / 2)
        color = star.colorHex
        if len(system.stars) == 4:
            color = "#00FF00"

        ovalID = canvas.create_oval(x-canvasSize, y-canvasSize, x+1+canvasSize, y+1+canvasSize, fill=color, outline=color)
        nameDict[ovalID] = system
        
        def show_name(event):
            global nameLabel
            system:System = nameDict[canvas.find_withtag("current")[0]]
            textToShow = f"{system.name} ({str(len(system.stars))} stars)"
            nameLabel.config(text = textToShow)
        canvas.tag_bind(ovalID, "<Enter>", show_name)

    print("Done!")
    canvas.create_oval(-GALAXYRADIUS, -GALAXYRADIUS, GALAXYRADIUS, GALAXYRADIUS, dash=(20, 20), outline="white")
    root.mainloop()

# some sectors are used in the making of this galaxy.
# systems will be relocated if the amount of systems in a sector exceeds systemsPerSector.
def make_galaxy_with_loose_sectors():
    global MAXCONNECTIONLENGTH, GALAXYCENTER, GALAXYRADIUS, SYSTEMAMOUNT
    # generate systems
    # sectorList is used to space out systems. If there are too many systems in a "sector", it will relocate.
    sectorAmountAxis = int(np.ceil((GALAXYRADIUS * 2) / SECTORDISTANCE))
    sectorList = [[[] for j in range(sectorAmountAxis)] for i in range(sectorAmountAxis)]
    sectorAmount = ((GALAXYRADIUS * 2) ** 2) // (SECTORDISTANCE ** 2)
    # the sectors form a square, but the galaxy is a circle! Not all sectors will be used.
    sectorUseAmount = np.ceil(sectorAmount * (np.pi / 4))
    # how many systems to expect per sector!
    systemsPerSector = int(np.ceil(SYSTEMAMOUNT / sectorUseAmount))
    sectorStartPos = (-GALAXYRADIUS, -GALAXYRADIUS)
    
    print("Generating systems...")
    for i in range(4000):
        system = make_system()
        systemList.append(system)

        # sector stuff
        successfulSectorPlacement = False
        attempts = 0
        while not successfulSectorPlacement:
            sector_x = int((system.x - sectorStartPos[0]) // SECTORDISTANCE)
            sector_y = int((system.y - sectorStartPos[1]) // SECTORDISTANCE)

            if len(sectorList[sector_x][sector_y]) < systemsPerSector:
                sectorList[sector_x][sector_y].append(system)
                successfulSectorPlacement = True
                break
            
            # if the sector is too full, replace!
            x = float('inf')
            y = float('inf')
            while np.sqrt((x ** 2)+(y ** 2)) > GALAXYRADIUS:
                x = uniform(-GALAXYRADIUS, GALAXYRADIUS)
                y = uniform(-GALAXYRADIUS, GALAXYRADIUS)
            system.x = x 
            system.y = y

            attempts += 1
            if attempts == 1000:
                print("We have issues")
                for row in sectorList:
                    for column in row:
                        print(len(column), end=' ')
                    print('\n')
    
            

    print("Making connections...")
    # make system connections
    for systemID, system in enumerate(systemList):
        totalConnections = weighted_randint((1, 0.1), (2, 0.15), (3, 0.4), (4, 0.3), (5, 0.05))
        system.maxConnections = totalConnections
        # totalConnections = ((GALAXYRADIUS - distance(system.x, system.y, GALAXYCENTER[0], GALAXYCENTER[1])) // 100) + 1
        currentConnections = len(system.warp_connections)
        # don't make more warp connections than we need to
        if currentConnections >= totalConnections:
            continue
        
        # get systems close to us (using taxicab distance)
        # if there aren't enough systems in MAXCONNECTIONLENGTH distance,
        # then add 5 to rangeBoost (increasing connectionRange) and try again.
        closeSystems:list[System] = []
        rangeBoost = 0
        while len(closeSystems) - currentConnections < totalConnections:
            # create a list of all systems closest to us
            for connectingSystem in systemList:
                connectionRange = MAXCONNECTIONLENGTH + rangeBoost
                if ((not (connectingSystem.x < system.x - connectionRange or
                    connectingSystem.x > system.x + connectionRange or
                    connectingSystem.y > system.y + connectionRange or
                    connectingSystem.y < system.y - connectionRange))
                    and connectingSystem != system
                    and len(connectingSystem.warp_connections) < connectingSystem.maxConnections + 1):
                    closeSystems.append(connectingSystem)
            
            rangeBoost += 5
            if rangeBoost > 1000:
                print("Hey we might have a problem", systemID)
        
        # shuffle(closeSystems)
        closeSystems.sort(key=lambda closeSystem: system.distance(closeSystem), reverse=False)
        while currentConnections < totalConnections:
            systemConnectingTo = closeSystems.pop()
            if systemConnectingTo in system.warp_connections:
                continue
            currentConnections += 1
            systemConnectingTo.warp_connections.append(system.id)
            system.warp_connections.append(systemConnectingTo.id)
            canvas.create_line(system.x, system.y, systemConnectingTo.x, systemConnectingTo.y, fill="blue")

            if len(closeSystems) == 0:
                break

    print("Drawing to screen...")
    for system in systemList:
        star = system.stars[0]
        x = system.x
        y = system.y

        canvasSize = np.ceil(star.radius / 2)
        color = star.colorHex
        if len(system.stars) == 4:
            color = "#00FF00"

        ovalID = canvas.create_oval(x-canvasSize, y-canvasSize, x+1+canvasSize, y+1+canvasSize, fill=color, outline=color)
        nameDict[ovalID] = system
        
        def show_name(event):
            global nameLabel
            system:System = nameDict[canvas.find_withtag("current")[0]]
            textToShow = f"{system.name} ({str(len(system.stars))} stars)"
            nameLabel.config(text = textToShow)
        canvas.tag_bind(ovalID, "<Enter>", show_name)

    print("Done!")
    canvas.create_oval(-GALAXYRADIUS, -GALAXYRADIUS, GALAXYRADIUS, GALAXYRADIUS, dash=(20, 20), outline="white")
    # draw sectors
    for x in range(0):#sectorAmountAxis):
        for y in range(sectorAmountAxis):
            canvas.create_rectangle(
                x * SECTORDISTANCE + sectorStartPos[0], 
                y*SECTORDISTANCE + sectorStartPos[1], 
                (x+1)*SECTORDISTANCE + sectorStartPos[0], 
                (y+1)*SECTORDISTANCE + sectorStartPos[1], 
                outline='white')
    root.mainloop()

# every sector has systemsPerSector sectors inside it.
# also every sector's systems connect to each other.
def make_galaxy_with_strong_sectors():
    global MAXCONNECTIONLENGTH, GALAXYCENTER, GALAXYRADIUS, SYSTEMAMOUNT
    # generate systems
    # sectorList is used to space out systems. If there are too many systems in a "sector", it will relocate.
    sectorAmountAxis = int(np.ceil((GALAXYRADIUS * 2) / SECTORDISTANCE))
    sectorList = [[[] for j in range(sectorAmountAxis)] for i in range(sectorAmountAxis)]
    sectorAmount = ((GALAXYRADIUS * 2) ** 2) // (SECTORDISTANCE ** 2)
    # the sectors form a square, but the galaxy is a circle! Not all sectors will be used.
    sectorUseAmount = np.ceil(sectorAmount * (np.pi / 4))
    # how many systems to expect per sector!
    systemsPerSector = int(np.ceil(SYSTEMAMOUNT / sectorUseAmount))
    sectorStartPos = (-GALAXYRADIUS, -GALAXYRADIUS)

    print("Generating systems...")
    for rowIndex, row in enumerate(sectorList):
        leftRowBound = sectorStartPos[0] + (rowIndex * SECTORDISTANCE)
        for columnIndex, column in enumerate(row):
            topColumnBound = sectorStartPos[1] + (columnIndex * SECTORDISTANCE)
            if distance(leftRowBound + (SECTORDISTANCE / 2), topColumnBound + (SECTORDISTANCE / 2), GALAXYCENTER[0], GALAXYCENTER[1]) > GALAXYRADIUS:
                continue
            for i in range(systemsPerSector):
                system = make_system()
                systemList.append(system)
                column.append(system)

                system.x = uniform(leftRowBound, leftRowBound + SECTORDISTANCE)
                system.y = uniform(topColumnBound, topColumnBound + SECTORDISTANCE)
            

    print("Making connections...")
    # make system connections
    # first, make every system have totalConnections
    for system in systemList:
        totalConnections = weighted_randint((1, 0.1), (2, 0.15), (3, 0.4), (4, 0.3), (5, 0.05))
        system.maxConnections = totalConnections

    # now, in every sector, make systems connect to each other
    for row in sectorList:
        for column in row:
            if not len(column):
                continue
            systemsConnected = 0
            systemsToConnect = systemsPerSector / 2
            while systemsConnected < systemsToConnect:
                system1 : System = random_from_list(column)
                system2 : System = random_from_list(column)
                if system1 == system2:
                    continue
                if system1.id in system2.warp_connections:
                    continue
                system1.connect(system2)
                systemsConnected += 1
                canvas.create_line(system1.x, system1.y, system2.x, system2.y, fill="blue")

    # make other connections
    for systemID, system in enumerate(systemList):
        totalConnections = system.maxConnections
        currentConnections = len(system.warp_connections)
        # don't make more warp connections than we need to
        if currentConnections >= totalConnections:
            continue
        
        # get systems close to us (using taxicab distance)
        # if there aren't enough systems in MAXCONNECTIONLENGTH distance,
        # then add 5 to rangeBoost (increasing connectionRange) and try again.
        closeSystems:list[System] = []
        rangeBoost = 0
        while len(closeSystems) - currentConnections < totalConnections:
            # create a list of all systems closest to us
            for connectingSystem in systemList:
                connectionRange = MAXCONNECTIONLENGTH + rangeBoost
                if ((not (connectingSystem.x < system.x - connectionRange or
                    connectingSystem.x > system.x + connectionRange or
                    connectingSystem.y > system.y + connectionRange or
                    connectingSystem.y < system.y - connectionRange))
                    and connectingSystem != system
                    and len(connectingSystem.warp_connections) < connectingSystem.maxConnections + 1
                    and connectingSystem.id not in system.warp_connections):
                    closeSystems.append(connectingSystem)
            
            rangeBoost += 5
            if rangeBoost > 1000:
                print("Hey we might have a problem", systemID)
        
        shuffle(closeSystems)
        # closeSystems.sort(key=lambda closeSystem: system.distance(closeSystem), reverse=False)
        while currentConnections < totalConnections:
            systemConnectingTo = closeSystems.pop()
            if systemConnectingTo in system.warp_connections:
                continue
            currentConnections += 1
            system.connect(systemConnectingTo)
            canvas.create_line(system.x, system.y, systemConnectingTo.x, systemConnectingTo.y, fill="blue")

            if len(closeSystems) == 0:
                break

    print("Drawing to screen...")
    for system in systemList:
        star = system.stars[0]
        x = system.x
        y = system.y

        canvasSize = np.ceil(star.radius / 2)
        color = star.colorHex
        if len(system.stars) == 4:
            color = "#00FF00"

        ovalID = canvas.create_oval(x-canvasSize, y-canvasSize, x+1+canvasSize, y+1+canvasSize, fill=color, outline=color)
        nameDict[ovalID] = system
        
        def show_name(event):
            global nameLabel
            system:System = nameDict[canvas.find_withtag("current")[0]]
            textToShow = f"{system.name} ({str(len(system.stars))} stars)"
            nameLabel.config(text = textToShow)
        canvas.tag_bind(ovalID, "<Enter>", show_name)

    print("Done!")
    canvas.create_oval(-GALAXYRADIUS, -GALAXYRADIUS, GALAXYRADIUS, GALAXYRADIUS, dash=(20, 20), outline="white")
    # draw sectors
    for x in range(0):#sectorAmountAxis):
        for y in range(sectorAmountAxis):
            canvas.create_rectangle(
                x * SECTORDISTANCE + sectorStartPos[0], 
                y*SECTORDISTANCE + sectorStartPos[1], 
                (x+1)*SECTORDISTANCE + sectorStartPos[0], 
                (y+1)*SECTORDISTANCE + sectorStartPos[1], 
                outline='white')
    root.mainloop()

def make_system_json():
    global systemList
    for systemID, system in enumerate(systemList):
        systemList[systemID] = system.to_json()
    
    with open("galaxy.json", 'w') as file:
        json.dump(systemList, file, indent=4)

if __name__ == "__main__":
    make_galaxy_with_strong_sectors()
    make_system_json()
import pygame

from district import District
from tile import Tile

class Level(object):
    def __init__(self, filename):
        #name           -> The level's name
        #raw            -> The raw numbers that make up the tiles
        #map            -> The map data made up of Tile classes

        file = open("data//lvl//" + filename + ".txt", "r")

        #Level name
        self.name = file.readline().split(":")[1][:-1]

        #Population and statistics
        self.population = 0
        self.homecount = 0
        self.schoolcount = 0
        self.policecount = 0
        self.firecount = 0
        self.hospitalcount = 0
        self.prisoncount = 0
        self.voterdrivecount = 0
        self.tilecount = 0

        #Raw data
        self.raw = ""
        for _ in range(0,25):
            self.raw += file.readline()[:-1]

        #Map data
        self.map = []

        #Max Districts
        self.maxdistricts = int(file.readline().split(":")[1])

        #Generate districts
        distcolors = ["cyan", "green", "purple", "yellow", "white", "dgreen", "dcyan", "dpurple", "dyellow", "white"]
        self.district = []
        for temp in range(0, self.maxdistricts):
            self.district.append(District(distcolors[temp]))

        #Has the level been drawn at all?
        self.drawn = False

        #High scores (5 per level)
        try:
            hs = open("data//scores//" + filename + ".txt", "r")
            self.highscores = []
            for x in range(0, 5):
                line = hs.readline().split(":")
                self.highscores.append((line[0], int(line[1])))
        except:
            self.highscores = [("--------------", 0), ("--------------", 0), ("--------------", 0), ("--------------", 0), ("--------------", 0)]

    def drawmap(self, window, gfx):

        maptiles = {"00":"home0", "01":"home1", "02":"home2", "03":"home3", "04":"home4", "05":"home5", "06":"home6", "07":"home7", "08":"home8", "0":"curious", "09":"school", "10":"police", "11":"fire", "12":"hospital", "13":"prison", "14":"voterreg"}

        gfxreqs = []

        if (self.drawn):
            return

        #Get list of needed graphics for the level
        for temp in range(0, len(self.raw) // 2):
            test = maptiles[self.raw[temp*2:(temp*2)+2]]
            if test not in gfxreqs:
                gfxreqs.append(test)

        #Forced graphics
        gfxreqs.append("border")
        gfxreqs.append("rawborder")
        gfxreqs.append("blank")
        gfxreqs.append("curious")
        gfxreqs.append("hud")
        gfxreqs.append("textbox")

        #Load those graphics into memory
        gfx.loadtiles(gfxreqs)

        #For now paint that border by hand...
        gfx.tiles["border"] = gfx.ColorSprite(gfx.bordercolors[0], gfx.tiles["border"])

        #Now create 600 tiles and get the necessary stats
        popdict = {1:100, 2:50, 3:30, 4:10, 5:10, 6:30, 7:50, 8:100}
        for temp in range(0, 600):
            id = self.raw[temp*2:(temp*2)+2]
            if (int(id) > 0) and (int(id) <= 8): #Add to the population
                self.population += popdict[int(id)]
                self.homecount += 1

            if (int(id) != 0):
                self.tilecount += 1

            if (int(id) == 9):
                self.schoolcount += 1
            elif (int(id) == 10):
                self.policecount += 1
            elif (int(id) == 11):
                self.firecount += 1
            elif (int(id) == 12):
                self.hospitalcount += 1
            elif (int(id) == 13):
                self.prisoncount += 1
            elif (int(id) == 14):
                self.voterdrivecount += 1

            self.map.append(Tile(gfx.tiles[maptiles[id]], id))

        #Now draw all of them
        for temp in range(0, 600):
            window.blit(self.map[temp].image, ((temp%24)*24,(temp // 24)*24))
        window.blit(gfx.tiles["hud"], (576, 0))
        pygame.display.update()

        self.drawn = True

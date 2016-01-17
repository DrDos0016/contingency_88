#Contingency 88 - By Dr. Dos
#Made in 1 month for the SA Gamedev Challenge
import pygame
import os
import glob
import math
import random

from pygame.locals import *
from sys import exit

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

def main():    
    #Before we do anything let's get our settings:
    try:
        settings = open("settings.cfg", "r")
        vidmode = settings.readline().split("=")[1][:-1]
        solutions = settings.readline().split("=")[1][:-1]
    except:
        print "Missing file"
        vidmode = "WINDOW"
        solutions = "SAVED"
    
    print vidmode
    print solutions
    
    icon = pygame.image.load("data//icon.png")
    pygame.display.set_icon(icon)
   
    if vidmode == "NOFRAME":
        window = pygame.display.set_mode((800, 600), NOFRAME)
    elif vidmode == "FULLSCREEN":
        window = pygame.display.set_mode((800, 600), FULLSCREEN)
    else:
        window = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("CONTINGENCY 88")
    
    #Timing
    clock = pygame.time.Clock()
    FRAMERATE = 20
    
    #Load graphics
    gfx = Gfx()
    
    #Victory(gfx, window, clock, FRAMERATE)
    #exit()
    
    #Run the titlescreen
    mode = Title(window, clock, FRAMERATE, gfx)
    
    startlevel =  "l1"
    if mode == "resumegame":
        startlevel = Resumegame(window, clock, FRAMERATE, gfx)
    
    #Gameplay begins
    game = Game(startlevel)
    if solutions == "DISCARDED":
        game.savesolutions = False
    cursor = Cursor()
    level = Level(game.levelfn)
    level.drawmap(window, gfx) #This is a bit overkill to get the population
    gfx.DrawHud(window, level, cursor, True) #Render EVERYTHING.
    tile = 0
    nextaction = ""
    pygame.mixer.music.stop()
    while game.mode == "play":
        gfx.updatehud = False
        finalize = False
        pygame.display.update()
        
        pos = (pygame.mouse.get_pos()[0]/24, pygame.mouse.get_pos()[1]/24)
        if pos[0] < 25:
            tile = (pos[1] * 24) + pos[0]
        
        #Check for things that would change the hud
        if cursor.tile != tile:
            cursor.tile = tile
            gfx.updatehud = True
            print "Tile changed"
        if cursor.lastdist != cursor.districtnum:
            print "UPDATING BECAUSE OF THIS", cursor.lastdist, cursor.districtnum
            cursor.lastdist = cursor.districtnum #Make the lastdist match
            gfx.updatehud = True
        
        level.drawmap(window, gfx)
        
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                exitgame(game.levelfn)
            if (event.type == MOUSEBUTTONDOWN):
                finalize = cursor.click((pygame.mouse.get_pos()[0]/24, pygame.mouse.get_pos()[1]/24), event.button, gfx, window, level, False)
            if (event.type == KEYUP):
                if event.key >= 49 and event.key <= 57:
                    cursor.SetDistrict(event.key - 49, gfx, level)
                if event.key == K_F1:
                    os.startfile("Manual.html")
                
        if (pygame.mouse.get_pressed()[0]):
            if cursor.lasttile != (pygame.mouse.get_pos()[0]/24, pygame.mouse.get_pos()[1]/24):
                cursor.click((pygame.mouse.get_pos()[0]/24, pygame.mouse.get_pos()[1]/24), 1, gfx, window, level, True)
                
        if finalize == "finalize":
            #Can we finalize?
            usedtiles = 0
            for x in xrange(0,len(level.district)):
                usedtiles += level.district[x].size
            unused = int(round(((level.tilecount - usedtiles) * 100.0) / level.tilecount))
            if unused < 1:
                
                min = 100
                maximum = 0
                for x in xrange(0,len(level.district)):
                    temp = int(round((level.district[x].size * 100.0) / level.tilecount))
                    if temp > maximum:
                        maximum = temp
                    if temp < min:
                        min = temp
                print min, maximum, "MIN-MAX:", min-maximum
                
                sizediff = abs(min-maximum)
                
                if sizediff <= 20:
                    print "FINALIZING VOTES"
                    nextaction = Finalize(gfx, window, level, game, clock, FRAMERATE)
                    print "NEXTACTION", nextaction
                else:
                    print "Your zones aren't balanced at all!"
            else:
                print "You need to zone everything."
        
        if nextaction != "":
            if nextaction == "restart":
                print "Restarting level..."
                nextaction = ""
                #Reload the level
                window.fill((0,0,0))
                pygame.display.update()
                cursor = Cursor()
                level = Level(game.levelfn)
                level.drawmap(window, gfx) #This is a bit overkill to get the population
                gfx.DrawHud(window, level, cursor, True) #Render EVERYTHING.
                tile = 0
                continue
                
            if nextaction == "highscore":
                print "HIGH SCORE TIME"
                print "NAME..........|SCORE"
                print "--------------+-----"
                Highscore(gfx, window, level, game, clock, FRAMERATE)
                print level.highscores[0][0], level.highscores[0][1]
                print level.highscores[1][0], level.highscores[1][1]
                print level.highscores[2][0], level.highscores[2][1]
                print level.highscores[3][0], level.highscores[3][1]
                print level.highscores[4][0], level.highscores[4][1]
                nextaction = "advance"
                
            if nextaction == "advance":
                nextaction = ""
                #Reload the level
                window.fill((0,0,0))
                pygame.display.update()
                cursor = Cursor()
                game.nextlevel() #Increase the level
                if game.levelfn == "l-win":
                    print "You beat the game!"
                    Victory(gfx, window, clock, FRAMERATE)
                    exitgame(game.maxlevel)
                level = Level(game.levelfn)
                level.drawmap(window, gfx) #This is a bit overkill to get the population
                gfx.DrawHud(window, level, cursor, True) #Render EVERYTHING.
                tile = 0
                pygame.mixer.music.stop()
                print "NEXT LEVEL TIME"
                continue
                
        if gfx.updatehud:
            gfx.DrawHud(window, level, cursor)
            
        #Tick the clock
        time = clock.tick(FRAMERATE)
    return
    
class Gfx(object):
    def __init__(self):
        #And just like that I have a dictionary with the file locations of every graphic in the game
        self.gfxlist = {}
        filelist = glob.glob("data//gfx//*")
        for file in filelist:
            self.gfxlist[file[10:-4]] = file
            
        #Border stuff, rects for blitting portions of the image, colors for how they should be painted
        self.bordertype = {"nsew":(264,0,24,24), "nse":(240,0,24,24), "nsw":(192,0,24,24), "new":(216,0,24,24), "ns":(144,0,24,24), "ne":(48,0,24,24), "nw":(24,0,24,24), "sew":(168,0,24,24), "ew":(120,0,24,24), "se":(72,0,24,24), "sw":(96,0,24,24), "none":(0,0,24,24)}
        #self.bordercolors = [(85,255,255), (255,85,255), (255,255,85), (85,255,95), (255,170,0), (64,224,208), (148,0,211), (34,139,34), (255,255,255), (100,100,0)]
        self.bordercolors = [(85,255,85), (255,255,85), (255,85,255),  (0, 170, 0), (85,255,255), (0, 170, 170), (170, 0, 170), (170, 85, 0), (255, 255, 255)]
        self.palette = {"blue":(85,85,255), "green":(85,255,85), "cyan":(85,255,255), "red":(255,85,85), "purple":(255,85,255), "yellow":(255,255,85), "white":(255,255,255), "black":(0,0,0), "dgray":(85, 85, 85), "gray":(170, 170, 170), "dblue":(0,0,170), "dgreen":(0, 170, 0), "dcyan":(0, 170, 170), "dred":(170, 0, 0), "dpurple":(170, 0, 170), "dyellow":(170, 85, 0)}
        
        #Font
        self.font = pygame.font.Font("data//pcsenior.ttf", 16)
        self.fontbig = pygame.font.Font("data//pcsenior.ttf", 32)
        
        #Hud
        self.hud = pygame.Surface((224,600))
        self.updatehud = False
        
        #Sound (I'm not making another class for like 4 sounds in the entire game)
        self.sfxzone = pygame.mixer.Sound("data//audio//zonetone.ogg")
        self.sfxnozone = pygame.mixer.Sound("data//audio//nozonetone.ogg")
        self.sfxdist = pygame.mixer.Sound("data//audio//dist.ogg")
        self.sfxunzone = pygame.mixer.Sound("data//audio//unzone.ogg")
        self.sfxtally = pygame.mixer.Sound("data//audio//tally.ogg")
            
    def loadtiles(self, requested):
        self.tiles = {}
        #Actually put these pngs into memory
        for tile in requested:
            self.tiles[tile] = pygame.image.load(self.gfxlist[tile])
            
    def ColorSprite(self, color1, graphic):
        raw = pygame.PixelArray(graphic)
        color2 = (255, 255, 255, 0) #Fully transparent
        raw.replace((0,0,0,255), color1)
        raw.replace((127,127,127,255), color2)
        image = raw.make_surface()
        return image
    
    def makeborder(self, number):
        self.tiles["border"] = self.ColorSprite(self.bordercolors[number], pygame.image.load("data//gfx//rawborder.png"))
        
    def DrawHud(self, window, level, cursor, full=False):
        #Create each element of the HUD in text
        if full:
            #Level name
            levelname = self.font.render(level.name.upper(), 0, self.palette["green"])
            
            #Population
            #Format population
            pop = str(level.population)
            print "pop orig", pop
            if (len(pop) >= 4):
                displaypop = pop[:len(pop)-3] + "," + pop[len(pop)-3:]
            else:
                displaypop = pop
                
            popdots = (9 - len(displaypop)) * "."
            population = self.font.render("POP.", 0, self.palette["yellow"])
            popval = self.font.render(displaypop, 0, self.palette["green"])
            popdots = self.font.render(popdots, 0, self.palette["yellow"])
            
            #Districts
            distsval = self.font.render(str(level.maxdistricts), 0, self.palette["green"])
            dists =  self.font.render("DISTRICTS", 0, self.palette["yellow"])
            
            #Area of districts
            areatext = self.font.render("SIZE", 0, self.palette["yellow"])
            
            #Now all 9 districts
            areas = []
            for x in xrange(0,9):
                if x < level.maxdistricts:
                    areas.append(self.font.render(str(x+1) + "    %", 0, self.bordercolors[x]))
                else:
                    areas.append(self.font.render(str(x+1) + " ---%", 0, self.palette["dgray"]))
            #10th undistricted area
            areas.append(self.font.render("*    %", 0, self.palette["gray"]))
            
            #District Info
            distinfo = self.font.render("DISTRICT INFO:", 0, self.palette["yellow"])
            
            #Homes
            homes = self.font.render("HOMES.......", 0, self.palette["green"])
            
            #Schools
            schools = self.font.render("SCHOOLS.....", 0, self.palette["yellow"])
            
            #Police Depts.
            pds = self.font.render("POLICE DPTS.", 0, self.palette["blue"])
                
            #Fire Depts.
            fds = self.font.render("FIRE DPTS...", 0, self.palette["red"])
            
            #Hospitals
            hospitals = self.font.render("HOSPITALS...", 0, self.palette["white"])
            
            #Prisons
            prisons = self.font.render("PRISONS.....", 0, self.palette["cyan"])
            
            #Voter Registration Drives
            voterdrives = self.font.render("VOTER DRVS..", 0, self.palette["purple"])

            #Tile info
            tileinfo = self.font.render("TILE INFO:", 0, self.palette["yellow"])
            
            #Zone
            zone = self.font.render("ZONE......", 0, self.palette["yellow"])
            
            #Support
            support = self.font.render("SUPPORT...", 0, self.palette["yellow"])
            
            #Concern
            concern = self.font.render("CONCERN...", 0, self.palette["yellow"])
            
            #Details
            details = self.font.render("DETAILS --", 0, self.palette["yellow"])
            
            #Finalize
            final = self.font.render("[-FINALIZE-]", 0, self.palette["red"])
            
            #Help
            help = self.font.render("F1 - FOR HELP.", 0,self.palette["yellow"])
            
        #RENDER EVERY TIME
        
        #Selected District
        curdist = self.font.render("CUR. DIST -", 0, self.palette["yellow"])
        curdistval = self.font.render(str(cursor.districtnum+1), 0, self.bordercolors[cursor.districtnum])
        
        #In district
        if level.map[cursor.tile].district != -1:
            indist = self.font.render("IN DISTRICT " + str(level.map[cursor.tile].district + 1), 0, self.bordercolors[level.map[cursor.tile].district])
        else:
            indist = self.font.render("NON-DISTRICT", 0, self.bordercolors[level.map[cursor.tile].district])
            
        #Tile Zone
        zoneval = self.font.render(level.map[cursor.tile].zone, 0, self.palette["yellow"])
        
        #Tile Support
        if level.map[cursor.tile].support == "RED":
            supportval = self.font.render(level.map[cursor.tile].support, 0, self.palette["red"])
        elif level.map[cursor.tile].support == "BLUE":
            supportval = self.font.render(level.map[cursor.tile].support, 0, self.palette["blue"])
        else:
            supportval = self.font.render(level.map[cursor.tile].support, 0, self.palette["yellow"])
        
        #Tile Concern
        concernval = self.font.render(level.map[cursor.tile].concern, 0,self.palette["yellow"])
        
        #Tile Details
        dtext = level.map[cursor.tile].details.split("=")
        
        if len(dtext) >= 4:
            d4val = self.font.render(dtext[3], 0, self.palette["white"])        
        if len(dtext) >= 3:
            d3val = self.font.render(dtext[2], 0, self.palette["white"])
        if len(dtext) >= 2:
            d2val = self.font.render(dtext[1], 0, self.palette["white"])
        if len(dtext) >= 1:
            d1val = self.font.render(dtext[0], 0, self.palette["white"])
        
        #District stats
        temp = str(level.district[cursor.districtnum].homes)
        if len(temp) == 1:
            temp = ". " + temp
        elif len(temp) == 2:
            temp = "." + temp
        homeval = self.font.render(temp, 0, self.palette["green"])
        
        temp = str(level.district[cursor.districtnum].schools)
        if len(temp) == 1:
            temp = "  " + temp
        elif len(temp) == 2:
            temp = " " + temp
        schoolval = self.font.render(temp, 0, self.palette["yellow"])
        
        temp = str(level.district[cursor.districtnum].hospitals)
        if len(temp) == 1:
            temp = "  " + temp
        elif len(temp) == 2:
            temp = " " + temp
        hospitalval = self.font.render(temp, 0, self.palette["white"])
        
        temp = str(level.district[cursor.districtnum].pds)
        if len(temp) == 1:
            temp = "  " + temp
        elif len(temp) == 2:
            temp = " " + temp
        pdval = self.font.render(temp, 0, self.palette["blue"])
        
        temp = str(level.district[cursor.districtnum].fds)
        if len(temp) == 1:
            temp = "  " + temp
        elif len(temp) == 2:
            temp = " " + temp
        fdval = self.font.render(temp, 0, self.palette["red"])
        
        temp = str(level.district[cursor.districtnum].voterdrives)
        if len(temp) == 1:
            temp = "  " + temp
        elif len(temp) == 2:
            temp = " " + temp
        voterdriveval = self.font.render(temp, 0, self.palette["purple"])
        
        temp = str(level.district[cursor.districtnum].prisons)
        if len(temp) == 1:
            temp = "  " + temp
        elif len(temp) == 2:
            temp = " " + temp
        prisonval = self.font.render(temp, 0, self.palette["cyan"])
        
        
        #-------------------------------------------------------------------------------------------------------
        #Images to blit the first time
        if full:
            blot = pygame.Surface((260,80))
            blot.fill((0,0,0))
            self.hud.blit(blot,(0,0))
            self.hud.blit(levelname, (0,0))
            self.hud.blit(population, (0,16))
            self.hud.blit(popval, (80,16))
            self.hud.blit(popdots, (80+(16*len(displaypop)),16))
            self.hud.blit(distsval, (0, 32))
            self.hud.blit(dists, (32, 32))
            self.hud.blit(curdist, (0, 64))
            self.hud.blit(areatext, (80, 96))
            self.hud.blit(distinfo, (0, 208))
            self.hud.blit(homes, (0, 240))
            self.hud.blit(schools, (0, 256))
            self.hud.blit(pds, (0, 272))
            self.hud.blit(fds, (0, 288))
            self.hud.blit(hospitals, (0, 304))
            self.hud.blit(prisons, (0, 320))
            self.hud.blit(voterdrives, (0, 336))
            self.hud.blit(tileinfo, (0, 368))
            self.hud.blit(zone, (0, 400))
            self.hud.blit(support, (0, 416))
            self.hud.blit(concern, (0, 432))
            self.hud.blit(details, (0, 448))
            self.hud.blit(final, (16, 544))
            self.hud.blit(help, (0, 576))
            
            #District Areas sans values
            for x in xrange(0,10):
                if x % 2 == 0:
                    self.hud.blit(areas[x], (0, 112+(x*8)))
                else:
                    self.hud.blit(areas[x], (112, 104+(x*8)))
            
        #Images to blit all the time
        #First blank all the old values
        #District number...
        blank = pygame.Surface((14, 14))
        self.hud.blit(blank, (192, 64))
        #District Sizes
        blank = pygame.Surface((48, 80))
        self.hud.blit(blank, (32, 112))
        self.hud.blit(blank, (144, 112))
        blank = pygame.Surface((32, 120))
        self.hud.blit(blank, (192, 240))
        blank = pygame.Surface((48, 16))
        self.hud.blit(blank, (176, 240))
        
        #In district...
        blank = pygame.Surface((224, 14))
        self.hud.blit(blank, (0, 384))
        self.hud.blit(indist, (0, 384))
        
        #Tile info
        blank = pygame.Surface((64, 48))
        self.hud.blit(blank, (160, 400))
        
        #Tile details
        blank = pygame.Surface((224, 64))
        self.hud.blit(blank, (0, 464))
        
        #AREAS Calculations
        distareas = []
        for x in xrange(0,len(level.district)):
            temp = str(int(round((level.district[x].size * 100.0) / level.tilecount)))
            if len(temp) == 2:
                temp = " " + temp
            elif len(temp) == 1:
                temp = "  " + temp
            distareas.append(temp)
        usedtiles = 0
        for x in xrange(0,len(level.district)):
            usedtiles += level.district[x].size
        unused = str((int(round(((level.tilecount - usedtiles) * 100.0) / level.tilecount))))
        if len(unused) == 2:
            unused = " " + unused
        elif len(unused) == 1:
            unused = "  " + unused
        
        #Now blit the new values
        self.hud.blit(homeval, (176,240))
        self.hud.blit(schoolval, (176,256))
        self.hud.blit(pdval, (176,272))
        self.hud.blit(fdval, (176,288))
        self.hud.blit(hospitalval, (176,304))
        self.hud.blit(prisonval, (176,320))
        self.hud.blit(voterdriveval, (176,336))
        
        #Current district
        self.hud.blit(curdistval, (192, 64))
        
        #Tile info
        Information = {"00":"", "01":""}
        print level.map[cursor.tile].id
        
        #Tile zone
        self.hud.blit(zoneval, (160, 400))
        
        #Tile support
        self.hud.blit(supportval, (160,416))
        
        #Tile concern
        self.hud.blit(concernval, (160,432))
        
        #Tile details
        if len(dtext) >= 4:
            self.hud.blit(d4val, (16,512))
        if len(dtext) >= 3:
            self.hud.blit(d3val, (16,496))
        if len(dtext) >= 2:
            self.hud.blit(d2val, (16,480))
        if len(dtext) >= 1:
            self.hud.blit(d1val, (16,464))
            
        #District Area values
            for x in xrange(0,len(distareas)):
                render = self.font.render(distareas[x], 0, self.bordercolors[x])
                if x % 2 == 0:
                    self.hud.blit(render, (32, 112+(x*8)))
                else:
                    self.hud.blit(render, (144, 104+(x*8)))
            render = self.font.render(str(unused), 0, self.palette["gray"])
            self.hud.blit(render, (144, 176))
        
        #District building stats?
        
        window.blit(self.hud, (576,0))
        print "I UPDATED THE HUD"

        
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
        for _ in xrange(0,25):
            self.raw += file.readline()[:-1]
        
        #Map data
        self.map = []

        #Max Districts
        self.maxdistricts = int(file.readline().split(":")[1])
        
        #Generate districts
        distcolors = ["cyan", "green", "purple", "yellow", "white", "dgreen", "dcyan", "dpurple", "dyellow", "white"]
        self.district = []
        for temp in xrange(0, self.maxdistricts):
            self.district.append(District(distcolors[temp]))
        
        #Has the level been drawn at all?
        self.drawn = False
        
        #High scores (5 per level)
        try:
            hs = open("data//scores//" + filename + ".txt", "r")
            self.highscores = []
            for x in xrange(0, 5):
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
        for temp in xrange(0, len(self.raw)/2):
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
        for temp in xrange(0, 600):
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
        print "POPULATION", self.population
        
        #Now draw all of them
        for temp in xrange(0, 600):
            window.blit(self.map[temp].image, ((temp%24)*24,(temp/24)*24))
        window.blit(gfx.tiles["hud"], (576, 0))
        pygame.display.update()
        
        self.drawn = True
        
class Game(object):
    def __init__(self, levelfn):
        self.mode = "play"
        self.levelfn = levelfn
        self.score = 0
        self.savesolutions = True
        
        levelinfo = open("data//levelinfo.txt", "r")
        temp = levelinfo.readline().split(":")[1]
        self.maxlevel = "l" + temp
        self.levelcount = int(temp)
        
    def nextlevel(self):
        self.score = 0
        levelnum = int(self.levelfn[1:])
        levelnum += 1
        if levelnum > self.levelcount:
            levelnum = "-win"
        self.levelfn = "l" + str(levelnum)
        
class Tile(object):
    def __init__(self, image, id):
        typedict = {"00":"nonpuzzle", "01":"blue10", "02":"blue5", "03":"blue3", "04":"blue1", "05":"red1", "06":"red3", "07":"red5", "08":"red10", "09":"school", "10":"police", "11":"fire", "12":"hospital", "13":"prison", "14":"voterreg"}
        zonedict = {"00":"", "01":"HOME", "02":"HOME", "03":"HOME", "04":"HOME", "05":"HOME", "06":"HOME", "07":"HOME", "08":"HOME", "09":"SCHL", "10":"PLDP", "11":"FRDP", "12":"HSPT", "13":"PRSN", "14":"VOTE"}
        supportdict = {"00":"", "01":"BLUE", "02":"BLUE", "03":"BLUE", "04":"BLUE", "05":"RED", "06":"RED", "07":"RED", "08":"RED", "09":"", "10":"", "11":"", "12":"", "13":"", "14":""}
        concerndict = {"00":"", "01":"MAX", "02":"HIGH", "03":"AVG", "04":"LOW", "05":"LOW", "06":"AVG", "07":"HIGH", "08":"MAX", "09":"", "10":"", "11":"", "12":"", "13":"", "14":""}
        detailsdict = {"00":"", "01":"100 VOTES BUT=NOT FOR RED.=ZONE THEM OUT=OR BE DEAD.", "02":"50 VOTES YET=ALL ARE BLUE.=ZONE SAFELY=OR BE THROUGH", "03":"30 BLUE VOTES=COULD BE MORE=ZONE AWAY TO=EVEN SCORE", "04":"10 BLUE VOTES=WON'T BOTHER=YOU.UNTIL RED=LOSES BY TWO.", "05":"RESIDENTIAL=AREA WITH 10=EXPECTED RED=VOTERS.", "06":"RESIDENTIAL=AREA WITH 30=EXPECTED RED=VOTERS.", "07":"RESIDENTIAL=AREA WITH 50=EXPECTED RED=VOTERS.", "08":"100 VOTERS=AT THE CORE=THEY KNOW WHO=TO VOTE FOR!", "09":"SCHOOLS HELP=KIDS TO GROW=IGNORING THIS=WOULD BE LOW.", "10":"DO BE TOUGH=ON ANY CRIME=TO ABIDE RED=PARTY LINE", "11":"FIRE DEPT.=FIRE DEPT.2=FIRE DEPT.3=FIRE DEPT.4", "12":"LAUGHTER IS=BEST MEDICINE=NO BLUE CRIES=IS A SURE WIN", "13":"MY BACKYARD=HAS NO JAILS.=IF IT CANT GO=SUPPORT FAILS", "14":"I WON IT ALL,=RED GLOATS.=HOW WE DID IT=VIA NEW VOTES"}
        
        self.id = id
        self.type = typedict[id]
        self.zone = zonedict[id]
        self.support = supportdict[id]
        self.concern = concerndict[id]
        self.details = detailsdict[id]
        
        if (id != "00"):
            print id
        
        self.image = image
        self.district = -1

class Cursor(object):
    def __init__(self):
        self.left = "DISTRICT"
        self.right = "FILL"
        self.districtnum = 0
        self.lastdist = 0
        self.tile = 0
        
        #Rectangle for finalize button
        self.finalize = pygame.Rect((594, 544), (184, 14))
        
        #Where did you last click
        self.lasttile = (-1, -1)
        #And what did you do by clicking there
        self.lastaction = "district"
        
        #Fill counter for flood fill
        self.fillcount = 0
        
        #Delete counter for deleting a tile
        self.deletecount = 0
        
        #Useful tiles for deleting a tile
        self.usefultiles = []
        
    def click(self, pos, button, gfx, window, level, holding=False):
        if button == 2:
            return False
        #print button
        self.lasttile = pos
        
        #Just update the hud
        gfx.updatehud = True
        
        #Get the tile before we do anything
        tile = (pos[1] * 24) + pos[0]
        if button == 4:
            self.lastdist = self.districtnum
            self.districtnum += 1
            if self.districtnum >= level.maxdistricts:
                self.districtnum = 0
            gfx.makeborder(self.districtnum)
            print "You changed the active district"
            gfx.sfxdist.play() #Play tone
            return False
        elif button == 5:
            self.lastdist = self.districtnum
            self.districtnum -= 1
            if self.districtnum < 0:
                self.districtnum = level.maxdistricts - 1
            gfx.makeborder(self.districtnum)
            print "You changed the active district"
            gfx.sfxdist.play() #Play tone
            return False
            
        if (button == 3): #Fill tool
            olddistrict = level.map[(pos[1] * 24) + pos[0]].district
            self.fill(level, gfx, window, pos, olddistrict)
            self.lastaction = "fill"
            self.fillcount = 0
            print "You used the fill tool"
            return False
        
        if (button == 6):
            print "Information..."
            print "LEVEL INFO"
            print "POP  ", level.population
            print "HOMEs", level.homecount
            print "SCHLs", level.schoolcount
            print "PDs  ", level.policecount
            print "FDs  ", level.firecount
            print "HSPTs", level.hospitalcount
            print "PRSNs", level.prisoncount
            print "VDRVs", level.voterdrivecount
            print "TILES", level.tilecount
            return False
        
        if (button == 7):
            print "Dist list"
            print level.district[0].tiles
            return False
        
        if pos[0] >= 24:
            if self.finalize.collidepoint(pygame.mouse.get_pos()):
                print "You clicked FINALIZE!"
                return "finalize"
            else:
                print "You clicked the sidebar"
            return False #You clicked the sidebar, handle later
        
        #DISTRICTING:
        
        #Do nothing if you're on non-puzzle map tiles
        
        if (level.map[tile].id) == "00":
            print "You tried to district a non-puzzle map tile"
            return False
        
            
        if ((level.map[tile].district) != self.districtnum):
            if holding and self.lastaction != "district":
                print "You were holding down a button but not trying to district additional tiles"
                return False
            
            #Check the district isn't disjointed
            if level.district[self.districtnum].size > 0:
                borders = 0
                if (tile - 1) % 24 != 23: #Check west if you can
                    if level.map[tile-1].district == self.districtnum:
                        borders += 1
                if (tile + 1) % 24 != 0: #Check east if you can
                    if level.map[tile+1].district == self.districtnum:
                        borders += 1
                if (tile + 24) < 600: #Check south if you can
                    if level.map[tile+24].district == self.districtnum:
                        borders += 1
                if (tile - 24) >= 0: #Check north if you can
                    if level.map[tile-24].district == self.districtnum:
                        borders += 1
                if borders <= 0:
                    print "Districting tile #", tile, "would have caused a gap!"
                    gfx.sfxnozone.play() #Play tone
                    return False
            
            #Reduce count of old district
            print "Tile's current district", level.map[tile].district
            if level.map[tile].district != -1:
                #Check if you can safely redistrict the tile without breaking a district into pieces
                print "Checking with CanDelete"
                if not self.CanDelete(level, gfx, window, pos, level.map[tile].district):
                    print "You can't delete that tile, it would break up another district"
                    gfx.sfxnozone.play() #Play tone
                    return False
                else:
                    level.district[level.map[tile].district].size -= 1
                
            #Change to new district
            level.map[tile].district = self.districtnum
            
            #Update district size
            level.district[self.districtnum].size += 1
            
            #Update the district stats
            if level.map[tile].type in ["blue10", "blue5", "blue3", "blue1", "red1", "red3", "red5", "red10"]:
                level.district[self.districtnum].homes += 1
            elif level.map[tile].type == "school":
                level.district[self.districtnum].schools += 1
            elif level.map[tile].type == "police":
                level.district[self.districtnum].pds += 1
            elif level.map[tile].type == "fire":
                level.district[self.districtnum].fds += 1
            elif level.map[tile].type == "hospital":
                level.district[self.districtnum].hospitals += 1
            elif level.map[tile].type == "prison":
                level.district[self.districtnum].prisons += 1
            elif level.map[tile].type == "voterreg":
                level.district[self.districtnum].voterdrives += 1
            
            #Add district tile # to list
            level.district[self.districtnum].tiles.append(tile)
            
            #Draw marked tile border
            window.blit(gfx.tiles["border"], (pos[0]*24,pos[1]*24), self.chooseborder(tile, gfx, level.map, self.districtnum))
            print "You marked a tile"
            if not holding:
                self.lastaction = "district"
                gfx.sfxzone.play() #Play tone
        else:
            if holding and self.lastaction != "delete":
                print "You unintentionally tried to delete a tile while holding the district button down"
                return False
                
            #Check if you can safely redistrict the tile without breaking a district into pieces
            print "Checking with CanDelete PART2"
            if not self.CanDelete(level, gfx, window, pos, level.map[tile].district):
                print "You can't delete that tile, it would break up another district PART2"
                gfx.sfxnozone.play() #Play tone
                return False
            else:
                level.district[level.map[tile].district].size -= 1
            window.blit(gfx.tiles["blank"], (pos[0]*24,pos[1]*24))
            window.blit(level.map[tile].image, (pos[0]*24,pos[1]*24))
            level.map[tile].district = -1
            if not holding:
                self.lastaction = "delete"
                
                #Update the district stats
                if level.map[tile].type in ["blue10", "blue5", "blue3", "blue1", "red1", "red3", "red5", "red10"]:
                    level.district[self.districtnum].homes -= 1
                elif level.map[tile].type == "school":
                    level.district[self.districtnum].schools -= 1
                elif level.map[tile].type == "police":
                    level.district[self.districtnum].pds -= 1
                elif level.map[tile].type == "fire":
                    level.district[self.districtnum].fds -= 1
                elif level.map[tile].type == "hospital":
                    level.district[self.districtnum].hospitals -= 1
                elif level.map[tile].type == "prison":
                    level.district[self.districtnum].prisons -= 1
                elif level.map[tile].type == "voterreg":
                    level.district[self.districtnum].voterdrives -= 1
                print "You did in fact delete a tile and the function will now return true"
                gfx.sfxunzone.play()
            
        return True

    def chooseborder(self, tile, gfx, map, districtnum):
        return gfx.bordertype["nsew"] #This might be something to go back to later, but don't get hung up on fancy bordering
        
    def fill(self, level, gfx, window, pos, olddistrict):
        x = pos[0]
        y = pos[1]
        tile = (pos[1] * 24) + pos[0]
        
        #If the fill is just starting, move north until you hit a border before clicking
        if self.fillcount == 0:
            while True:
                if level.map[tile].district == olddistrict:
                    if y - 1 >= 0:
                        y -= 1
                        tile = (y * 24) + pos[0]
                    else: #Same code as below?
                        print "I'm actually clicking on", x, y+1
                        y += 1
                        tile = (y * 24) + pos[0]
                        break
                else:
                    print "I'm actually clicking on", x, y+1
                    y += 1
                    tile = (y * 24) + pos[0]
                    break
        
        if (level.map[tile].district == olddistrict):
            if not (self.click((x, y), 1, gfx, window, level)): #This fakes a click causing the actual fill to happen
                return
            else:
                self.fillcount += 1
            
            if (x+1 < 24):
                self.fill(level, gfx, window, (x+1,y), olddistrict)
            if (x-1 >= 0):
                self.fill(level, gfx, window, (x-1,y), olddistrict)
            if (y+1 < 25):
                self.fill(level, gfx, window, (x,y+1), olddistrict)
            if (y-1 >= 0):
                self.fill(level, gfx, window, (x,y-1), olddistrict)

    def CanDelete(self, level, gfx, window, pos, olddistrict):
    
        self.deletecount = 0
        self.usefultiles = []
        
        #Get the target tile
        tile = (pos[1] * 24) + pos[0]
        
        #If this tile is the entirety of the district go nuts and delete it
        print len(level.district[level.map[tile].district].tiles), "is the dist size"
        if len(level.district[level.map[tile].district].tiles) == 1:    
            level.district[level.map[tile].district].tiles.remove(tile)
            level.map[tile].district = olddistrict
            return True
        
        #Get the target tile's district #
        workingdist = level.map[tile].district
        print "Tile", tile, "has district #", workingdist
        keytiles = []
        if (tile+1) % 24 != 0: #Can there be a tile to the right?
            if level.map[tile+1].district == workingdist:
                keytiles.append(tile+1)
        if (tile) % 24 != 0: #Can there be a tile to the left?
            if level.map[tile-1].district == workingdist:
                keytiles.append(tile-1)
        if (tile) >= 24: #Can there be a tile above?
            if level.map[tile-24].district == workingdist:
                keytiles.append(tile-24)
        if (tile) <= 575: #Can there be a tile below?
            if level.map[tile+24].district == workingdist:
                keytiles.append(tile+24)
        print "KEY TILES", keytiles
        
        #Remove target tile from the district
        print "Tile to remove...", tile
        level.district[level.map[tile].district].tiles.remove(tile)
        level.map[tile].district = -1
        
        self.DeletionCheck(level, level.district[olddistrict].tiles, keytiles, keytiles[0], keytiles[0])
        print "Out of that deletion check mess"
        print "Usefultiles...", self.usefultiles
        
        print "Now if the length of usefultiles == length of the district, you can delete..."
        if len(self.usefultiles) == len(level.district[olddistrict].tiles):
            print "Yeah sure you can delete that!"
            level.map[tile].district = olddistrict
            return True
        else:
            print "NO THAT WOULD BREAK THE DISTRICT INTO PIECES!", tile, olddistrict
            print "Lengths", len(self.usefultiles), len(level.district[olddistrict].tiles)
            level.district[olddistrict].tiles.append(tile) #Put the tile back in the district list
            level.map[tile].district = olddistrict #Set the tile's district
            return False
        
    def DeletionCheck(self, level, tilelist, keytiles, origtile, targettile):
        self.usefultiles.append(targettile)
            
        if (targettile+1) % 24 != 0: #Can there be a tile to the right?
            if level.map[targettile+1].district == level.map[keytiles[0]].district:
                if targettile+1 not in self.usefultiles:
                    self.DeletionCheck(level, tilelist, keytiles, origtile, targettile+1)
        if (targettile) % 24 != 0: #Can there be a tile to the left?
            if level.map[targettile-1].district == level.map[keytiles[0]].district:
                if targettile-1 not in self.usefultiles:
                    self.DeletionCheck(level, tilelist, keytiles, origtile, targettile-1)
        if (targettile) >= 24: #Can there be a tile above?
            if level.map[targettile-24].district == level.map[keytiles[0]].district:
                if targettile-24 not in self.usefultiles:
                    self.DeletionCheck(level, tilelist, keytiles, origtile, targettile-24)
        if (targettile) <= 575: #Can there be a tile below?
            if level.map[targettile+24].district == level.map[keytiles[0]].district:
                if targettile+24 not in self.usefultiles:
                    self.DeletionCheck(level, tilelist, keytiles, origtile, targettile+24)
        
    def SetDistrict(self, num, gfx, level):
        if num > (level.maxdistricts - 1):
            print "That district isn't available on this map"
            return
        self.lastdist = self.districtnum
        self.districtnum = num
        gfx.makeborder(self.districtnum)
        print "You changed the active district via key"
        gfx.sfxdist.play() #Play tone
        return False
        

class District(object):
    def __init__(self, color):
        self.size = 0
        self.homes = 0
        self.schools = 0
        self.hospitals = 0
        self.prisons = 0
        self.pds = 0
        self.fds = 0
        self.voterdrives = 0
        self.color = color
        
        self.tiles = []
        
        #NEVER USED THIS
        #Votes for     R/B
        self.votes  = (0,0)
        self.hvotes = (0,0)
        self.tvotes = (0,0)
        self.qvotes = (0,0)
        
    def totalvotes(self):
        #NEVER USED THIS EITHER
        rtotal = self.votes[0] * 100
        rtotal += (self.hvotes[0]) * 50
        rtotal += (self.tvotes[0]) * 30
        rtotal += self.qvotes[0] * 10
        
        btotal  = self.votes[1]  * 100
        btotal += self.hvotes[1] * 50
        btotal += self.tvotes[1] * 30
        btotal += self.qvotes[1] * 10
        
        return rtotal, btotal
        

def Title(window, clock, FRAMERATE, gfx):
    bg = pygame.image.load("data//gfx//titlescreen.png")
    box = pygame.image.load("data//gfx//textbox.png")
    logo = pygame.image.load("data//gfx//logo.png")
    
    window.blit(bg, (0,0))
    box.blit(logo, (14,260))
    window.blit(box, (227,100))
    
    temp = gfx.font.render(" - CONTINGENCY 88 - ", 0, gfx.palette["purple"])
    window.blit(temp, (240,114))
    temp = gfx.font.render("TO ONLY BE INITIATED", 0, gfx.palette["purple"])
    window.blit(temp, (240,146))
    temp = gfx.font.render("  IN CASE OF TOTAL  ", 0, gfx.palette["purple"])
    window.blit(temp, (240,162))
    temp = gfx.font.render("  ELECTION FAILURE  ", 0, gfx.palette["purple"])
    window.blit(temp, (240,178))
    
    newgame1 = gfx.font.render("    EXECUTE PLAN    ", 0, gfx.palette["white"])
    window.blit(newgame1, (240,226))
    resumegame1 = gfx.font.render("   RESUME PROJECT   ", 0, gfx.palette["white"])
    window.blit(resumegame1, (240,258))
    manual1 = gfx.font.render("  OPERATING MANUAL  ", 0, gfx.palette["white"])
    window.blit(manual1, (240,290))
    
    newgame2 = gfx.font.render("    EXECUTE PLAN    ", 0, gfx.palette["red"])
    resumegame2 = gfx.font.render("   RESUME PROJECT   ", 0, gfx.palette["red"])
    manual2 = gfx.font.render("  OPERATING MANUAL  ", 0, gfx.palette["red"])
    
    temp = gfx.font.render("developed by Dr. Dos", 0, gfx.palette["cyan"])
    window.blit(temp, (240,338))
    
    pygame.display.update()
    pygame.mixer.music.load("data//audio//title.ogg")
    pygame.mixer.music.play(1)
    clickedat = (-1, -1)
    
    area1 = pygame.Rect((272, 225), (253, 15))
    area2 = pygame.Rect((272, 257), (253, 15))
    area3 = pygame.Rect((272, 289), (253, 15))
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                exitgame("x")
            if (event.type == MOUSEBUTTONUP and event.button == 1):
                clickedat = pygame.mouse.get_pos()
                
        pos = pygame.mouse.get_pos()
        
        if area1.collidepoint(pos):
            window.blit(newgame2, (240,226))
        else: 
            window.blit(newgame1, (240,226))
        
        if area2.collidepoint(pos):
            window.blit(resumegame2, (240,258))
        else:
            window.blit(resumegame1, (240,258))
        
        if area3.collidepoint(pos):
            window.blit(manual2, (240,290))
        else:
            window.blit(manual1, (240,290))
            
        pygame.display.update()
        
        if clickedat != (-1, -1):
            if area1.collidepoint(clickedat):
                button = "newgame"
                break
            elif area2.collidepoint(clickedat):
                button = "resumegame"
                break
            elif area3.collidepoint(clickedat):
                clickedat = (-1, -1)
                os.startfile("Manual.html")
        time = clock.tick(FRAMERATE)
    pygame.mixer.music.stop()
    return button
    



def Finalize(gfx, window, level, game, clock, FRAMERATE):
    snapshot = pygame.Surface((800,600))
    snapshot.blit(window, (0,0))
    print "Tallying votes or something"
    
    textbox = gfx.tiles["textbox"]
    temp = gfx.font.render("-RUNNING SIMLUATION-", 1, gfx.palette["purple"])
    textbox.blit(temp, (14,14))
    
    for num in xrange(0,level.maxdistricts):
        temp = gfx.font.render("     DISTRICT " + str(num+1), 1, gfx.bordercolors[num])
        textbox.blit(temp, (14,46+(16*num)))

    window.blit(textbox, (115,100))
    pygame.display.update()
    
    #Calculate votes one district at a time
    results = []
    for num in xrange(0,level.maxdistricts):
        #Set the voting table
        #        100 50 30 10
        rvotes = [0, 0, 0, 0]
        bvotes = [0, 0, 0, 0]
        redshift = 0
        blueshift = 0
        #First lets get the raw votes ignoring special buildings
        #Loop through every tile assigned to the district
        for tile in level.district[num].tiles:
            if level.map[tile].id == "01":
                bvotes[0] += 1
            elif level.map[tile].id == "02":
                bvotes[1] += 1
            elif level.map[tile].id == "03":
                bvotes[2] += 1
            elif level.map[tile].id == "04":
                bvotes[3] += 1
            elif level.map[tile].id == "05":
                rvotes[3] += 1
            elif level.map[tile].id == "06":
                rvotes[2] += 1
            elif level.map[tile].id == "07":
                rvotes[1] += 1
            elif level.map[tile].id == "08":
                rvotes[0] += 1
        
        print "PRE BUILDING TOTALS"
        print "-RED:", rvotes, " BLUE:", bvotes
        
        #Now take special buildings into account:
        #Schools
        if level.schoolcount > 0:
            if level.district[num].schools == 0:
                print "No school penalty!"
                blueshift += 1
        #Police
        if level.policecount > 0:
            if level.district[num].pds > 0:
                print "Police bonus!"
                redshift += 1
        #Fire
        if level.firecount > 0:
            if level.district[num].fds == 0:
                print "No fire dpt. penalty I guess"
        #Hospitals
        if level.hospitalcount > 0:
            if level.district[num].hospitals > 0:
                print "Hospital bonus!"
                blueshift -= 1
        #Prisons
        if level.prisoncount > 0:
            if level.district[num].prisons > 0:
                print "Prison penalty!"
                redshift -= 1
        #Voter Drives
        if level.voterdrivecount > 0:
            if level.district[num].voterdrives > 0:
                print "ROCK THE VOTE!"
                rvotesum = (rvotes[0])+(rvotes[1])+(rvotes[2])+(rvotes[3])
                bvotesum = (bvotes[0])+(bvotes[1])+(bvotes[2])+(bvotes[3])
                if rvotesum > bvotesum:
                    print "Blue is motivated penalty!"
                    bvotes[1] = bvotes[3]
                    bvotes[3] = 0
                elif bvotesum > rvotesum:
                    print "Red is motivated bonus!"
                    rvotes[1] = rvotes[3]
                    rvotes[3] = 0
        
        print "Done figuring out bonuses/penalties"
        print "Now applying bonuses/penalties"
        if blueshift == 1:
            bvotes[0] += bvotes[1]
            bvotes[1] = 0 #All 50 vote tiles became 100
            bvotes[1] += bvotes[2]
            bvotes[2] = 0 #All 30 vote tiles became 50
            bvotes[2] += bvotes[3]
            bvotes[3] = 0 #All 10 vote tiles became 30
        elif blueshift == -1:
            bvotes[3] = bvotes[2] #All 30 vote tiles became 10
            bvotes[2] = bvotes[1] #All 50 vote tiles became 30
            bvotes[1] = 0
        
        if redshift == 1:
            rvotes[0] += rvotes[1]
            rvotes[1] = 0 #All 50 vote tiles became 100
            rvotes[1] += rvotes[2]
            rvotes[2] = 0 #All 30 vote tiles became 50
            rvotes[2] += rvotes[3]
            rvotes[3] = 0 #All 10 vote tiles became 30
        elif redshift == -1:
            rvotes[3] = rvotes[2] #All 30 vote tiles became 10
            rvotes[2] = rvotes[1] #All 50 vote tiles became 30
            rvotes[1] = 0
 
        
        print "DISTRICT", num, "FINAL TALLY"
        print "-RED:", rvotes, " BLUE:", bvotes
        rvotesum = (rvotes[0]*100)+(rvotes[1]*50)+(rvotes[2]*30)+(rvotes[3]*10)
        bvotesum = (bvotes[0]*100)+(bvotes[1]*50)+(bvotes[2]*30)+(bvotes[3]*10)
        print "--POPULAR VOTE: RED-", rvotesum, "BLUE-", bvotesum
        if rvotesum > bvotesum:
            print "---RED wins district"
            winner = "red"
        else:
            print "---BLUE wins district"
            winner = "blue"
            
        results.append((rvotesum, bvotesum, winner))
        
    #Draw the districts won/loss
    temp = gfx.font.render("- ELECTION RESULTS -", 1, gfx.palette["white"])
    textbox.blit(temp, (14,208))
    temp = gfx.font.render("DISTRICTS WON :     ", 1, gfx.palette["red"])
    textbox.blit(temp, (14,224))
    temp = gfx.font.render("DISTRICTS LOST:     ", 1, gfx.palette["blue"])
    textbox.blit(temp, (14,240))
    
    
    #Now we have all the results, let's draw us some ~Rectangles~
    
    bg = pygame.Surface((320,16))
    bg.fill(gfx.palette["dgray"])
    
    
    
    for num in xrange(0,level.maxdistricts):
        data = results[num]
        #Draw the 100% gray rectangle
        textbox.blit(bg, (13,46+(16*num)))
        rpercent = int(math.floor(data[0] * 100.0 /(data[0]+data[1])))
        bpercent = int(math.ceil(data[1] * 100.0 /(data[0]+data[1])))
        
        while (rpercent % 5) != 0:
            rpercent = rpercent - 1
        while (bpercent % 5) != 0:
            bpercent = bpercent + 1
        #Start drawing a rectangle #(320 pixels wide, 16px tall)
        
        
        for foo in xrange(1, max(rpercent/5, bpercent/5)+1):
            #Draw red bar
            width = 16 * (foo)
            if width > 16*(rpercent/5):
                width = 16*(rpercent/5)
            red = pygame.Surface((width,16))
            red.fill(gfx.palette["dred"])
            textbox.blit(red, (13,46+(16*num)))
            
            #Draw blue bar
            width = 16 * (foo)
            if width > 16*(bpercent/5):
                width = 16*(bpercent/5)
            blue = pygame.Surface((width,16))
            blue.fill(gfx.palette["dblue"])
            textbox.blit(blue, (333-blue.get_width(),46+(16*num)))
            
            
            
            temp = gfx.font.render("     DISTRICT " + str(num+1), 1, gfx.bordercolors[num])
            textbox.blit(temp, (14,46+(16*num)))
            window.blit(textbox, (115,100))
            pygame.display.update()
            time = clock.tick(FRAMERATE)
            
        #Final blit of the now done district
        red.fill((170,0,0))
        blue.fill((0,0,170))
        textbox.blit(red, (13,46+(16*num)))
        textbox.blit(blue, (333-blue.get_width(),46+(16*num)))
        temp = gfx.font.render("     DISTRICT " + str(num+1), 1, gfx.palette[data[2]])
        textbox.blit(temp, (14,46+(16*num)))
        window.blit(textbox, (115,100))
        pygame.display.update()
        
    #So the end result?
    redwins = 0
    bluewins = 0
    for district in results:
        if district[2] == "red":
            redwins += 1
        else:
            bluewins += 1
    
    temp = gfx.font.render("- ELECTION RESULTS -", 1, gfx.palette["white"])
    textbox.blit(temp, (14,208))
    temp = gfx.font.render("DISTRICTS WON :    " + str(redwins), 1, gfx.palette["red"])
    textbox.blit(temp, (14,224))
    temp = gfx.font.render("DISTRICTS LOST:    " + str(bluewins), 1, gfx.palette["blue"])
    textbox.blit(temp, (14,240))
    
    if redwins > bluewins:
        pygame.mixer.music.load("data//audio//RedvsBlue.ogg")
        pygame.mixer.music.play(1)
        temp = gfx.fontbig.render("DEMOCRACY", 1, gfx.palette["red"])
        textbox.blit(temp, (textbox.get_width()/2-temp.get_width()/2,304))
        temp = gfx.fontbig.render("PREVAILS", 1, gfx.palette["red"])
        textbox.blit(temp, (textbox.get_width()/2-temp.get_width()/2,336))
        winner = "red"
    else:
        pygame.mixer.music.load("data//audio//lose.ogg")
        pygame.mixer.music.play(1)
        temp = gfx.fontbig.render("BLUE LIES", 1, gfx.palette["blue"])
        textbox.blit(temp, (textbox.get_width()/2-temp.get_width()/2,304))
        temp = gfx.fontbig.render("PREVAIL", 1, gfx.palette["blue"])
        textbox.blit(temp, (textbox.get_width()/2-temp.get_width()/2,336))
        winner = "blue"
    
    window.blit(textbox, (115,100))
    pygame.display.update()
    
    textrect = pygame.Rect((115,100), (346,400))
    
    #Wait for player's input
    pygame.event.clear()
    looping = True
    while looping:
        for event in pygame.event.get():
            if (event.type == MOUSEBUTTONUP and event.button == 1):
                if textrect.collidepoint(pygame.mouse.get_pos()):
                    looping = False
    pygame.event.clear()
    
    print "Newspaper time"
    #Newspaper part
    gfx.tiles["textbox"] = pygame.image.load("data//gfx//textbox.png")
    newspaper = gfx.tiles["textbox"]
    bg = pygame.Surface((318,186))
    bg.fill((255,255,255))
    newspaper.blit(bg, (14,14))
    
    percentwon = int(round(redwins * 100.0 / (redwins + bluewins)))
    print "percent won", percentwon
    
    if (percentwon == 100):#10 chars per row
        headline = "CLEAR RED=MANDATE"
    elif (percentwon >= 85):
        headline = "DECISIVE=RED WIN"
    elif (percentwon >= 70):
        headline = "RED REIGN=CONTINUES"
    elif (percentwon >= 51):
        headline = "ANDERSON=EKES WIN"
    elif (percentwon >= 31):
        headline = "TRUE BLUE=STATE"
    elif (percentwon >= 16):
        headline = "ANDERSON=OUSTED"
    elif (percentwon == 0):
        headline = "RED IS=DEAD"
    
    temp = gfx.font.render(" ROOSYLVANIA RECORD ", 1, gfx.palette["black"])
    newspaper.blit(temp, (14,14))
    temp = gfx.fontbig.render(headline.split("=")[0], 1, gfx.palette["black"])
    newspaper.blit(temp, (textbox.get_width()/2-temp.get_width()/2,30))
    temp = gfx.fontbig.render(headline.split("=")[1], 1, gfx.palette["black"])
    newspaper.blit(temp, (textbox.get_width()/2-temp.get_width()/2,62))
    temp = gfx.font.render(" ================== ", 1, gfx.palette["black"])
    newspaper.blit(temp, (14,94))
    newspaper.blit(temp, (14,110))
    temp = gfx.font.render(" =|&&|============= ", 1, gfx.palette["black"])
    newspaper.blit(temp, (14,126))
    newspaper.blit(temp, (14,142))
    temp = gfx.font.render(" ================== ", 1, gfx.palette["black"])
    newspaper.blit(temp, (14,158))
    
    if percentwon > 50:
        print "Because you won,calculate a score"
        
        vicbonus = redwins * 2500
        redbonus = 0
        blueloss = 0
        for item in results:
            redbonus += item[0]
            blueloss += item[1]
        
        min = 100
        maximum = 0
        for x in xrange(0,len(level.district)):
            temp = int(round((level.district[x].size * 100.0) / level.tilecount))
            if temp > maximum:
                maximum = temp
            if temp < min:
                min = temp
        print min, maximum, "MIN-MAX:", min-maximum
        
        sizediff = abs(min-maximum)
        if sizediff == 0:
            sizebonus = 5000
        elif sizediff > 0 and sizediff <= 5:
            sizebonus = 2500
        elif sizediff > 5 and sizediff <= 10:
            sizebonus = 1000
        elif sizediff > 10 and sizediff <= 15:
            sizebonus = 500
        else:
            sizebonus = 0
        
        total = vicbonus + redbonus - blueloss + sizebonus
        
        #Blit scoring info
        temp = gfx.font.render("     YOUR SCORE     ", 1, gfx.palette["red"])
        newspaper.blit(temp, (14,206))
        temp = gfx.font.render("VICTORY BONUS       ", 1, gfx.palette["red"])
        newspaper.blit(temp, (14,222))
        temp = gfx.font.render("RED VOTE BONUS      ", 1, gfx.palette["red"])
        newspaper.blit(temp, (14,238))
        temp = gfx.font.render("BLUE VOTE LOSS      ", 1, gfx.palette["blue"])
        newspaper.blit(temp, (14,254))
        temp = gfx.font.render("SIZING BONUS        ", 1, gfx.palette["red"])
        newspaper.blit(temp, (14,270))
        temp = gfx.font.render("TOTAL SCORE         ", 1, gfx.palette["red"])
        newspaper.blit(temp, (14,302))
        
        #Blit actual scores
        temp = gfx.font.render(str(vicbonus), 1, gfx.palette["red"])
        newspaper.blit(temp, (14+(16*(20-len(str(vicbonus)))),222))
        temp = gfx.font.render(str(redbonus), 1, gfx.palette["red"])
        newspaper.blit(temp, (14+(16*(20-len(str(redbonus)))),238))
        temp = gfx.font.render(str(blueloss), 1, gfx.palette["blue"])
        newspaper.blit(temp, (14+(16*(20-len(str(blueloss)))),254))
        temp = gfx.font.render(str(sizebonus), 1, gfx.palette["red"])
        newspaper.blit(temp, (14+(16*(20-len(str(sizebonus)))),270))
        temp = gfx.font.render(str(total), 1, gfx.palette["red"])
        newspaper.blit(temp, (14+(16*(20-len(str(total)))),302))
        
        #Check if you set a high score
        newscore = False
        message = "CLICK FOR NEXT LEVEL"
        if total > level.highscores[-1][1]:
            game.score = total
            newscore = True
            message = "  NEW HIGH SCORE!!  "
            if game.savesolutions == True:
                pygame.image.save(snapshot, "data//solutions//" + game.levelfn + "-" + str(total) + ".png")
        
        temp = gfx.font.render(message, 1, gfx.palette["red"])
        newspaper.blit(temp, (14,350))
        
        window.blit(newspaper, (115,100))
        pygame.display.update()
        
        looping = True
        counter = 0
        while looping:
            if counter >= 10:
                counter = 0
            for event in pygame.event.get():
                if (event.type == MOUSEBUTTONUP and event.button == 1):
                    looping = False                    
            time = clock.tick(FRAMERATE)

        if newscore:
            return "highscore"
        return "advance"
    else:
        print "You lost so we need some choices about what to do now"
        print "Try Again / Resign"
        temp = gfx.fontbig.render("GAME OVER", 1, gfx.palette["blue"])
        newspaper.blit(temp, (textbox.get_width()/2-temp.get_width()/2,238))
            
        looping = True
        retry = pygame.Rect((46+115,(16*18)+114), (16*5, 16))
        retire = pygame.Rect((14*12+155,(16*18)+114), (16*6, 16))
        while looping:
            temp = gfx.font.render("  RETRY", 1, gfx.palette["white"*(not retry.collidepoint(pygame.mouse.get_pos()))+"red"*(retry.collidepoint(pygame.mouse.get_pos()))])
            newspaper.blit(temp, (14,(16*18)+14))
            temp = gfx.font.render("RETIRE", 1, gfx.palette["white"*(not retire.collidepoint(pygame.mouse.get_pos()))+"red"*(retire.collidepoint(pygame.mouse.get_pos()))])
            newspaper.blit(temp, (14*15,(16*18)+14))
            window.blit(newspaper, (115,100))
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    exitgame(game.levelfn)
                if (event.type == MOUSEBUTTONUP and event.button == 1):
                    if retry.collidepoint(pygame.mouse.get_pos()):
                        looping = False
                        print "Clicked retry"
                        return "restart"
                        #Reload the map
                    elif retire.collidepoint(pygame.mouse.get_pos()):
                        print "Clicked retire"
                        exitgame(game.levelfn)
        pygame.event.clear()
        return True
    
def Highscore(gfx, window, level, game, clock, FRAMERATE):
    gfx.tiles["textbox"] = pygame.image.load("data//gfx//textbox.png")
    textbox = gfx.tiles["textbox"]
    
    levelfn = game.levelfn
    levelhs = level.highscores
    score = game.score
    
    print "New high score"
    print levelfn
    print levelhs
    print "Your score: ", score
    
    #Figure out where your score goes
    hs1 = level.highscores[0][1]
    hs2 = level.highscores[1][1]
    hs3 = level.highscores[2][1]
    hs4 = level.highscores[3][1]
    hs5 = level.highscores[4][1]
    
    print "hs1-5"
    print hs1
    print hs2
    print hs3
    print hs4
    print hs5
    
    if score > hs1:
        slot = 0
    elif score > hs2:
        slot = 1
    elif score > hs3:
        slot = 2
    elif score > hs4:
        slot = 3
    else:
        slot = 4

    if slot == 0:
        level.highscores = [("", score), level.highscores[0], level.highscores[1], level.highscores[2], level.highscores[3]]
    elif slot == 1:
        level.highscores = [level.highscores[0], ("", score), level.highscores[1], level.highscores[2], level.highscores[3]]
    elif slot == 2:
        level.highscores = [level.highscores[0], level.highscores[1], ("", score), level.highscores[2], level.highscores[3]]
    elif slot == 3:
        level.highscores = [level.highscores[0], level.highscores[1], level.highscores[2], ("", score), level.highscores[3]]
    elif slot == 4:
        level.highscores = [level.highscores[0], level.highscores[1], level.highscores[2], level.highscores[3], ("", score)]    
    
    temp = gfx.font.render("   - HIGH SCORE -   ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,16))
    temp = gfx.font.render("  ...ENTER NAME...  ", 1, gfx.palette["white"])
    textbox.blit(temp, (14,32))
    colors = ["red", "purple", "yellow", "green", "cyan"]
    postedslot = 0
    for x in xrange(0,5):
        temp = gfx.font.render(level.highscores[x][0], 1, gfx.palette[colors[x]])
        textbox.blit(temp, (14,(x*32)+80))
        temp = gfx.font.render(str(level.highscores[x][1]), 1, gfx.palette[colors[x]])
        textbox.blit(temp, (14+(16*(20-len(str(level.highscores[x][1])))),(x*32)+80))
    
    window.blit(textbox, (115,100))
    pygame.display.update()
    
    looping = True
    yourname = ""
    temp = gfx.font.render("_", 1, gfx.palette[colors[slot]])
    textbox.blit(temp, (14,(slot*32)+80))
    index = 0
    blankname = pygame.Surface((14*16,16))
    blankname.fill((0,0,0))
    while looping:
        temp = gfx.font.render(yourname + (14-len(yourname))*" ", 1, gfx.palette[colors[slot]])
        textbox.blit(blankname, (14,(slot*32)+80))
        textbox.blit(temp, (14,(slot*32)+80))
        window.blit(textbox, (115,100))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == KEYUP:
                print event
                try:
                    letter = chr(event.key)
                    if letter.upper() in "ABCDEFGHIJKLMNOPQRSTUVWXYZ._ 1234567890-?!":
                        yourname = yourname+letter.upper()
                        index += 1
                except:
                    None
                if event.key == 8:
                    yourname = yourname[:-1]
                    index -= 1
                if index < 0:
                    index = 0
                elif index > 14:
                    index = 14
                    yourname = yourname[:14]
                if event.key == 13:
                    print "Submitting name"
                    looping = False
            
        clock.tick(FRAMERATE)
        
    #Done getting your name
    #Write a new high score file
    print "Saving scores"
    level.highscores[slot] = (yourname, score)
    #level.highscores.insert(slot, (yourname, score))
    hsfile = open("data//scores//" + levelfn + ".txt", "w")
    for temp in xrange(0,5):
        print level.highscores[temp]
        hsfile.write(level.highscores[temp][0] + ":" + str(level.highscores[temp][1]) + "\n")
        print "saving stuff..."
        
    print "Score saved"

def exitgame(savelevel):
    print "QUITTING"
    if savelevel == "x":
        exit()
    
    #Read in save data
    savedata = open("data//saved.txt", "r")
    maxlevel = int(savedata.readline())
    print "Max level is ", maxlevel
    
    savelevel = int(savelevel[1:])
    print "SAVELEVEL", savelevel
    
    if savelevel > maxlevel:
        print "Updating save"
        savedata = open("data//saved.txt", "w")
        savedata.write(str(savelevel))
    exit()
    
def Resumegame(window, clock, FRAMERATE, gfx):
    lnames = open("data//lnames.txt", "r")
    levelnames = lnames.readline().split(",")
    
    #Read in save data
    savedata = open("data//saved.txt", "r")
    maxlevel = int(savedata.readline())
    print "Max level is ", maxlevel
    levelnames = levelnames[:maxlevel]
    
    rectangles = []
    print "RESUME GAME"
    
    box = pygame.image.load("data//gfx//textbox.png")
    
    
    temp = gfx.font.render("   CITY SELECTION   ", 1, gfx.palette["white"])
    box.blit(temp, (14,14))
    
    for x in xrange(0, len(levelnames)):
        temp = gfx.font.render(levelnames[x], 1, gfx.palette["white"])
        box.blit(temp, (14,46+(x*16)))
        rectangles.append(pygame.Rect((227+14,100+46+(x*16)), (16*len(levelnames[x]),16)))
    
    window.blit(box, (227,100))
    pygame.display.update()
    
    looping = True
    while looping:
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                exitgame("x")
            if (event.type == MOUSEBUTTONUP and event.button == 1):
                for xyzzy in xrange(0,len(rectangles)):
                    if rectangles[xyzzy].collidepoint(pos):
                        print "You clicked #", xyzzy+1
                        return "l" + str(xyzzy+1)
                        
        #Draw highlighted rectangle if needed
        for x in xrange(0, len(rectangles)):
            if rectangles[x].collidepoint(pos):
                temp = gfx.font.render(levelnames[x], 1, gfx.palette["red"])
                box.blit(temp, (14,46+(x*16)))
            else:
                temp = gfx.font.render(levelnames[x], 1, gfx.palette["white"])
                box.blit(temp, (14,46+(x*16)))
                #print "Not over #", x
        window.blit(box, (227,100))
        pygame.display.update()
        clock.tick(FRAMERATE)
    
def Victory(gfx, window, clock, FRAMERATE):
    textbox = pygame.image.load("data//gfx//textbox.png")
    
    temp = gfx.font.render("  CONGRATULATIONS!  ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,14))
    temp = gfx.font.render("YOU HAVE MANAGED TO ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,46))
    temp = gfx.font.render("GERRYMANDER ALL THE ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,62))
    temp = gfx.font.render("  MAJOR CITIES OF   ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,78))
    temp = gfx.font.render("    ROOSYLVANIA!    ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,94))
    temp = gfx.font.render("THANKS TO YOUR SKILL", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,110))
    temp = gfx.font.render(" GOVERNOR ANDERSON  ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,126))
    temp = gfx.font.render("EASILY WINS THE NEXT", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,142))
    temp = gfx.font.render(" ELECTION. THE RED  ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,158))
    temp = gfx.font.render("  PARTY GOES ON TO  ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,174))
    temp = gfx.font.render("ENABLE ITS WONDEROUS", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,190))
    temp = gfx.font.render(" AGENDA. BY 1990 THE", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,206))
    temp = gfx.font.render("STATE'S WEALTHY ARE ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,222))
    temp = gfx.font.render(" THE RICHEST AND THE", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,238))
    temp = gfx.font.render(" LEAST TAXED IN THE ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,254))
    temp = gfx.font.render(" COUNTRY. NO DOUBT  ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,270))
    temp = gfx.font.render("THE WEALTH TRICKLES ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,286))
    temp = gfx.font.render("   EVER DOWNWARD.   ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,302))
    temp = gfx.font.render("THANK YOU MR. MILLER", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,318))
    temp = gfx.font.render("FOR MAKING THE DREAM", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,350))
    temp = gfx.font.render("    A REALITY...    ", 1, gfx.palette["yellow"])
    textbox.blit(temp, (14,366))
    
    window.blit(textbox, (227,100))
    pygame.display.update()
    
    looping = True
    while looping:
        for event in pygame.event.get():
            if (event.type == MOUSEBUTTONUP and event.button == 1):
                looping = False                    
        time = clock.tick(FRAMERATE)
    
    random.seed()
    
    #Random newspaper effect
    frame = 0
    cutoff = 5*10
    paper = Newspaper("ANDERSON VOWS FOR+TAX CUTS+ +New plan to aid bus-+inesses. Grow jobs.", gfx)
    window.blit(paper, (random.randint(0,800-320), random.randint(0,600-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
    
    frame = 0
    cutoff = 5*10
    paper = Newspaper("FIRE DEPARTMENTS+WILL OPEN SOON+ +Governor says that+fire safety is a+'very big issue'.", gfx)
    window.blit(paper, (random.randint(0,800-320), random.randint(0,600-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
        
    frame = 0
    cutoff = 5*10
    paper = Newspaper("GOVERNMENT UNIONS+BUSTED+ +Looming strikes+averted as govt+cracks down.", gfx)
    window.blit(paper, (random.randint(0,800-320), random.randint(0,600-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
        
    frame = 0
    cutoff = 5*5
    paper = Newspaper("MERCY HOSPITAL HOLDS+FUNDRAISER+ +Slashed budget leads+to charity event", gfx)
    window.blit(paper, (random.randint(0,800-320), random.randint(0,600-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
        
    frame = 0
    cutoff = 5*5
    paper = Newspaper("WIKIVILLE MOURNS+FIRE VICTIMS+ +Unfought fire rages,+17 dead, 6 missing.", gfx)
    window.blit(paper, (random.randint(0,800-320), random.randint(0,600-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
        
    frame = 0
    cutoff = 5*5
    paper = Newspaper("GAS PROFITS, PRICES+SOAR+ +Citizens hurting+as CEOS earn more", gfx)
    window.blit(paper, (random.randint(0,800-320), random.randint(0,600-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
        
    frame = 0
    cutoff = 5*5
    paper = Newspaper("KANGAROO MASCOT DEAD+ +Cream the kangaroo+dead as zoo loses+funding to buy meds", gfx)
    window.blit(paper, (random.randint(0,800-320), random.randint(0,600-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
        
    frame = 0
    cutoff = 5*3
    paper = Newspaper("POLICE PRIVATIZED+ +Funding cuts cause+corporations to take+over law enforcement", gfx)
    window.blit(paper, (random.randint(0,800-320), random.randint(0,600-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
        
    frame = 0
    cutoff = 5*3
    paper = Newspaper("CHILDREN SUFFER+FROM POOR SCHOOLS+ +State ranked 51st on+standardized tests", gfx)
    window.blit(paper, (random.randint(0,800-320), random.randint(0,600-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
        
    frame = 0
    cutoff = 5*3
    paper = Newspaper("PRISONS PACKED+ +Influx of morality-+based laws fills+prisons. 3% citizens+behind bars", gfx)
    window.blit(paper, (random.randint(100,800-320), random.randint(50,550-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)

    frame = 0
    cutoff = 5*1
    paper = Newspaper("YOU CAN'T CUT BACK+ON FUNDING+ +You will regret this", gfx)
    window.blit(paper, (random.randint(100,800-320), random.randint(50,550-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
    
    frame = 0
    cutoff = 5*1
    paper = Newspaper("BLUE PARTY LEADERS+FOUND GUILTY+OF CONSPIRACY+ +Assassination plans+foiled.", gfx)
    window.blit(paper, (random.randint(100,800-320), random.randint(50,550-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
        
    frame = 0
    cutoff = 5*10
    paper = Newspaper("BANKRUPTCY+ +Anderson refuses tax+hikes as govt shuts-+down.", gfx)
    window.blit(paper, (random.randint(100,800-320), random.randint(50,550-160)))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
        
    #window.fill((0,0,0))
    #pygame.display.update()
    frame = 0
    cutoff = 5*1
    paper = Newspaper("SHANTYTOWN RIOTS+'Rooverville' erupts+into chaos in front+of Anderson mansion.+ +At 4:30pm unemployed+and enraged citizens+turned violent as+Anderson continued", gfx)
    window.blit(paper, (240, 140))
    pygame.display.update()
    while frame < cutoff:
        frame += 1
        time = clock.tick(FRAMERATE)
    
    looping = True
    while looping:
        for event in pygame.event.get():
            if (event.type == MOUSEBUTTONUP and event.button == 1):
                looping = False                    
        time = clock.tick(FRAMERATE)
    
    paper = Newspaper("to ignore complaints+on his policies. One+man sparked the riot+throwing rocks at+the balcony. Others+soon followed. At 6,+the mansion was+ablaze, protesters+having stormed it.+Anderson now missing", gfx, False)
    window.blit(paper, (240, 300))
    pygame.display.update()
    looping = True
    while looping:
        for event in pygame.event.get():
            if (event.type == MOUSEBUTTONUP and event.button == 1):
                looping = False                    
        time = clock.tick(FRAMERATE)
    
    #window.fill((0,0,0))
    temp = gfx.fontbig.render("RUNTIME ERROR 204" , 1, gfx.palette["cyan"])
    window.blit(temp,(0,0))
    temp = gfx.fontbig.render("AT 0B40:2405." , 1, gfx.palette["cyan"])
    window.blit(temp,(0,32))
    temp = gfx.fontbig.render("C:\>" , 1, gfx.palette["cyan"])
    window.blit(temp,(0,96))
    pygame.display.update()

    frame = 0
    looping = True
    while looping:
        if frame < 10:
            temp = gfx.fontbig.render("_" , 1, gfx.palette["cyan"])
            window.blit(temp,(96,96))
        else:
            temp = pygame.Surface((32,32))
            temp.fill((0,0,0))
            window.blit(temp,(96,96))
        pygame.display.update()
        for event in pygame.event.get():
            if (event.type == MOUSEBUTTONUP and event.button == 1) or event.type == QUIT:
                looping = False                    
        time = clock.tick(FRAMERATE)    
        frame += 1
        if frame > 20:
            frame = 0
    
    return
    
def Newspaper(article, gfx, heading=True):
    article = article.split("+")
    paper = pygame.Surface((320, 160))
    paper.fill((255,255,255))
    fold = pygame.Surface((320,16))
    fold.fill((170,170,170))
    paper.blit(fold, (0,144))

    if heading:
        temp = gfx.font.render("ROOSYLVANIA RECORD", 1, gfx.palette["black"])
        paper.blit(temp, (160-(18*16)/2,0))
        x = 1
    else:
        x = 0
    
    for line in article:
        temp = gfx.font.render(line, 1, gfx.palette["black"])
        paper.blit(temp, (160-(len(line)*16)/2,16*x))
        x += 1
    return paper
if __name__ == '__main__': main()
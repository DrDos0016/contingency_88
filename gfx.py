import glob
import os

import pygame

class Gfx(object):
    def __init__(self):
        #And just like that I have a dictionary with the file locations of every graphic in the game
        self.gfxlist = {}
        filelist = glob.glob(os.path.join("data", "gfx", "*"))
        for file in filelist:
            self.gfxlist[os.path.basename(file)[:-4]] = file

        #Border stuff, rects for blitting portions of the image, colors for how they should be painted
        self.bordertype = {"nsew":(264,0,24,24), "nse":(240,0,24,24), "nsw":(192,0,24,24), "new":(216,0,24,24), "ns":(144,0,24,24), "ne":(48,0,24,24), "nw":(24,0,24,24), "sew":(168,0,24,24), "ew":(120,0,24,24), "se":(72,0,24,24), "sw":(96,0,24,24), "none":(0,0,24,24)}
        #self.bordercolors = [(85,255,255), (255,85,255), (255,255,85), (85,255,95), (255,170,0), (64,224,208), (148,0,211), (34,139,34), (255,255,255), (100,100,0)]
        self.bordercolors = [(85,255,85), (255,255,85), (255,85,255),  (0, 170, 0), (85,255,255), (0, 170, 170), (170, 0, 170), (170, 85, 0), (255, 255, 255)]
        self.palette = {"blue":(85,85,255), "green":(85,255,85), "cyan":(85,255,255), "red":(255,85,85), "purple":(255,85,255), "yellow":(255,255,85), "white":(255,255,255), "black":(0,0,0), "dgray":(85, 85, 85), "gray":(170, 170, 170), "dblue":(0,0,170), "dgreen":(0, 170, 0), "dcyan":(0, 170, 170), "dred":(170, 0, 0), "dpurple":(170, 0, 170), "dyellow":(170, 85, 0)}

        #Font
        self.font = pygame.font.Font(os.path.join("data", "pcsenior.ttf"), 16)
        self.fontbig = pygame.font.Font(os.path.join("data", "pcsenior.ttf"), 32)

        #Hud
        self.hud = pygame.Surface((224,600))
        self.updatehud = False
        self.hud_message = ""
        self.hud_color = "white"

        #Sound (I'm not making another class for like 4 sounds in the entire game)
        self.sfxzone = pygame.mixer.Sound(os.path.join("data", "audio", "zonetone.ogg"))
        self.sfxnozone = pygame.mixer.Sound(os.path.join("data", "audio", "nozonetone.ogg"))
        self.sfxdist = pygame.mixer.Sound(os.path.join("data", "audio", "dist.ogg"))
        self.sfxunzone = pygame.mixer.Sound(os.path.join("data", "audio", "unzone.ogg"))
        # self.sfxtally = pygame.mixer.Sound(os.path.join("data", "audio", "tally.ogg")) # MISSING FILE

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
        self.tiles["border"] = self.ColorSprite(self.bordercolors[number], pygame.image.load(os.path.join("data", "gfx", "rawborder.png")))

    def DrawHud(self, window, level, cursor, full=False):
        #Create each element of the HUD in text
        if full:
            #Level name
            levelname = self.font.render(level.name.upper(), 0, self.palette["green"])

            #Population
            #Format population
            pop = str(level.population)
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
            for x in range(0,9):
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
            for x in range(0,10):
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
        for x in range(0,len(level.district)):
            temp = str(int(round((level.district[x].size * 100.0) / level.tilecount)))
            if len(temp) == 2:
                temp = " " + temp
            elif len(temp) == 1:
                temp = "  " + temp
            distareas.append(temp)
        usedtiles = 0
        for x in range(0,len(level.district)):
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

        #Tile zone
        self.hud.blit(zoneval, (160, 400))

        #Tile support
        self.hud.blit(supportval, (160,416))

        #Tile concern
        self.hud.blit(concernval, (160,432))

        #Tile details / HUD Message
        if (dtext == [""]):  # If there's no tile text to render, use hud msg
            self.hud_write(window, self.hud_message, self.hud_color)
        else:  # Render the tile text
            if len(dtext) >= 4:
                self.hud.blit(d4val, (16,512))
            if len(dtext) >= 3:
                self.hud.blit(d3val, (16,496))
            if len(dtext) >= 2:
                self.hud.blit(d2val, (16,480))
            if len(dtext) >= 1:
                self.hud.blit(d1val, (16,464))

            self.hud_message = ""  # Reset the HUD message

        #District Area values
            for x in range(0,len(distareas)):
                render = self.font.render(distareas[x], 0, self.bordercolors[x])
                if x % 2 == 0:
                    self.hud.blit(render, (32, 112+(x*8)))
                else:
                    self.hud.blit(render, (144, 104+(x*8)))
            render = self.font.render(str(unused), 0, self.palette["gray"])
            self.hud.blit(render, (144, 176))

        #District building stats?

        window.blit(self.hud, (576,0))

    def hud_write(self, window, message, color_key="white"):
        self.hud_message = message
        self.hud_color = color_key
        lines = message.split("=")
        x = 16
        y = 464
        height = 16

        for line in lines:
            image = self.font.render(line, 0, self.palette[color_key])
            self.hud.blit(image, (x,y))
            y += height

        window.blit(self.hud, (576,0))
        return True

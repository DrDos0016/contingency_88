# Contingency 88 - By Dr. Dos
# Made in 1 month for the SA Gamedev Challenge
import pygame
import os
import glob
import math
import random
import webbrowser
from sys import exit

from pygame.locals import *

from gfx import Gfx
from level import Level
from game import Game
from tile import Tile
from cursor import Cursor
from district import District


os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

def main():
    #Before we do anything let's get our settings:
    try:
        settings = open("settings.cfg", "r")
        vidmode = settings.readline().split("=")[1][:-1]
        solutions = settings.readline().split("=")[1][:-1]
    except:
        vidmode = "WINDOW"
        solutions = "SAVED"

    icon = pygame.image.load(os.path.join("data", "icon.png"))
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

        pos = (pygame.mouse.get_pos()[0] // 24, pygame.mouse.get_pos()[1] // 24)
        if pos[0] < 25:
            tile = (pos[1] * 24) + pos[0]

        #Check for things that would change the hud
        if cursor.tile != tile:
            cursor.tile = tile
            gfx.updatehud = True
        if cursor.lastdist != cursor.districtnum:
            cursor.lastdist = cursor.districtnum #Make the lastdist match
            gfx.updatehud = True

        level.drawmap(window, gfx)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                exitgame(game.levelfn)
            if (event.type == MOUSEBUTTONDOWN):
                finalize = cursor.click((pygame.mouse.get_pos()[0] // 24, pygame.mouse.get_pos()[1] //24), event.button, gfx, window, level, False)
            if (event.type == KEYUP):
                if event.key >= 49 and event.key <= 57:
                    cursor.SetDistrict(event.key - 49, gfx, level)
                if event.key == K_F1:
                    os.startfile("Manual.html")

        if (pygame.mouse.get_pressed()[0]):
            if cursor.lasttile != (pygame.mouse.get_pos()[0] // 24, pygame.mouse.get_pos()[1] // 24):
                cursor.click((pygame.mouse.get_pos()[0] // 24, pygame.mouse.get_pos()[1] // 24), 1, gfx, window, level, True)

        if finalize == "finalize":
            #Can we finalize?
            usedtiles = 0
            for x in range(0,len(level.district)):
                usedtiles += level.district[x].size
            unused = int(round(((level.tilecount - usedtiles) * 100.0) / level.tilecount))
            if unused < 1:

                min = 100
                maximum = 0
                for x in range(0,len(level.district)):
                    temp = int(round((level.district[x].size * 100.0) / level.tilecount))
                    if temp > maximum:
                        maximum = temp
                    if temp < min:
                        min = temp

                sizediff = abs(min-maximum)

                if sizediff <= 20:
                    nextaction = Finalize(gfx, window, level, game, clock, FRAMERATE)
                else:  # Unbalanced districting
                    gfx.hud_write(window, "!! ERROR !!=ZONES MUST BE=BALANCED TO=FINALIZE!", "red")
                    gfx.sfxnozone.play()
            else:  # Incompleting districting
                gfx.hud_write(window, "!! ERRROR !!=MAP NOT FULLY=DISTRICTED", "red")
                gfx.sfxnozone.play()
                pygame.display.update()

        if nextaction != "":
            if nextaction == "restart":
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
                Highscore(gfx, window, level, game, clock, FRAMERATE)
                nextaction = "advance"

            if nextaction == "advance":
                nextaction = ""
                #Reload the level
                window.fill((0,0,0))
                pygame.display.update()
                cursor = Cursor()
                game.nextlevel() #Increase the level
                if game.levelfn == "l-win":
                    Victory(gfx, window, clock, FRAMERATE)
                    exitgame(game.maxlevel)
                level = Level(game.levelfn)
                level.drawmap(window, gfx) #This is a bit overkill to get the population
                gfx.DrawHud(window, level, cursor, True) #Render EVERYTHING.
                tile = 0
                pygame.mixer.music.stop()
                continue

        if gfx.updatehud:
            gfx.DrawHud(window, level, cursor)

        #Tick the clock
        time = clock.tick(FRAMERATE)
    return

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
                webbrowser.open("Manual.html")
        time = clock.tick(FRAMERATE)
    pygame.mixer.music.stop()
    return button

def Finalize(gfx, window, level, game, clock, FRAMERATE):
    snapshot = pygame.Surface((800,600))
    snapshot.blit(window, (0,0))
    textbox = gfx.tiles["textbox"]
    temp = gfx.font.render("-RUNNING SIMLUATION-", 1, gfx.palette["purple"])
    textbox.blit(temp, (14,14))

    for num in range(0,level.maxdistricts):
        temp = gfx.font.render("     DISTRICT " + str(num+1), 1, gfx.bordercolors[num])
        textbox.blit(temp, (14,46+(16*num)))

    window.blit(textbox, (115,100))
    pygame.display.update()

    #Calculate votes one district at a time
    results = []
    for num in range(0,level.maxdistricts):
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

        # print("PRE BUILDING TOTALS")
        # print("-RED:", rvotes, " BLUE:", bvotes)

        #Now take special buildings into account:
        #Schools
        if level.schoolcount > 0:
            if level.district[num].schools == 0:  # Penalize no schools
                blueshift += 1
        #Police
        if level.policecount > 0:
            if level.district[num].pds > 0:  # Reward police
                redshift += 1
        #Fire
        if level.firecount > 0:
            if level.district[num].fds == 0:  # Unused building
                None  # Don't do a thing.
        #Hospitals
        if level.hospitalcount > 0:
            if level.district[num].hospitals > 0:  # Hospital bonus
                blueshift -= 1
        #Prisons
        if level.prisoncount > 0:
            if level.district[num].prisons > 0:  # Prison penalty
                redshift -= 1
        #Voter Drives
        if level.voterdrivecount > 0:
            if level.district[num].voterdrives > 0:
                rvotesum = (rvotes[0])+(rvotes[1])+(rvotes[2])+(rvotes[3])
                bvotesum = (bvotes[0])+(bvotes[1])+(bvotes[2])+(bvotes[3])
                # These += were just = before which meant votes were erased?
                if rvotesum > bvotesum:
                    bvotes[1] += bvotes[3]
                    bvotes[3] = 0
                elif bvotesum > rvotesum:
                    rvotes[1] += rvotes[3]
                    rvotes[3] = 0

        # Apply bonuses/penalties
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


        # Total votes
        rvotesum = (rvotes[0]*100)+(rvotes[1]*50)+(rvotes[2]*30)+(rvotes[3]*10)
        bvotesum = (bvotes[0]*100)+(bvotes[1]*50)+(bvotes[2]*30)+(bvotes[3]*10)

        # Determine district winner
        if rvotesum > bvotesum:
            winner = "red"
        else:
            winner = "blue"

        results.append((rvotesum, bvotesum, winner))

    # Draw the districts won/loss
    temp = gfx.font.render("- ELECTION RESULTS -", 1, gfx.palette["white"])
    textbox.blit(temp, (14,208))
    temp = gfx.font.render("DISTRICTS WON :     ", 1, gfx.palette["red"])
    textbox.blit(temp, (14,224))
    temp = gfx.font.render("DISTRICTS LOST:     ", 1, gfx.palette["blue"])
    textbox.blit(temp, (14,240))


    # Now we have all the results, let's draw us some ~Rectangles~
    bg = pygame.Surface((320,16))
    bg.fill(gfx.palette["dgray"])



    for num in range(0,level.maxdistricts):
        data = results[num]
        # Draw the 100% gray rectangle
        textbox.blit(bg, (13,46+(16*num)))
        rpercent = int(math.floor(data[0] * 100.0 /(data[0]+data[1])))
        bpercent = int(math.ceil(data[1] * 100.0 /(data[0]+data[1])))

        while (rpercent % 5) != 0:
            rpercent = rpercent - 1
        while (bpercent % 5) != 0:
            bpercent = bpercent + 1
        # Start drawing a rectangle #(320 pixels wide, 16px tall)

        for foo in range(1, max(rpercent // 5, bpercent // 5)+1):
            #Draw red bar
            width = 16 * (foo)
            if width > 16*(rpercent // 5):
                width = 16*(rpercent // 5)
            red = pygame.Surface((width,16))
            red.fill(gfx.palette["dred"])
            textbox.blit(red, (13,46+(16*num)))

            #Draw blue bar
            width = 16 * (foo)
            if width > 16*(bpercent // 5):
                width = 16*(bpercent // 5)
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
        textbox.blit(temp, (textbox.get_width() // 2-temp.get_width() // 2,304))
        temp = gfx.fontbig.render("PREVAILS", 1, gfx.palette["red"])
        textbox.blit(temp, (textbox.get_width() // 2-temp.get_width() // 2,336))
        winner = "red"
    else:
        pygame.mixer.music.load("data//audio//lose.ogg")
        pygame.mixer.music.play(1)
        temp = gfx.fontbig.render("BLUE LIES", 1, gfx.palette["blue"])
        textbox.blit(temp, (textbox.get_width() // 2-temp.get_width() // 2,304))
        temp = gfx.fontbig.render("PREVAIL", 1, gfx.palette["blue"])
        textbox.blit(temp, (textbox.get_width() // 2-temp.get_width() // 2,336))
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

    #Newspaper part
    gfx.tiles["textbox"] = pygame.image.load("data//gfx//textbox.png")
    newspaper = gfx.tiles["textbox"]
    bg = pygame.Surface((318,186))
    bg.fill((255,255,255))
    newspaper.blit(bg, (14,14))

    percentwon = int(round(redwins * 100.0 / (redwins + bluewins)))

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

    if percentwon > 50:  # You win, calculate map score

        vicbonus = redwins * 2500
        redbonus = 0
        blueloss = 0
        for item in results:
            redbonus += item[0]
            blueloss += item[1]

        min = 100
        maximum = 0
        for x in range(0,len(level.district)):
            temp = int(round((level.district[x].size * 100.0) / level.tilecount))
            if temp > maximum:
                maximum = temp
            if temp < min:
                min = temp

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

        # Blit scoring info
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

        # Check if you set a high score
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
    else:  # Retry / Retire
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
                        return "restart"
                        #Reload the map
                    elif retire.collidepoint(pygame.mouse.get_pos()):
                        exitgame(game.levelfn)
        pygame.event.clear()
        return True

def Highscore(gfx, window, level, game, clock, FRAMERATE):
    gfx.tiles["textbox"] = pygame.image.load("data//gfx//textbox.png")
    textbox = gfx.tiles["textbox"]

    levelfn = game.levelfn
    levelhs = level.highscores
    score = game.score

    #Figure out where your score goes
    hs1 = level.highscores[0][1]
    hs2 = level.highscores[1][1]
    hs3 = level.highscores[2][1]
    hs4 = level.highscores[3][1]
    hs5 = level.highscores[4][1]

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
    for x in range(0,5):
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
                    looping = False

        clock.tick(FRAMERATE)

    #Done getting your name
    # Write a new high score file
    level.highscores[slot] = (yourname, score)
    hsfile = open("data//scores//" + levelfn + ".txt", "w")
    for temp in range(0,5):
        hsfile.write(level.highscores[temp][0] + ":" + str(level.highscores[temp][1]) + "\n")

def exitgame(savelevel):
    if savelevel == "x":
        exit()

    # Read in save data
    savedata = open("data//saved.txt", "r")
    maxlevel = int(savedata.readline())
    savelevel = int(savelevel[1:])

    if savelevel > maxlevel:
        savedata = open("data//saved.txt", "w")
        savedata.write(str(savelevel))
    exit()

def Resumegame(window, clock, FRAMERATE, gfx):
    lnames = open("data//lnames.txt", "r")
    levelnames = lnames.readline().split(",")

    #Read in save data
    savedata = open("data//saved.txt", "r")
    maxlevel = int(savedata.readline())
    levelnames = levelnames[:maxlevel]
    rectangles = []

    box = pygame.image.load("data//gfx//textbox.png")
    temp = gfx.font.render("   CITY SELECTION   ", 1, gfx.palette["white"])
    box.blit(temp, (14,14))

    for x in range(0, len(levelnames)):
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
                for xyzzy in range(0,len(rectangles)):
                    if rectangles[xyzzy].collidepoint(pos):
                        return "l" + str(xyzzy+1)

        #Draw highlighted rectangle if needed
        for x in range(0, len(rectangles)):
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

if __name__ == '__main__':
    main()

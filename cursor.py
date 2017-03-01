import pygame

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
            gfx.sfxdist.play()  # Play tone
            return False
        elif button == 5:
            self.lastdist = self.districtnum
            self.districtnum -= 1
            if self.districtnum < 0:
                self.districtnum = level.maxdistricts - 1
            gfx.makeborder(self.districtnum)
            gfx.sfxdist.play()  # Play tone
            return False

        if (button == 3):  # Fill tool
            olddistrict = level.map[(pos[1] * 24) + pos[0]].district
            self.fill(level, gfx, window, pos, olddistrict)
            self.lastaction = "fill"
            self.fillcount = 0
            return False

        if pos[0] >= 24: #  Finalize button
            if self.finalize.collidepoint(pygame.mouse.get_pos()):
                return "finalize"
            return False

        #DISTRICTING:

        #Do nothing if you're on non-puzzle map tiles
        if (level.map[tile].id) == "00":
            return False


        if ((level.map[tile].district) != self.districtnum):
            if holding and self.lastaction != "district":
                return False  # Holding down a button but not districting

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
                    gfx.sfxnozone.play() #Play tone
                    return False  # Districting <tile> would cause a gap

            #Reduce count of old district
            if level.map[tile].district != -1:
                # Check if you can safely redistrict the tile without breaking a district into pieces
                if not self.CanDelete(level, gfx, window, pos, level.map[tile].district):
                    gfx.sfxnozone.play() #Play tone
                    return False  # Deleting would break up district
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

            # Draw marked tile border
            window.blit(gfx.tiles["border"], (pos[0]*24,pos[1]*24), self.chooseborder(tile, gfx, level.map, self.districtnum))
            if not holding:
                self.lastaction = "district"
                gfx.sfxzone.play() #Play tone
        else:
            if holding and self.lastaction != "delete":
                return False  # Holding to erase, but it's a different district

            # Check if you can safely redistrict the tile without breaking a district into pieces
            if not self.CanDelete(level, gfx, window, pos, level.map[tile].district):
                gfx.sfxnozone.play() #Play tone
                return False  # Deleting would break up the district
            else:
                level.district[level.map[tile].district].size -= 1
            window.blit(gfx.tiles["blank"], (pos[0]*24,pos[1]*24))
            window.blit(level.map[tile].image, (pos[0]*24,pos[1]*24))
            level.map[tile].district = -1
            if not holding:  # Successful deletion
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
                gfx.sfxunzone.play()
        return True

    def chooseborder(self, tile, gfx, map, districtnum):
        return gfx.bordertype["nsew"]  # This might be something to go back to later, but don't get hung up on fancy bordering

    def fill(self, level, gfx, window, pos, olddistrict):
        x = pos[0]
        y = pos[1]
        tile = (pos[1] * 24) + pos[0]

        # If the fill is just starting, move north until you hit a border before clicking
        if self.fillcount == 0:
            while True:
                if level.map[tile].district == olddistrict:
                    if y - 1 >= 0:
                        y -= 1
                        tile = (y * 24) + pos[0]
                    else: #Same code as below?
                        y += 1
                        tile = (y * 24) + pos[0]
                        break
                else:
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

        # Get the target tile
        tile = (pos[1] * 24) + pos[0]

        # If this tile is the entirety of the district go nuts and delete it
        if len(level.district[level.map[tile].district].tiles) == 1:
            level.district[level.map[tile].district].tiles.remove(tile)
            level.map[tile].district = olddistrict
            return True

        # Get the target tile's district #
        workingdist = level.map[tile].district
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

        # Remove target tile from the district
        level.district[level.map[tile].district].tiles.remove(tile)
        level.map[tile].district = -1

        self.DeletionCheck(level, level.district[olddistrict].tiles, keytiles, keytiles[0], keytiles[0])

        if len(self.usefultiles) == len(level.district[olddistrict].tiles):
            level.map[tile].district = olddistrict
            return True  # Can delete
        else:
            level.district[olddistrict].tiles.append(tile) # Put the tile back in the district list
            level.map[tile].district = olddistrict # Set the tile's district
            return False  # Can't delete

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
            return  # District unused on this map
        self.lastdist = self.districtnum
        self.districtnum = num
        gfx.makeborder(self.districtnum)
        gfx.sfxdist.play() # Play tone
        return False

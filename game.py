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

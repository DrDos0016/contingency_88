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

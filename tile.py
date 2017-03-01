class Tile(object):
    def __init__(self, image, id):
        typedict = {"00":"nonpuzzle", "01":"blue10", "02":"blue5", "03":"blue3", "04":"blue1", "05":"red1", "06":"red3", "07":"red5", "08":"red10", "09":"school", "10":"police", "11":"fire", "12":"hospital", "13":"prison", "14":"voterreg"}
        zonedict = {"00":"", "01":"HOME", "02":"HOME", "03":"HOME", "04":"HOME", "05":"HOME", "06":"HOME", "07":"HOME", "08":"HOME", "09":"SCHL", "10":"PLDP", "11":"FRDP", "12":"HSPT", "13":"PRSN", "14":"VOTE"}
        supportdict = {"00":"", "01":"BLUE", "02":"BLUE", "03":"BLUE", "04":"BLUE", "05":"RED", "06":"RED", "07":"RED", "08":"RED", "09":"", "10":"", "11":"", "12":"", "13":"", "14":""}
        concerndict = {"00":"", "01":"MAX", "02":"HIGH", "03":"AVG", "04":"LOW", "05":"LOW", "06":"AVG", "07":"HIGH", "08":"MAX", "09":"", "10":"", "11":"", "12":"", "13":"", "14":""}
        detailsdict = {"00":"", "01":"100 VOTES BUT=NOT FOR RED.=ZONE THEM OUT=OR BE DEAD.", "02":"50 VOTES YET=ALL ARE BLUE.=ZONE SAFELY=OR BE THROUGH", "03":"30 BLUE VOTES=COULD BE MORE=ZONE AWAY TO=EVEN SCORE", "04":"10 BLUE VOTES=WON'T BOTHER=YOU.UNTIL RED=LOSES BY TWO.", "05":"RESIDENTIAL=AREA WITH 10=EXPECTED RED=VOTERS.", "06":"RESIDENTIAL=AREA WITH 30=EXPECTED RED=VOTERS.", "07":"RESIDENTIAL=AREA WITH 50=EXPECTED RED=VOTERS.", "08":"100 VOTERS=AT THE CORE=THEY KNOW WHO=TO VOTE FOR!", "09":"SCHOOLS HELP=KIDS TO GROW=IGNORING THIS=WOULD BE LOW.", "10":"DO BE TOUGH=ON ANY CRIME=TO ABIDE RED=PARTY LINE", "11":"FIRE DEPT.=FIRE DEPT.2=FIRE DEPT.3=FIRE DEPT.4", "12":"LAUGHTER IS=BEST MEDICINE=NO BLUE CRIES=IS A SURE WIN", "13":"MY BACKYARD=HAS NO JAILS.=IF IT CANT GO=SUPPORT FAILS", "14":"I WON IT ALL,=RED GLOATS.=HOW WE DID IT=VIA NEW VOTES"}
        # HUD Message area is 14x4

        self.id = id
        self.type = typedict[id]
        self.zone = zonedict[id]
        self.support = supportdict[id]
        self.concern = concerndict[id]
        self.details = detailsdict[id]
        self.image = image
        self.district = -1

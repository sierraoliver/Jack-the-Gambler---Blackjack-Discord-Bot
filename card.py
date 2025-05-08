class Card:
    def __init__(self, suit, value, card, img, fileName):
        self.suit = suit
        self.value = int(value)
        self.card = card
        self.img = img
        self.fileName = fileName

    def getSuit(self):
        return self.suit
    
    def getValue(self):
        return self.value
    
    def getCard (self):
        return self.card
    
    def setSuit(self, suit):
        self.suit = suit
        return

    def setValue (self, value):
        self.value = value
        return
    
    def setCard (self, card):
        self.card = card
        return
    
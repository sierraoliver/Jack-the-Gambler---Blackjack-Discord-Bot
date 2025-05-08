import discord
import random
from card import Card
from pathlib import Path
import os
from PIL import Image
import time
from dotenv import load_dotenv

data_folder = Path("/Users/sierraoliver/Desktop/personal/discord bot/Jack-the-Gambler---Blackjack-Discord-Bot/Playing Cards/card list/")
card_back = "/Users/sierraoliver/Desktop/personal/discord bot/Jack-the-Gambler---Blackjack-Discord-Bot/Playing Cards/card list/card back.png"

def searchCard(folder, card):
    fileName = card.card.lower() + " " + card.suit.lower() + "s.png"
    card.fileName = fileName

    for root, _, files in os.walk(folder):
        if fileName in files:
            card.img = os.path.join(root,fileName)
    
global currentlyPlaying
currentlyPlaying = False
cardNames = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
global totalCardDeck
totalCardDeck = []
for x in range(0,13,1):
    cardName = cardNames[x]
    card = Card("Diamond",x+1,cardName,'','')
    totalCardDeck.append(card)
    card = Card("Heart",x+1,cardName,'','')
    totalCardDeck.append(card)
    card = Card("Spade",x+1,cardName,'','')
    totalCardDeck.append(card)
    card = Card("Club",x+1,cardName,'','')
    totalCardDeck.append(card)

for x in range (0, len(totalCardDeck),1):
    searchCard(data_folder, totalCardDeck[x])

global currentCardDeck
currentCardDeck = []
global dealerHand 
global playerHand
dealerHand = []
playerHand = []

def dealHand(hand):
   for x in range(0,2,1):
        checkDeck()
        r = random.randint(0,len(currentCardDeck)-1)
        hand.append(currentCardDeck[r]) 
        currentCardDeck.pop(r)

def checkDeck():
    if (len(currentCardDeck)==0):
        setCurrentDeck()

def setCurrentDeck():
    for x in range(0, len(totalCardDeck),1):
        currentCardDeck.append(totalCardDeck[x])

def checkBust(hand):
    total = 0
    busted = False
    
    total = handTotal(hand)
    
    if (total>21):
        busted = True

    return busted

def playerHit(hand):
    checkDeck()
    r = random.randint(0, len(currentCardDeck)-1)
    hand.append(currentCardDeck[r])
    currentCardDeck.pop(r)

def handTotal (hand):
    total = 0
    containsAce = 0
    for x in range (0, len(hand),1):
        if (hand[x].card.__eq__("Ace")):
            total += 11
            containsAce +=1
        elif (hand[x].value >=10):
            total +=10
        else:
            total += hand[x].value
    
    while(total > 21 and containsAce>0):
        total -=10
        containsAce-=1

    return total

def resetHands():
    for x in range (0,len(dealerHand),1):
        dealerHand.pop()
    
    for x in range (0, len(playerHand),1):
        playerHand.pop()

def combineImages(hand):
    imgs = []
    for x in range (0, len(hand), 1):
        img = Image.open(hand[x].img)
        imgs.append(img)
    
    if (currentlyPlaying and hand == dealerHand):
        imgs[0] = Image.open(card_back)
    
    min_height = min(imgs[0].height, imgs[1].height)
    combined_width = 0

    for x in range (0, len(imgs), 1):
        imgs[x] = imgs[x].resize((int(imgs[x].width * min_height / imgs[x].height), min_height))
        combined_width += imgs[x].width

    combined_height = max(imgs[x].height, imgs[x].height)
    combined_image = Image.new("RGB", (combined_width, combined_height))
    
    combined_image.paste(imgs[0], (0, 0))
    for x in range (1, len(imgs), 1):
        combined_image.paste(imgs[x], (imgs[x-1].width*x, 0))
    combined_image.save("combined_image.jpg")

    return "combined_image.jpg"

def printHand(hand):
    for x in range (0, len(hand),1):
        print(hand[x].card + " " + hand[x].suit)

class Client(discord.Client):
    async def on_message(self, message):
        global currentlyPlaying
        if (message.author == self.user):
            return
        
        if(message.content.startswith("hello")):
            await message.channel.send(f"Hi there {message.author}")
            return
        
        if(message.content == ("/play blackjack") and not currentlyPlaying):
            currentlyPlaying = True

            #start blackjack by getting dealer cards + player cards
            dealHand(dealerHand)
            dealHand(playerHand)

            combined = combineImages(dealerHand)
            with open(combined, 'rb') as f:
                pic = discord.File(f, filename = combined)
            await message.channel.send("Dealer Hand:", file = pic)

            combined = combineImages(playerHand)
            with open(combined, 'rb') as f:
                pic = discord.File(f, filename = combined)
            await message.channel.send("Player Hand:", file = pic)

            if (handTotal(playerHand)==21):
                currentlyPlaying = False
                await message.channel.send(f"You got BlackJack!")
                dealerTotal = handTotal(dealerHand)
                playerTotal = handTotal(playerHand)
                if (playerTotal > dealerTotal):
                    await message.channel.send(f"You Beat the Dealer!")
                elif (playerTotal < dealerTotal):
                    await message.channel.send(f"You Lost to the Dealer")
                else:
                    await message.channel.send(f"Push - You tied the Dealer")
                
                combined = combineImages(dealerHand)
                with open(combined, 'rb') as f:
                    pic = discord.File(f, filename = combined)
                await message.channel.send("Dealer Hand:", file = pic)
                resetHands()
                return

            await message.channel.send(f"Would you like to Hit or Stay?")
            return

        if (message.content == "/hit" and (currentlyPlaying)):
            playerHit(playerHand)

            combined = combineImages(playerHand)
            with open(combined, 'rb') as f:
                pic = discord.File(f, filename = combined)
            await message.channel.send("New Hand:", file = pic)

            busted = checkBust(playerHand)
            if (busted):
                await message.channel.send(f"You Busted! - Dealer Wins")
                currentlyPlaying = False
                combined = combineImages(dealerHand)
                with open(combined, 'rb') as f:
                    pic = discord.File(f, filename = combined)
                await message.channel.send("Dealer Hand:", file = pic)
                resetHands()
                return
            else:
                await message.channel.send(f"Would you like to Hit or Stay?")
                return
        
        if (message.content == "/stay" and (currentlyPlaying)):
            currentlyPlaying = False
            dealerTotal = handTotal(dealerHand)

            combined = combineImages(dealerHand)
            with open(combined, 'rb') as f:
                pic = discord.File(f, filename = combined)
            await message.channel.send("Dealer Hand:", file = pic)

            dealerBust = False
            while (dealerTotal <=16):
                await message.channel.send("Dealer Hit ...")
                playerHit(dealerHand)
                time.sleep(1)
                combined = combineImages(dealerHand)
                with open(combined, 'rb') as f:
                    pic = discord.File(f, filename = combined)
                await message.channel.send("Dealer Hand:", file = pic)
                dealerBust = checkBust(dealerHand)
                if (dealerBust):
                    break
                dealerTotal = handTotal(dealerHand)

            if (not dealerBust):
                playerTotal = handTotal(playerHand)
                if (playerTotal > dealerTotal):
                    await message.channel.send(f"You Beat the Dealer!")
                elif (playerTotal < dealerTotal):
                    await message.channel.send(f"You Lost to the Dealer")
                else:
                    await message.channel.send(f"Push - You tied the Dealer")
            
            else:
                await message.channel.send(f"Dealer Busted")
                await message.channel.send(f"You Beat the Dealer!")
            
            resetHands()
            return

        if ((message.content == "/hit" or message.content == "/stay") and not currentlyPlaying):
            await message.channel.send(f"You are not currently playing a blackjack game")
            await message.channel.send(f"To start a game type '/play blackjack'")
            return
        

intents = discord.Intents.default()
intents.message_content = True

load_dotenv()
token = os.getenv("BOT-TOKEN")
client = Client(intents=intents)
client.run(token)
    
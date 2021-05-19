import discord
import os
from replit import db

import re

from keep_alive import keep_alive

token = os.environ['token']

client = discord.Client()


def add_user(user, rating):
    if "user_id" in db.keys():
        user_id = db["user_id"]
        add = True;
        for i in range(len(user_id)):
            if (user_id[i].startswith(user)):
                add = False
        if (add):
            user_id.append(user + ":" + str(rating))
        db["user_id"] = user_id
    else:
      db["user_id"] = [user]

def change_user_rating(user, new_rating):
    user_id = []
    user_id = user_id + list(db["user_id"])
    user_index = 0
    print (str(user_id) + "before change")
    for i in range(len(user_id)):
      if (user_id[i].startswith(user)):
        user_index = i
    db["user_id"][user_index] = user + ":" + str(new_rating)
    return user_id

def get_user_rating(user):
    user_id = []
    user_id = user_id + list(db["user_id"])
    #x = re.search(user, user_id)
    user_index = 0
    for i in range(len(user_id)):
      if (user_id[i].startswith(user)):
        user_index = i
    return user_id[user_index].split(user + ":", 1)[1]


def remove_user(index):
    user_id = db["user_id"]
    if len(user_id) > index:
        del user_id[index]
        db["user_id"] = user_id

def rating_calculator(player1, player2, player1_rating, player2_rating, result):
    development_coefficient = 20;
    player1_rating = int(get_user_rating(player1));
    player2_rating = int(get_user_rating(player2));
    rating_change = round(development_coefficient * (1 - 1/(10**((player1_rating - player2_rating)/400) + 1)));
    print(rating_change)
    if (result == "win"):
        player1_rating = player1_rating + rating_change
        player2_rating = player2_rating - rating_change
    elif (result == "lose" or result == "loss" or result == "lost"):
        player1_rating = player1_rating - rating_change
        player2_rating = player2_rating + rating_change
      
    change_user_rating(player1, player1_rating)
    change_user_rating(player2, player2_rating)

    return player1 + ": " + str(player1_rating) + ", " + player2 + ": " + str(player2_rating)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='The Elo Rating Ladder'))


game_in_progress = 0;
default_rating = 1500;
opponent = "";

@client.event
async def on_message(message):

    global game_in_progress
    global default_rating
    global opponent
    if message.author == client:
        return

    if message.content.startswith('#/startmatch'):
        #print(game_in_progress)
        if (game_in_progress == 1):
          await message.channel.send("a game is already in progress")
          return;
        game_in_progress = 1
        opponent = message.content.split("#/startmatch ", 1)[1]
        await message.channel.send("starting match against: " + opponent)
        #await message.channel.send(str(message.author.id) + " " + message.author.name + " " + str(message.author.discriminator))
        add_user(message.author.name, default_rating)
        add_user(opponent, default_rating)
        #add_user(message.author.name)
        #add_user(message.author.discriminator)

    if message.content.startswith('#/result'):
        if (game_in_progress == 0):
            await message.channel.send("no game in progress")
            return
        game_in_progress = 0;
        result = message.content.split("#/result ", 1)[1]
        author_rating = get_user_rating(message.author.name);
        opponent_rating = get_user_rating(opponent);
        await message.channel.send(str(rating_calculator(message.author.name, opponent, author_rating, opponent_rating, result)))
        opponent = ""


    if message.content.startswith('#/list_users'):
        user_id = []
        if "user_id" in db.keys():
            user_id = user_id + list(db["user_id"])
        await message.channel.send("Users: " + str(user_id))

    if message.content.startswith('#/remove_user'):
        user_id = []
        if "user_id" in db.keys():
            index = int(message.content.split("#/remove_user ", 1)[1])
            remove_user(index)
            user_id = user_id + list(db["user_id"])
        await message.channel.send("Remaining users: " + str(user_id))

    #if message.content.startswith('#/user_rating'):
    #  user = message.content.split("#/user_rating ",1)[1]

keep_alive()
client.run(token)




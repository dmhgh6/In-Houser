# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.template import loader
from .models import Player, Document, Game, OverallPlayer
from .forms import GamesForm
import os, json, uuid

from .forms import DocumentForm

# Create your views here.
def index(request):
    if Document.objects.all().exists():
        filePath = Document.objects.all().get().document.path
        Document.objects.all().delete()
        os.remove(filePath)
    playerList = OverallPlayer.objects.order_by('name')
    context = {'playerList': playerList}
    return render(request, 'inHouseSite/index.html', context)


def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if ".json" in form.instance.document.path:
                parseJsonFile(form.instance.document.path)

            return redirect('index')
    else:
        form = DocumentForm()
    return render(request, 'inHouseSite/model_form_upload.html', {
        'form': form
    })


def games(request):
    if Document.objects.all().exists():
        filePath = Document.objects.all().get().document.path
        Document.objects.all().delete()
        os.remove(filePath)

    if request.method == 'GET':
        form = GamesForm(request.GET)
        if form.is_valid():
            print 'Hello'
            return HttpResponseRedirect('games/')
        else:
            form = GamesForm()

    s = 1
    g = 1


    game = Game.objects.filter(seasonNumber=s, gameNumber=g)
    teamOneList = Player.objects.filter(seasonNumber=s, gameNumber=g, teamNumber=1)
    teamTwoList = Player.objects.filter(seasonNumber=s, gameNumber=g, teamNumber=2)

    context = {'game': game, 'teamOneList': teamOneList, 'teamTwoList': teamTwoList, 'form': form}
    return render(request, 'inHouseSite/season.html', context)


def players(request):
    return render(request, 'inHouseSite/player.html')


def parseJsonFile(filePath):
    game = json.load(open(filePath))

    # Game Information
    g = Game(seasonNumber=game["Season"], gameNumber=game["Game"], map=game["Map"], winner=game["Winner"],
             teamOneScore=game["TeamOneScore"], teamTwoScore=game["TeamTwoScore"])
    g.save()

    # Team One Parsing
    for i in game["TeamOne"]:
        win = 0
        if game["TeamOneScore"] > game["TeamTwoScore"]:
            win = 1

        if OverallPlayer.objects.filter(steamId=i["SteamId"]).exists():
            p = OverallPlayer.objects.get(steamId=i["SteamId"])
            p.kills += i["Kills"]
            p.deaths += i["Deaths"]
            p.assists += i["Assists"]
            p.mvps += i["Mvps"]
            p.roundsPlayed += game["TeamOneScore"] + game["TeamTwoScore"]
            p.roundsWon += game["TeamOneScore"]
            p.gamesWon += win
            p.gamesPlayed += 1

            p.save()

        elif not i["isBot"]:
            p = OverallPlayer(name=i["Name"], kills=i["Kills"], deaths=i["Deaths"], assists=i["Assists"],
                              mvps=i["Mvps"], steamId=i["SteamId"],
                              roundsPlayed=game["TeamOneScore"]+game["TeamTwoScore"], roundsWon=game["TeamOneScore"],
                              gamesPlayed=1, gamesWon=win)
            p.save()

        n = str(i["Name"]) + "_s" + str(game["Season"]) + "_g" + str(game["Game"])
        p1 = Player(nameKey=n, name=i["Name"], kills=i["Kills"], deaths=i["Deaths"], assists=i["Assists"], mvps=i["Mvps"],
                    steamId=i["SteamId"], teamNumber=1, seasonNumber=game["Season"], gameNumber=game["Game"])
        p1.save()

    # Team Two Parsing
    for i in game["TeamTwo"]:
        win = 0
        if game["TeamOneScore"] < game["TeamTwoScore"]:
            win = 1

        if OverallPlayer.objects.filter(steamId=i["SteamId"]).exists():
            p = OverallPlayer.objects.get(steamId=i["SteamId"])
            p.kills += i["Kills"]
            p.deaths += i["Deaths"]
            p.assists += i["Assists"]
            p.mvps += i["Mvps"]
            p.roundsPlayed += game["TeamOneScore"] + game["TeamTwoScore"]
            p.roundsWon += game["TeamTwoScore"]
            p.gamesWon += win
            p.gamesPlayed += 1

            p.save()

        elif not i["isBot"]:
            p = OverallPlayer(name=i["Name"], kills=i["Kills"], deaths=i["Deaths"], assists=i["Assists"], mvps=i["Mvps"],
                       steamId=i["SteamId"], roundsPlayed=game["TeamOneScore"] + game["TeamTwoScore"],
                       roundsWon=game["TeamTwoScore"], gamesPlayed=1, gamesWon=win)
            p.save()

        n = str(i["Name"]) + "_s" + str(game["Season"]) + "_g" + str(game["Game"])
        p2 = Player(nameKey=n, name=i["Name"], kills=i["Kills"], deaths=i["Deaths"], assists=i["Assists"], mvps=i["Mvps"],
                    steamId=i["SteamId"], teamNumber=2, seasonNumber=game["Season"], gameNumber=game["Game"])
        p2.save()


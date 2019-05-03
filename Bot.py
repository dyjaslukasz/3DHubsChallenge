#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 13:06:15 2019

@author: lukasz
"""

import urllib.parse
import urllib.request
import json


class MissingJsonData(Exception):
    
    def __init__(self):
        super(MissingJsonData, self).__init__("Json data not found in server's answer")
        

class WrongJsonData(Exception):
    
    def __init__(self):
        super(WrongJsonData, self).__init__("Not all required fields found in server's answer")
        
    
class RequestError(Exception):
    
    def __init__(self, originalException, triggeringUrl, triggeringMethod, triggeringData):
        super(RequestError, self).__init__()
        self.originalException = originalException
        self.triggeringUrl = triggeringUrl
        self.triggeringMethod = triggeringMethod
        self.triggeringData = triggeringData
        
    def __str__(self):
        string = str(self.originalException)+"\n"
        string += "Error triggering request:\n"
        string += str(self.triggeringUrl)+"\n"
        string += str(self.triggeringMethod)+"\n"
        string += str(self.triggeringData)+"\n"
        return string


def checkForJson(headers):
    return headers['Content-Type'] == "application/json"

def checkData(jsonDict, requiredFields):
    return all( field in jsonDict for field in requiredFields)


def getState():
    dataJson = None
    url = 'http://localhost:5000/hangman/api/gameState'    
    req = urllib.request.Request(url, method = 'GET')
    try:
        with urllib.request.urlopen(req) as response:
           if not checkForJson(response.info()):
               raise MissingJsonData
           data = response.read()
           dataJson = json.loads(data)
           if not checkData(dataJson, ['attemptsLeft', 'currentGuess', 'gameActive', 'score', 'userGuessed', 'userName']):
               raise WrongJsonData
    except (urllib.error.URLError, WrongJsonData, MissingJsonData)  as e:
        raise RequestError(e,req.get_full_url(),req.get_method(),req.data)
    return dataJson
   

def startGame(name):
    url = 'http://localhost:5000/hangman/api/startGame'
    data = {"name":name}
    dataBytes = bytes(json.dumps(data), encoding='utf8')
    req = urllib.request.Request(url, method = 'POST', data=dataBytes, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
           if not checkForJson(response.info()):
               raise MissingJsonData
           data = response.read()
           dataJson = json.loads(data)
           if not checkData(dataJson, ['message']):
               raise WrongJsonData
    except (urllib.error.URLError, WrongJsonData, MissingJsonData) as e:
        raise RequestError(e,req.get_full_url(),req.get_method(),req.data)
    return dataJson['message']
   
    
def makeAGuess(character):
    url = 'http://localhost:5000/hangman/api/tryCharacter'
    data = {"character":character}
    dataBytes = bytes(json.dumps(data), encoding='utf8')
    req = urllib.request.Request(url, method = 'PUT', data=dataBytes, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
           if not checkForJson(response.info()):
               raise MissingJsonData
           data = response.read()
           dataJson = json.loads(data)
           if not checkData(dataJson, ['successfullAttempt']):
               raise WrongJsonData
    except (urllib.error.URLError, WrongJsonData, MissingJsonData) as e:
        raise RequestError(e,req.get_full_url(),req.get_method(),req.data)
    return dataJson['successfullAttempt']


def endGame():
    url = 'http://localhost:5000/hangman/api/endGame'
    req = urllib.request.Request(url, method = 'GET')
    try:
        with urllib.request.urlopen(req) as response:
           if not checkForJson(response.info()):
               raise MissingJsonData
           data = response.read()
           dataJson = json.loads(data)
           if not checkData(dataJson, ['message']):
               raise WrongJsonData
    except (urllib.error.URLError, WrongJsonData, MissingJsonData) as e:
        raise RequestError(e,req.get_full_url(),req.get_method(),req.data)
    return dataJson['message']



def getSortedCharacters(possibleWords):
    charactersFrequencies = dict()
    for word in possibleWords:
        for c in word:
            if not c in charactersFrequencies:
                charactersFrequencies[c] = 1
            else:
                charactersFrequencies[c] += 1
    return list(dict(sorted(charactersFrequencies.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)).keys())


if __name__ == '__main__':
    
    possibleWords = ["3dhubs", "marvin", "print", "filament", "order", "layer"] 
    attemptedLetters = list()
    
    try:
        print(startGame("Bot")) 
        
        active = getState()['gameActive']
        while active:
            print("\n***************************************")
            sortedCharacters = getSortedCharacters(possibleWords)
            sortedCharacters = [character for character in sortedCharacters if not character in attemptedLetters]
            print("Possible characters: ", sortedCharacters)
            
            guess = None
            for character in sortedCharacters:
                if not all( character in word for word in possibleWords):
                    guess = character
                    break
            if guess is None:
                guess = sortedCharacters[0]
                
            attemptedLetters.append(guess)
            guessed = makeAGuess(guess)
            if guessed:
                possibleWords = [ word for word in possibleWords if guess in word ]
            else:
                possibleWords = [ word for word in possibleWords if not guess in word]
            print()
            print("Character attempted: " ,guess)
            print("Result             : " ,guessed)
            print()
            print("New list of words  : ", possibleWords)
            state = getState()
            print(state['currentGuess'])
            active = state['gameActive']
        finalState = getState()
        if finalState['userGuessed']:
            print("Bot won!!")
        else:
            print("Bot lost :(")
        print("Bot's score: ",finalState['score'])
        print(endGame())
        
    except RequestError as e:
        print(e)
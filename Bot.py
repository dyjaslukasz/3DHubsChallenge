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
    """
    Excetipn raised when provided json is missing some entries.

    """
    
    def __init__(self):
        super(MissingJsonData, self).__init__("Json data not found in server's answer")
        

class WrongJsonData(Exception):
    """
    Excetipn raised when provided json contains wrong data.

    """
    
    def __init__(self):
        super(WrongJsonData, self).__init__("Not all required fields found in server's answer")
        
    
    
class RequestError(Exception):
    """
    Excetipn raised when any problem with https request occured. It provides additional
    information on what was the reauest which caused the problem.

    """
    
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
    """
    Checks if header specifieas a json data

    Parameters
    ----------
    headers
        https request header
        
    Returns
    ----------
    bool
        True if header specifieas a json data
    
    """  
    return headers['Content-Type'] == "application/json"




def checkData(jsonDict, requiredFields):
    """
    Checks if dict has all required keys

    Parameters
    ----------
    jsonDict: dict(string,...)
        a dict to check
    requiredFields  : list(string)
        keys required in the dict
        
    Returns
    ----------
    bool
        True if all keys were found in the dict
    
    """  
    return all( field in jsonDict for field in requiredFields)



def getState():
    """
    Asks the game server for the data describing the state of the game. Validates 
    the answer and returns the requested data.
    
    Rsises RequestError.

    Parameters
    ----------
        
    Returns
    ----------
    josn
        json with the data describing the state of the game
    
    """  
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
    """
    Starts the game and sends user's name to the server. Validates 
    the answer and returns server's message.
    
    Rsises RequestError.

    Parameters
    ----------
    name: string
        users name
        
    Returns
    ----------
    string
        server's message
    
    """    
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
    """
    Sends a character guess to the game server. Validates 
    the answer and returns the result.
    
    Rsises RequestError.

    Parameters
    ----------
    character: string
        a guess which needs to be evaluated by the game
        
    Returns
    ----------
    bool
        True if the guess was correct
    
    """
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
    """
    Ends the game. Validates the answer and returns server's message.
    
    Rsises RequestError.

    Parameters
    ----------
        
    Returns
    ----------
    string
        server's message
    
    """    
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
    """
    Provides a list of characters which can be found in the possible words.
    List is soted such that the most frequent characters are in the front.

    Parameters
    ----------
    possibleWords: list(string)
        a list with the words which can be a solution to the game
        
    Returns
    ----------
    list(string)
        a sorted list of characters which can be found in the possible words
    
    """ 
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
    
    #Solve the game by guessing with the most frequent character in the list of the words which 
    #can be a solution of the game. If such a character exists in all the words then use the next most frequent one.
    #This provides some sort of the maximized expected gain.
    
    #If guessed character was proper, remove all entries from the list of possible words which do not have it 
    #If guessed character was not proper, remove all entries from the list of possible words which have it
    
    #Repeat all the procedure untill game is active.
    
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
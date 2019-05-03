#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 18:39:37 2019

@author: lukasz
"""

import Game

class Base:

    def __init__(self):
        self._errorMessage = ""
        self._gameInstance = Game.Core()
        
    def validateInput(self, userInput, lengthCondition, messageOnWrongLength, messageOnWrongCharacters, allowWhitespaces=False):
        if not lengthCondition(len(userInput)):
            self._errorMessage += messageOnWrongLength
            return False
        if not all(x.isalpha() or (allowWhitespaces and x.isspace()) or  x.isdecimal() for x in userInput):
            self._errorMessage += messageOnWrongCharacters
            return False
        return True
    
    def clearErrorMessage(self):
        self._errorMessage = ""


import os

class Option:
    def __init__(self, description, action):
        self.description    = description
        self.action         = action

class InTerminal(Base):
    
    def __init__(self):
        super(InTerminal, self).__init__()
        self.__widthOfDisplay         = 8
        self.__exit                   = False
        
    def run(self):
        options = \
        {
         '1': Option("Play",              self.play),
         '2': Option("Display scores",    self.displayScores),
         '3': Option("Exit",              self.end)
         }
        
        while not self.__exit:
            self.askForOptions(options)
    
    def end(self):
        self._gameInstance.end()
        print("Bye bye")
        self.__exit = True
    
    def askForOptions(self, options):
        properInput     = False
        while not properInput:
            os.system( 'clear' )
            print()
            for key, option in options.items():
                print("[", key, "] - ", option.description)
            self.printPreviousErrors()
            print()
            try:
                userInput = input("Please select an option: ")
            except Exception as e:
                self._errorMessage += "Someone probably wanted to crash the game with input. The following exception was cought:"
                self._errorMessage += str(e)
                continue
            if not userInput in options:
                self._errorMessage += "Wrong option identifier provided"
                continue
            else:
                properInput = True
        options[userInput].action()
      
        
    def displayScores(self):
        os.system( 'clear' )
        try:        
            scores = self._gameInstance.getScores()
        except Game.ScoreDataProblem:
            print("Scores could not be accessed")
        else:
            if len(scores) == 0:
                print("No saved scores")
            else:
                for date, details in scores.items():
                    print(date, end=" ")
                    for value in details.values() :
                        print(value, end=" ")
                    print()
        print()
        print("Press enter to return")
        input()
    
    def play(self):
        lengthCondition = lambda x: x > 0
        name = self.askForTheInformation(lengthCondition, "Please enter your name: ", displayCurrentState=False, allowWhitespaces=True)
        self._gameInstance.start(name)
        lengthCondition = lambda x: x == 1
        while self._gameInstance.active:
            character = self.askForTheInformation(lengthCondition, "Please provide a character as a guess: ")
            self._gameInstance.handleNewCharacter(character)
        os.system( 'clear' )
        self.showCurrent()
        if self._gameInstance.userGuesssed:
            print("Yay. You are amazing. Final score: {0:.2f}".format(self._gameInstance.score))
        else:
            print("Oh c'mon. It's only 6 words to choose from. Final score: {0:.2f}".format(self._gameInstance.score))
        print()
        print("Press enter to continue")
        input()
        self._gameInstance.resetVariables()
        
    def showCurrent(self):
        lengthOfGuess       = len(self._gameInstance.currentGuess)
        emptySpaceInFront   = int((self.__widthOfDisplay-lengthOfGuess)*0.5)
        emptySpaceBehind    = int(self.__widthOfDisplay-lengthOfGuess-emptySpaceInFront)
        
        emptyFront          = " "*emptySpaceInFront
        emptyBack           = " "*emptySpaceBehind
        
        print()
        print(emptyFront, end='')
        for character in self._gameInstance.currentGuess:
            print(character, end='')
        print(emptyBack , end='')
        
        print(" | Attempts left: ", self._gameInstance.attemptsLeft)
        print()
        
    def printPreviousErrors(self):
        if len(self._errorMessage) > 0:
            print(self._errorMessage)
            self.clearErrorMessage()
        
    def printPreviousGuess(self, userInput=None):
        if not userInput is None:
            if len(userInput) > 8:
                userInput = userInput[:8]+"..."
            print("Previous guess: ",userInput)
        
    def askForTheInformation(self, lengthCondition, requestMessage, displayCurrentState=True, allowWhitespaces=False): 
        properInput     = False
        userInput       = None
        while not properInput:
            os.system( 'clear' )
            if displayCurrentState:
                self.showCurrent()
                self.printPreviousGuess(userInput)
            self.printPreviousErrors()
            print()
            try:
                userInput = input(requestMessage)
            except Exception as e:
                self._errorMessage += "Someone probably wanted to crash the game with input. The following exception was cought:"
                self._errorMessage += str(e)
                continue
            properInput = self.validateInput(userInput, lengthCondition, "Invalid number of characters", "Wrong character provided", allowWhitespaces)
        return userInput
        
if __name__ == '__main__':
    
    pass    
            
        
        
        
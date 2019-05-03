#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 18:39:37 2019

@author: lukasz
"""

import Game

class Base:
    """
    Base class for all interfaces of the game (including api).

    """

    def __init__(self):
        """
        Constructor of Interface Base Class. Creates an instance of game's core.
    
        Parameters
        ----------
    
        """
        self._errorMessage = ""
        self._gameInstance = Game.Core()
        
        
        
    def validateInput(self, userInput, lengthCondition, messageOnWrongLength, messageOnWrongCharacters, allowWhitespaces=False):
        """
        Checks if usersInput meets the requirements of length and type of characters.
    
        Parameters
        ----------
        userInput: string
            users guess
        lengthCondition : lambda
            condition which needs to be satisfied by len(userInput)
        messageOnWrongLength: string
            text added to self._errorMessage if length condition failed
        messageOnWrongCharacters: string
            text added to self._errorMessage if characters' type condition failed
        allowWhitespaces: bool
            if True then the provided characters can also be whitespaces
            
        Returns:
        ----------
        bool
            True if input is correct
    
        """        
        if not lengthCondition(len(userInput)):
            self._errorMessage += messageOnWrongLength
            return False
        if not all(x.isalpha() or (allowWhitespaces and x.isspace()) or  x.isdecimal() for x in userInput):
            self._errorMessage += messageOnWrongCharacters
            return False
        return True
    
    
    def clearErrorMessage(self):
        """
        Clears and data stored in self._errorMessage
    
        Parameters
        ----------
        
        """   
        self._errorMessage = ""


import os



class Option:
    """
    Basically a struct holding a description and an action of elements in menu.

    """
    
    def __init__(self, description, action):
        """
        Constructor of Option struct.
    
        Parameters
        ----------
    
        """
        self.description    = description
        self.action         = action



class InTerminal(Base):
    """
    Class which creates game's interface in terminal. Inherits from Interface.Base.

    """    
    
    def __init__(self):
        """
        Constructor of InTerminal. Sets the with of display for the current
        state of the guess.
    
        Parameters
        ----------
    
        """
        super(InTerminal, self).__init__()
        self.__widthOfDisplay         = 8
        self.__exit                   = False
        
        
        
    def run(self):
        """
        Main method of the class, launches the view and is executed as long as 
        interface is active.
    
        Parameters
        ----------
    
        """        
        options = \
        {
         '1': Option("Play",              self.play),
         '2': Option("Display scores",    self.displayScores),
         '3': Option("Exit",              self.end)
         }
        
        while not self.__exit:
            self.askForOptions(options)
    
    
    
    def end(self):
        """
        Enables the condition which terminates the run method and ends game instance.
    
        Parameters
        ----------
    
        """
        self._gameInstance.end()
        print("Bye bye")
        self.__exit = True
    
    
    
    def askForOptions(self, options):
        """
        Creates a querry in terminal asking the user to choose one of the displayed options.
        Question is repeated until the provided choice indicator is correct.
        In case of the latter, an action related to the selected entry is executed.
    
        Parameters
        ----------
        options: dict(string, Option)
            details of possible menu entries
    
        """
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
        """
        Displays the scores saved by the game.
    
        Parameters
        ----------
    
        """
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
        """
        Asks for user's name. Asks for user gesses until the game is active.
        Afterwards dispalys the result.
    
        Parameters
        ----------
    
        """
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
        """
        Prints a line with current state of the word to guess and the amount of remaining attempts. 
    
        Parameters
        ----------
    
        """        
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
        """
        Prints the whole string stored in self._errorMessage. 
    
        Parameters
        ----------
    
        """
        if len(self._errorMessage) > 0:
            print(self._errorMessage)
            self.clearErrorMessage()
        
        
        
    def printPreviousGuess(self, userInput=None):
        """
        Prints the line with the previous guess of the user. 
    
        Parameters
        ----------
        userInput: string
            string to display as user's previous guess
    
        """
        if not userInput is None:
            if len(userInput) > 8:
                userInput = userInput[:8]+"..."
            print("Previous guess: ",userInput)
        
        
        
    def askForTheInformation(self, lengthCondition, requestMessage, displayCurrentState=True, allowWhitespaces=False): 
        """
        Creates a querry in terminal asking the user to provide some information.
        Question is repeated until the provided data is correct.
        In case of the latter, the data is returned.
    
        Parameters
        ----------
        lengthCondition : lambda
            condition which needs to be satisfied by len(userInput)
        requestMessage: string
            a message to display explaining what to enter
        displayCurrentState: bool
            display current state line with every repeated question
        allowWhitespaces: bool
            if True then the provided characters can also be whitespaces
    
        """
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
            
        
        
        
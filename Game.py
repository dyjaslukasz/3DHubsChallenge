#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 18:30:53 2019

@author: lukasz
"""
import random
import pandas
import datetime

import logging
import logging.handlers

#Since game is supposed to be running with some interfaces  (either api or gui), 
#any problems cannot be priinted as output and need to be stored for further 
#handling in the future. Fort tha reason a logger is created.

loggingFormatter       = logging.Formatter(fmt='%(asctime)s %(message)s')
loggingHandler         = logging.handlers.RotatingFileHandler('hangman.log', maxBytes=1024 * 1024)
loggingHandler.setFormatter(loggingFormatter)
logger                 = logging.getLogger('HangmanLogger')
logger.addHandler(loggingHandler)
logger.setLevel(logging.INFO)


class ScoreDataProblem(Exception):
    """
    Exception to handle any score file related problems.

    """
    
    def __init__(self, message):
        """
        Constructor of state ScoreDataProblem.
    
        Parameters
        ----------
        message: string
            detalis of the problem
    
        """
        super(ScoreDataProblem, self).__init__(message)
        logger.info("ScoreDataProblem: "+message)



class Core:
    """
    The logic part of the game.
    The score is calculated when the outcome of the game is known using the formula:
        remainingAttempts/5*50 + (totalSizeOfTheWordToGuess - numberOfUnguessedCharacters)totalSizeOfTheWordToGuess*50

    """
    
    def __init__(self):
        """
        Constructor of Core.
        Sets possible words to guess and defines needed class instance variables.
    
        Parameters
        ----------
        
        """
        self.__possibleWords            = ["3dhubs", "marvin", "print", "filament", "order", "layer"]
        self.resetVariables()
        
        
        
    def resetVariables(self):
        """
        Resets class instance variables' values.
    
        Parameters
        ----------
        
        """
        self.__userName                 = None
        self.__selectedWordId           = None
        self.__currentGuess             = None
        self.__attemptsLeft             = None
        self.__active                   = False
        self.__userGuesssed             = False
        self.__score                    = None
        
        
        
    def start(self, userName):
        """
        Starts the game. Picks one word for user to guess and sets class instance variables' values.
    
        Parameters
        ----------
        userName: string
            the name of the user
        
        """
        self.__userName                 = userName
        self.__selectedWordId           = random.randint(0,len(self.__possibleWords)-1)
        self.__attemptedWrongLetters    = set()
        self.__attemptsLeft             = 5
        self.__currentGuess             = ["_"]*len(self.__possibleWords[self.__selectedWordId])
        self.__active                   = True
        self.__userGuesssed             = False
        self.__score                    = 0
        
        
        
    def end(self):
        """
        Ends the game. Resets class instance variables' values.
    
        Parameters
        ----------
        
        """
        self.resetVariables()
        
        
        
    def handleNewCharacter(self, usersCharacter):
        """
        Checks if user guess a correct character and updates class instance variables.
        If end of the game detected, appends new score with the timestap and user name
        to scores.csv.
        
        If any problem with scores.csv handling is detected, raises ScoreDataProblem.
    
        Parameters
        ----------
        usersCharacter: string
            a signle character given by the user as a guess
            
        Returns
        ----------
        bool
            True if user made a correct guess
        
        """
        success = self.checkCurrentGuess(usersCharacter)
        if not success:
            self.__attemptsLeft -= 1      
            self.__active        = self.__attemptsLeft > 0
        else:
            self.__active        = ("_" in self.__currentGuess)
            if not self.__active:
                self.__userGuesssed = True
        if not self.__active:
            numberOfUnguessed   = self.__currentGuess.count("_")
            totalLength         = len(self.__possibleWords[self.__selectedWordId])
            self.__score        = self.__attemptsLeft/5.0*50.0 + (totalLength-numberOfUnguessed)/totalLength*50.0
            index = pandas.DatetimeIndex([datetime.datetime.now()])
            df = pandas.DataFrame(index=index, data = {'name': self.__userName, 'score': self.__score})
            df.index.name = 'date'
            try:
                with open('scores.csv', 'a') as f:
                    df.to_csv(f, header=f.tell()==0)
            except Exception as e:
                raise ScoreDataProblem(str(e))
        return success
   
    
    @property        
    def userName(self):
        return self.__userName
    
    
    @property        
    def attemptsLeft(self):
        return self.__attemptsLeft
    
    
    @property        
    def currentGuess(self):
        return self.__currentGuess
    
    
    @property     
    def active(self):
        return self.__active
    
    
    @property     
    def userGuesssed(self):
        return self.__userGuesssed
    
    
    @property     
    def score(self):
        return self.__score
    
    
    
    def getScores(self):
        """
        Reads scores.csv and returns its representation as dict.
        
        If any problem with scores.csv handling is detected, raises ScoreDataProblem.
    
        Parameters
        ----------
            
        Returns
        ----------
        dict( timestamp, dict(name:score))
            Dict representation of the data from scores.csv        
        """
        try:
            df = pandas.read_csv('scores.csv', index_col = 0)
        except Exception as e:
            raise ScoreDataProblem(str(e))
        return df.to_dict('index')
        
    
    
    def checkCurrentGuess(self, usersCharacter):
        """
        Checks if the provided character can be found in the word to guess.
    
        Parameters
        ----------
        usersCharacter: string
            character to analyze
            
        Returns
        ----------
        bool
            True if character can be found in the word to guess 
        """
        correctGuess = False
        for idx,character in enumerate(self.__possibleWords[self.__selectedWordId]):
            if character == usersCharacter:
                if self.__currentGuess[idx] == "_":
                    self.__currentGuess[idx] = character
                correctGuess = True
        return correctGuess
                
        
if __name__ == '__main__':
    
    pass
    
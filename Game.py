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


loggingFormatter       = logging.Formatter(fmt='%(asctime)s %(message)s')
loggingHandler         = logging.handlers.RotatingFileHandler('hangman.log', maxBytes=1024 * 1024)
loggingHandler.setFormatter(loggingFormatter)
logger                 = logging.getLogger('HangmanLogger')
logger.addHandler(loggingHandler)
logger.setLevel(logging.INFO)


class ScoreDataProblem(Exception):
    def __init__(self, message):
        super(ScoreDataProblem, self).__init__(message)
        logger.info("ScoreDataProblem: "+message)


class Core:
    
    def __init__(self):
        self.__possibleWords            = ["3dhubs", "marvin", "print", "filament", "order", "layer"]
        self.resetVariables()
        
    def resetVariables(self):
        self.__userName                 = None
        self.__selectedWordId           = None
        self.__currentGuess             = None
        self.__attemptsLeft             = None
        self.__active                   = False
        self.__userGuesssed             = False
        self.__score                    = None
        
    def start(self, userName=None):
        self.__userName                 = userName
        self.__selectedWordId           = random.randint(0,len(self.__possibleWords)-1)
        self.__attemptedWrongLetters    = set()
        self.__attemptsLeft             = 5
        self.__currentGuess             = ["_"]*len(self.__possibleWords[self.__selectedWordId])
        self.__active                   = True
        self.__userGuesssed             = False
        self.__score                    = 0
        
    def end(self):
        self.resetVariables()
        
    def handleNewCharacter(self, usersCharacter):      
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
        try:
            df = pandas.read_csv('scores.csv', index_col = 0)
        except Exception as e:
            raise ScoreDataProblem(str(e))
        return df.to_dict('index')
        
    def checkCurrentGuess(self, usersCharacter):
        correctGuess = False
        for idx,character in enumerate(self.__possibleWords[self.__selectedWordId]):
            if character == usersCharacter:
                if self.__currentGuess[idx] == "_":
                    self.__currentGuess[idx] = character
                correctGuess = True
        return correctGuess
                
        
if __name__ == '__main__':
    
    pass
    
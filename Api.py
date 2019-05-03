#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  1 16:26:47 2019

@author: lukasz
"""

import Game
import Interface
from flask import Flask, jsonify, request

app = Flask("Hangman")

class CustomError(Exception):
    """
    Excetipn handling any problem which needs to be reported back via https.

    """
    
    status_code = 400

    def __init__(self, message, status_code=None):
        """
        Constructor of CustomError Class.
    
        Parameters
        ----------
        message: string
            text returned in json back to the client with the explenation of the problem
        status_code: int
            a custom code of the error which should be returned to the client
    
        """
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        
        
        
    def toDict(self):
        """
        Creates a dict representation of the error's mesage.
    
        Parameters
        ----------
    
        """
        return {'message' : self.message}
        
    
    
@app.errorhandler(CustomError)
def handleCustomError(error):
    """
    Custom handler of CustomError.

    Parameters
    ----------
    error: CustomError
        exception instance which holds the needed data
    
    """
    response = jsonify(error.toDict())
    response.status_code = error.status_code
    return response



class HangmanApi(Interface.Base):
    """
    Class holding the methods used by game's flask web api.

    """
    
    def __init__(self):
        """
        Constructor of HangmanApi Class.
    
        Parameters
        ----------
    
        """
        super(HangmanApi, self).__init__()
    
    
    
    def createGameStateDict(self):
        """
        Creates a dict representation of the game's state.
    
        Parameters
        ----------
        
        Returns
        dict(string,...)
            a dict representation of the game's state
    
        """
        state = dict()
        state['currentGuess']   = self._gameInstance.currentGuess
        state['attemptsLeft']   = self._gameInstance.attemptsLeft
        state['gameActive']     = self._gameInstance.active
        state['userGuessed']    = self._gameInstance.userGuesssed
        state['userName']       = self._gameInstance.userName
        state['score']          = self._gameInstance.score
        return state
    
    
    
    def endGame(self):
        """
        Ends the game, but does not delete its instance.
    
        Parameters
        ----------
        
        Returns
        json
            a jasonified message for the client
    
        """
        self._gameInstance.end()
        return jsonify({'message': "Game ended"})
    
    
    
    def startGame(self):
        """
        Checks if the data from the client with user's name is proper and (re)starts the game.
        
        Rsises CustomError.
    
        Parameters
        ----------
        
        Returns
        json
            a jasonified message for the client
    
        """
        try:
            jsonData = request.get_json(force=True)
        except:
            raise CustomError("Missing or wrong json data in request")
        if not ('name' in jsonData):
            raise CustomError('Missing name field in json data')
        usersInput = jsonData.get('name')
        lengthCondition = lambda x: x > 0
        correctInput = self.validateInput(usersInput, lengthCondition, "Name cannot be empty", "Unsupported characters in name", allowWhitespaces=True)
        if not correctInput:
            raise CustomError(self._errorMessage)
            self.clearErrorMessage()
        self._gameInstance.start(usersInput)
        return jsonify({'message': "Game started"})
    
    
    
    def getGameState(self):
        """
        Provides json with the current state of the game.
    
        Parameters
        ----------
        
        Returns
        json
            a jasonified state of the game
    
        """
        return jsonify(self.createGameStateDict())



    def tryCharacter(self):
        """
        Checks if the data from the client with user's guess is proper and forewards it to the game.
        
        Rsises CustomError.
    
        Parameters
        ----------
        
        Returns
        json
            a jasonified bool which is True if the guess was correct
    
        """
        if not self._gameInstance.active:
            raise CustomError('Game is not active. (Re)start', status_code=412)
        try:
            jsonData = request.get_json(force=True)
        except:
            raise CustomError("Missing or wrong json data in request")
        if not ('character' in jsonData):
            raise CustomError('Missing character field in json data')
        usersInput = jsonData.get('character')
        lengthCondition = lambda x: x == 1
        correctInput = self.validateInput(usersInput, lengthCondition, "Invalid number of characters", "Wrong character provided")
        if not correctInput:
            raise CustomError(self._errorMessage)
            self.clearErrorMessage()
        #here we choose to ignore any exceptions related to score data since it is not related directly to the request
        succesfullAttempt = self._gameInstance.handleNewCharacter(usersInput)
        return jsonify({'successfullAttempt': succesfullAttempt})
    
    
    
    def getScores(self):
        """
        Provides json with all the scores saved by the game.
    
        Parameters
        ----------
        
        Returns
        json
            a jasonified scores saved by the game
    
        """
        try:        
            scores = self._gameInstance.getScores()
        except Game.ScoreDataProblem:
            raise CustomError("Problem with score data handling", status_code=500)
        return jsonify(scores)
    
    
#bind methods to flask requests
InstanceOfApi = HangmanApi()

app.add_url_rule('/hangman/api/endGame',      view_func=InstanceOfApi.endGame,      methods=['GET'])
app.add_url_rule('/hangman/api/startGame',    view_func=InstanceOfApi.startGame,    methods=['POST'])
app.add_url_rule('/hangman/api/gameState',    view_func=InstanceOfApi.getGameState, methods=['GET'])
app.add_url_rule('/hangman/api/tryCharacter', view_func=InstanceOfApi.tryCharacter, methods=['PUT'])
app.add_url_rule('/hangman/api/getScores',    view_func=InstanceOfApi.getScores,    methods=['GET'])

if __name__ == '__main__':
    
    app.run(debug=True)
    
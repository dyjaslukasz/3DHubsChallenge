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
    status_code = 400

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        
    def toDict(self):
        return {'message' : self.message}
        
@app.errorhandler(CustomError)
def handleCustomError(error):
    response = jsonify(error.toDict())
    response.status_code = error.status_code
    return response


class HangmanApi(Interface.Base):
    
    def __init__(self):
        super(HangmanApi, self).__init__()
    
    def createGameStateDict(self):
        state = dict()
        state['currentGuess']   = self._gameInstance.currentGuess
        state['attemptsLeft']   = self._gameInstance.attemptsLeft
        state['gameActive']     = self._gameInstance.active
        state['userGuessed']    = self._gameInstance.userGuesssed
        state['userName']       = self._gameInstance.userName
        state['score']          = self._gameInstance.score
        return state
    
    def endGame(self):
        self._gameInstance.end()
        return jsonify({'message': "Game ended"})
    
    def startGame(self):
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
        return jsonify(self.createGameStateDict())

    def tryCharacter(self):
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
        try:        
            scores = self._gameInstance.getScores()
        except Game.ScoreDataProblem:
            raise CustomError("Problem with score data handling", status_code=500)
        return jsonify(scores)
    
InstanceOfApi = HangmanApi()

app.add_url_rule('/hangman/api/endGame',      view_func=InstanceOfApi.endGame,      methods=['GET'])
app.add_url_rule('/hangman/api/startGame',    view_func=InstanceOfApi.startGame,    methods=['POST'])
app.add_url_rule('/hangman/api/gameState',    view_func=InstanceOfApi.getGameState, methods=['GET'])
app.add_url_rule('/hangman/api/tryCharacter', view_func=InstanceOfApi.tryCharacter, methods=['PUT'])
app.add_url_rule('/hangman/api/getScores',    view_func=InstanceOfApi.getScores,    methods=['GET'])

if __name__ == '__main__':
    
    app.run(debug=True)
    
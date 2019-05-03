# Hangman game

A simple game of hangman with in-terminal user interface and flask-based web API.
Created as the solution to 3DHubs Challenge.

It was supposed to take approximatelly 4 hours to create this application. However, since the implementaion of the web API is a totally new thing to me, I decided to take this opportunity to learn and try it out.
As the result, the developement took me way more than 4 hours. Since the time limit was violated any way, I decided to add a documentation and a bot which always wins the game and comunicates using the web API. The latter one I did for fun.


### Prerequisites

Needed to launch the game in both in-terminal mode and API. 

```
python3  (tested on 3.6)
pandas   (tested on 0.24.2)
flask    (tested on 1.0.2)
urllib3  (tested on 1.24.2)

```

## Tests

A bot is a kind of automated client, which test the server. I have not added unit-tests, because then I would extend the time even more. Wrong prorities? Maybe. This version of the code is the first one which makes all I wanted it to do 
so if I continued the developement, unit-tests would be the first thing on my to-do list.

## Running


### In-terminal

To launch in-terminal interface:

```
python Execute.py

```

### Web API

To launch web API server of the game:

```
python Execute.py -a

```

Then using `curl` as the example,

-to start the game:

```
curl -i -H "Content-Type: application/json" -X POST -d '{"name":"USER NAME"}' http://localhost:5000/hangman/api/startGame

```

-to make a guess:

```
curl -i -H "Content-Type: application/json" -X PUT -d '{"character":"x"}' http://localhost:5000/hangman/api/tryCharacter

```

-to get the status of the game:

```
curl -i -X GET http://localhost:5000/hangman/api/gameState

```

-to end the game:

```
curl -i -X GET http://localhost:5000/hangman/api/endGame

```

-to get saved scores:

```
curl -i -X GET http://localhost:5000/hangman/api/getScores

```

### Launching the bot

```
./LetThemFight.sh

```
Script starts a temporary game server in the background, launches the bot, displays the results and the solution process and kills the server.


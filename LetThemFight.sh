#!/bin/sh

python3 Execute.py -a > /dev/null 2>&1 &
BACK_PID=$!
echo "Starting Hangman server..."
sleep 3
echo "Bot starts to play"
python3 Bot.py

echo "Killing Hangman server..."
kill $BACK_PID

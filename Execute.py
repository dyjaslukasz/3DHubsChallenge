#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  2 21:51:31 2019

@author: lukasz
"""
import Api
import Interface

if __name__ == '__main__':
    
    """
    Launch either terminal interface or api server.

    """
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Hangman Game')
    
    parser.add_argument('-a', '--api', action="store_true", default=False,
                        help='launch hangman\'s web API instead of in-terminal interface')
    
    args = parser.parse_args()
    
    if args.api:
        Api.app.run()
    else:
        Interface.InTerminal().run()
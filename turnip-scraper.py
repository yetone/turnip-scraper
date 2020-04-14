from __future__ import print_function
import requests
import os
import threading
import sys
import argparse
import time
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15'}
COOKIES = {
    '__cfduid': 'db1eb4357d63476a501dfd1f76aabb4801586213874',
    '_ga_ccuid_v2': 'QZ4CfTwZ5%2B5MIB4UTteY1Q%3D%3D%3A%3Atqrs%2FxGGlTJqOpWSIpLP779obLM2vPSA%2BLvLa0eZwuAK%2BD7aNVO9Aq2lTDojX8daeV%2FBY%2BXYKJPbb03dwo7h%2BPpx%2Bn79l2UlBLki4JLCwVudGcwtnMBqf1n7AlqlVITbvR7b90s43WDj%2F8%2F5o95cTOOPGyiY7NmB%2Feqd41OMT%2FDgMbLq3ElXgct26V47Wup7VkbXR25colMIpB%2Bmh%2FjBJs2%2BFvU1bmeB07Uv4AcBpv%2BVfzIwDPpd6jf48TcF4GvpKKgeZMiUzyGezMYuQKsX2TjIpASDgOyQqvssxyJyc%2BP3anaYIsB6cV0iCvjFxy%2BChN3Gbfftn0hvfKb7dAZjRdP54Thex3SPsBdYitrEGG6f4drVUqWFRo8RryI2q7hM8F2LG3BCptmcdMd5y6nUqkJZteIvYTdo0rLkmdJGkwhKwTlmfn%2BDxf1fz9wf07DD9MZbN2bc4crHJvzoCuFOM5t2K4Ic1ZtPcmrQqGc5kVgOogBMKp9u5m7VrPWoh5sJHqaI7b8h0K2LZGf7mGXws0qZ%2BrFV8m0WQWC0sluyvefwdLm9faZ6JLyhtCWy05Cq6QegJ%2FbLokH84pyhSfU1sXwv78s1BeOhMaOzO0CUg5PhawFfvegd4fS%2BGx%2FEKtY%2FUbFTC69DAa4og3%2Fk13h4uRr95mNhGPTGVPEhqP0BsWljKvZjGlWQ9w3HC2K9Mu8v',
    'adbe_omni_usr': '840c1450-a7b4-5285-90bf-a0c5afec6b91',
}

screenlock = threading.Semaphore(value=1)

turnipcodes = {}

class TurnipScraper:
    def __init__(self, verbose, timeinterval, price, queue):
        self.verbose = verbose
        self.API_URL = "https://api.turnip.exchange"
        self.timeinterval = int(timeinterval)
        self.price = price
        self.queue = queue

    def IslandDictBuilder(self, turnipcodedict):
        turnipcodes[turnipcodedict["turnipCode"]] = {}
        turnipcodes[turnipcodedict["turnipCode"]]['name'] = turnipcodedict["name"]
        turnipcodes[turnipcodedict["turnipCode"]]['fruit'] = turnipcodedict["fruit"]
        turnipcodes[turnipcodedict["turnipCode"]]['turnipPrice'] = turnipcodedict["turnipPrice"]
        turnipcodes[turnipcodedict["turnipCode"]]['hemisphere'] = turnipcodedict["hemisphere"]
        turnipcodes[turnipcodedict["turnipCode"]]['islandTime'] = turnipcodedict["islandTime"]
        turnipcodes[turnipcodedict["turnipCode"]]['description'] = turnipcodedict["description"]
        turnipcodes[turnipcodedict["turnipCode"]]['queued'] = turnipcodedict["queued"]
        turnipcodes[turnipcodedict["turnipCode"]]['creationTime'] = turnipcodedict["creationTime"]

    def IslandDictExists(self, turnipcode):
        if turnipcode in turnipcodes.keys():
            return True
        else:
            return False

    def IslandDictCreationTimeCheck(self, turnipcode):
        if turnipcode["creationTime"] == turnipcodes[turnipcode["turnipCode"]]['creationTime']:
            return True
        else:
            return False

    def IslandDictUpdater(self, turnipcodedict):
        turnipcodes[turnipcodedict["turnipCode"]]['name'] = turnipcodedict["name"]
        turnipcodes[turnipcodedict["turnipCode"]]['fruit'] = turnipcodedict["fruit"]
        turnipcodes[turnipcodedict["turnipCode"]]['turnipPrice'] = turnipcodedict["turnipPrice"]
        turnipcodes[turnipcodedict["turnipCode"]]['hemisphere'] = turnipcodedict["hemisphere"]
        turnipcodes[turnipcodedict["turnipCode"]]['islandTime'] = turnipcodedict["islandTime"]
        turnipcodes[turnipcodedict["turnipCode"]]['description'] = turnipcodedict["description"]
        turnipcodes[turnipcodedict["turnipCode"]]['queued'] = turnipcodedict["queued"]
        turnipcodes[turnipcodedict["turnipCode"]]['creationTime'] = turnipcodedict["creationTime"]

    def Alert(self, turnipcode):
        print("\n[!!!] TURNIP ALERT: TURNIP PRICE AND QUEUE HAVE MET YOUR CRITERIA [!!!]")
        print("Island Name:\t\t%s" % turnipcodes[turnipcode]["name"])
        print("Price:\t\t\t%s bells" % turnipcodes[turnipcode]["turnipPrice"])
        print("Currently in queue:\t%s" % turnipcodes[turnipcode]["queued"])
        print("Description:\t\t%s" % turnipcodes[turnipcode]["description"])
        print("Copy and paste the following link to your browser and join the queue:")
        print("\nhttps://turnip.exchange/island/%s\n\n" % turnipcode)
        os.system("open https://turnip.exchange/island/%s" % turnipcode)

    def CriteriaCheck(self, turnipcode):
        if turnipcodes[turnipcode]["turnipPrice"] >= int(self.price) and turnipcodes[turnipcode]["queued"] <= int(self.queue):
            return True
        else:
            return False

    def NookCrook(self):
        try:
            result = None
            response = requests.get(self.API_URL + "/islands", headers=HEADERS, cookies=COOKIES)
            try:
                print(response)
                result = response.json()
            except json.decoder.JSONDecodeError:
                print("[X] Island API call returned nothing, you may need to set your time interval higher")
                result = None
                
            if result is None:
                return
            
            if 'islands' in result.keys():
                for islanddictionary in result["islands"]:
                    islanddictionary = islanddictionary
                    if not self.IslandDictExists(islanddictionary["turnipCode"]):
                        self.IslandDictBuilder(islanddictionary)
                        if self.CriteriaCheck(islanddictionary["turnipCode"]):
                            self.Alert(islanddictionary["turnipCode"])
                    if self.IslandDictExists(islanddictionary["turnipCode"]):
                        if not self.IslandDictCreationTimeCheck(islanddictionary):
                            self.IslandDictUpdater(islanddictionary)
                            if self.CriteriaCheck(islanddictionary["turnipCode"]):
                                self.Alert(islanddictionary["turnipCode"])
        except requests.ConnectionError:
            print("[X] Islands pull failed, you may need to set your time interval higher")
            pass

    def STALNKS(self):
        try:
            while True:
                self.NookCrook()
                time.sleep(self.timeinterval)
        except KeyboardInterrupt:
            print("You killed it.")
            sys.exit()


class Main:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Turnip Exchange API ')
        parser.add_argument('-s', '--proxy', default=False, help='Specify SOCKS5 proxy (i.e. 127.0.0.1:8123)')
        parser.add_argument('-v', '--verbose', default=False, action='store_true',
                            help='Output in verbose mode while script runs')
        parser.add_argument('-t', '--timeinterval', default=60, help='Time interval to check server in seconds')
        parser.add_argument('-p', '--price', default=300, help='Price to alert on if island price is greater than')
        parser.add_argument('-q', '--queue', default=100, help='Queue to alert on if island queue is less than')

        args = parser.parse_args()
        self.banner()
        scraper = TurnipScraper(args.verbose, args.timeinterval, args.price, args.queue)
        scraper.STALNKS()

    def banner(self):
            print("""
                            @@@@   
          @@@@@@@@@@@      @@@@    
        @@@@@@@@@@@@@@@@  @@       
       @@@@@@@@@@@@@@@@@@@@        
      @@@@@@@@@@@@@@@@@@@@@@@@@    
      @@@@@@@@@@@@@@@@@@@@@@@@@@@  Turnip Exchange Scraper Service
     @@@@@@@@@@@@@@@@@@@@@@@@@@@@  STALNKS!
    @@@@@@@@@@@@@@@@    &@@@@@@@@  Original Author @bashexplode
   @@@@@@@@@@@@@@(         @@@@@   Modified by @VeryCB
   @@@@@@@@@@@@@@          @@@     
       @@@@@@@@@@@                                        
                   """)


if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:
        print("You killed it.")
        sys.exit()

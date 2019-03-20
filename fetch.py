
import requests
import json
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QObject


class Chef:
    Recipes = []

    Helmets = []
    Chests = []
    Gloves = []
    Boots = []
    Rings = []
    Amulets = []
    Belts = []
    Weapons1Slot = []
    Weapons2Slot = []

    def append_item(self, item):
        cat = item["category"]
        if "armour" in cat:
            if cat["armour"][0] == "helmet":
                self.Helmets.append(item)
            elif cat["armour"][0] == "gloves":
                self.Gloves.append(item)
            elif cat["armour"][0] == "chest":
                self.Chests.append(item)
            elif cat["armour"][0] == "boots":
                self.Boots.append(item)
            elif cat["armour"][0] == "shield":
                self.Weapons1Slot.append(item)
        elif "accessories" in cat:
            if cat["accessories"][0] == "ring":
                self.Rings.append(item)
            elif cat["accessories"][0] == "amulet":
                self.Amulets.append(item)
            elif cat["accessories"][0] == "belt":
                self.Belts.append(item)
        elif "weapons" in cat:
            if item["w"] == 1:
                self.Weapons1Slot.append(item)
            elif item["w"] == 2:
                self.Weapons2Slot.append(item)

    def list_recipes(self):
        print()
        print()
        print()
        print("Possible Chaos Recipes available")
        print("Helmets : " + str(len(self.Helmets)))
        print("Chests : " + str(len(self.Chests)))
        print("Gloves : " + str(len(self.Gloves)))
        print("Boots : " + str(len(self.Boots)))
        print("Rings : " + str(int(len(self.Rings) / 2)))
        print("Amulets : " + str(len(self.Amulets)))
        print("1H-Weapons : " + str(int(len(self.Weapons1Slot) / 2)))
        print("2H-Weapons : " + str(len(self.Helmets)))
        print("Weapons Combined : " + str(len(self.Helmets) + int(len(self.Weapons1Slot) / 2)))

    def make_recipes(self):
        print()
        print()
        print()
        print("Making Chaos Recipes")
        self.Recipes.clear()
        stop = False
        while not stop:
            Items = []
            try:
                Items.append(self.Helmets.pop())
            except IndexError as e:
                stop = True
                print("Missing Helmet")
            try:
                Items.append(self.Chests.pop())
            except IndexError as e:
                stop = True
                print("Missing Chest")
            try:
                Items.append(self.Gloves.pop())
            except IndexError as e:
                stop = True
                print("Missing Gloves")
            try:
                Items.append(self.Boots.pop())
            except IndexError as e:
                stop = True
                print("Missing Boots")
            try:
                Items.append(self.Amulets.pop())
            except IndexError as e:
                stop = True
                print("Missing Amulet")
            try:
                Items.append(self.Belts.pop())
            except IndexError as e:
                stop = True
                print("Missing Belt")
            try:
                ringLeft = None
                ringRight = None  # maybe not needed at all but w/e
                ringLeft = self.Rings.pop()
                ringRight = self.Rings.pop()
                Items.append(ringLeft)
                Items.append(ringRight)
            except IndexError as e:
                stop = True
                if not ringLeft is None:
                    self.Rings.append(ringLeft)
                    print("Missing 1 Ring")
                else:
                    print("Missing 2 Rings")
            try:
                Items.append(self.Weapons2Slot.pop())
            except IndexError as e:
                # tried to find 2 handed weapon failed
                # fallback check for 2 1 handed weapons
                try:
                    weaponLeft = None
                    weaponRight = None  # maybe not needed at all but w/e
                    weaponLeft = self.Weapons1Slot.pop()
                    weaponRight = self.Weapons1Slot.pop()
                    Items.append(weaponLeft)
                    Items.append(weaponRight)
                except IndexError as e:
                    stop = True
                    if not weaponLeft is None:
                        self.Weapons1Slot.append(weaponLeft)
                        print("Missing 2H-Weapon and Missing 1 1H-Weapon")
                    else:
                        print("Missing 2H-Weapon and Missing 2 1H-Weapons")
            if not stop:
                cr = ChaosRecipe(Items)
                self.Recipes.append(cr)

        print("Chaos Recipes available: " + str(len(self.Recipes)))


class ChaosRecipe:
    Items = []

    def __init__(self, Items):
        self.Items = Items


class StashMonitor(QObject):
    ACCOUNT_NAME = "name"
    LEAGUE = "league"
    TABS_NUMBER = 0
    POESESSID = "poesessid"
    global_time_start = 0
    whitelisted_tabs = []
    selected_tabs = []
    tabs_loaded = []
    tabs_map = {}

    packet_signal = QtCore.pyqtSignal(dict)

    @QtCore.pyqtSlot()
    def fetchStash(self):
        # Setup the signal-slot mechanism.
        # mySrc = Communicate()
        # mySrc.myGUI_signal.connect(progress)
        rare_items = []
        chef = Chef()
        counter = 0
        #self.whitelist_tabs()
        print("Fetching stash tabs...")
        for tab_index in range(0, self.TABS_NUMBER):
            packet = {"id": tab_index}
            if tab_index not in self.whitelisted_tabs:
                packet["message"] = "Tab ID: " + str(tab_index) + " , Blacklisted"
                print("Tab ID: "
                      + str(tab_index) + " , Blacklisted")
                self.packet_signal.emit(packet)
                continue
            start = time.time()
            #      + " : " + str(rr.json()))
            rr = requests.post("https://www.pathofexile.com/character-window/get-stash-items?" +
                               "accountName=" + self.ACCOUNT_NAME +
                               "&tabIndex=" + str(tab_index) +
                               "&league=" + self.LEAGUE +
                               "&tabs=0"
                               , headers={'Cookie': 'POESESSID=' + self.POESESSID}
                               )
            while rr.status_code == 429:
                packet["message"] = "Tab ID: " + str(tab_index) \
                                    + " , Failed < Too many requests > , Time elapsed : " \
                                    + self.timePrintStr(start) + " ms"
                print("Tab ID: "
                      + str(tab_index) + " , Failed < Too many requests > , Time elapsed : " + self.timePrintStr(
                    start) + " ms")
                self.packet_signal.emit(packet)
                packet["message"] = "Sleep for 60 sec"
                self.packet_signal.emit(packet)
                print("Sleep for 60 sec")
                time.sleep(60)
                start = time.time()
                packet["message"] = "Retrying to fetch"
                self.packet_signal.emit(packet)
                print("Retrying to fetch")
                rr = requests.post("https://www.pathofexile.com/character-window/get-stash-items?" +
                                   "accountName=" + self.ACCOUNT_NAME +
                                   "&tabIndex=" + str(tab_index) +
                                   "&league=" + self.LEAGUE +
                                   "&tabs=0"
                                   , headers={'Cookie': 'POESESSID=' + self.POESESSID}
                                   )

            packet["message"] = "Tab ID: " \
                                + str(tab_index) + " , Success , Time elapsed : " \
                                + self.timePrintStr(start) + " ms"
            self.packet_signal.emit(packet)
            print("Tab ID: "
                  + str(tab_index) + " , Success , Time elapsed : " + self.timePrintStr(start) + " ms")

            # start = time.time()
            json_tab = json.loads(json.dumps(rr.json()))
            items = json_tab["items"]
            #      + " : " + str(rr.json()))

            counter = counter + 1

            for rare_item in [item for item in items]:
                if rare_item["frameType"] == 2 \
                        and not rare_item["identified"] \
                        and 74 >= rare_item["ilvl"] >= 60:
                    rare_items.append(rare_item)
                    chef.append_item(rare_item)

            # print("Tab ID: "
            #     + str(tab_index) + " , Reading JSON and Fetching Chaos recipe Items , Time elapsed : " + timePrintStr(start) + " ms")

        counter = 0
        for rare_item in rare_items:
            tab_id = rare_item["inventoryId"]
            tab_id = int(tab_id.replace("Stash", ""))
            # tab_name = tabs_map[tab_id]["n"]
            # x = rare_item["x"]
            # y = rare_item["y"]
            print("ID: "
                  + str(counter)
                  + " Base: "
                  + str(rare_item["typeLine"])
                  + " - Tab : { id = " + str(tab_id) + " ,"
                  + " name = " + self.tabs_map[tab_id -1]["n"] + " ,"
                  + " x = " + str(rare_item["x"]) + " ,"
                  + " y = " + str(rare_item["y"]) + " }")
            counter = counter + 1

        start = time.time()
        print()
        print()
        print()
        print("Making recipes...")
        chef.list_recipes()
        chef.make_recipes()
        print()
        print()
        print()
        self.timePrint(start)
        print()
        print()
        print()
        print("Total time spent on API calls : " + str(int(self.global_time_start)) + " sec")

    def setLeague(self, leagueName):
        if not self.LEAGUE == leagueName:
            self.selected_tabs = []
            self.tabs_loaded = []
        self.LEAGUE = leagueName.replace(" ", "%20")
        # global global_time_start
        # global_time_start = time.start()

    # and also map them :)
    def whitelist_tabs(self):
        #tab_indexes = []
        for tab in self.selected_tabs:
            #tab_indexes.append(tab["i"])
            # map the tab with each tab id { tab id -> tab["i"] }
            # not used atm. this map
            self.tabs_map[tab["i"]] = tab
            if tab["type"] == "MapStash" \
                    or tab["type"] == "CurrencyStash" \
                    or tab["type"] == "DivinationCardStash" \
                    or tab["type"] == "EssenceStash" \
                    or tab["type"] == "FragmentStash":
                print("Tab " + str(tab["i"]) + " was selected and got removed due to unique tab modifier.")
            else:
                self.whitelisted_tabs.append(tab["i"])


    @QtCore.pyqtSlot()
    def checkAccount(self, accountName, poesessid, fallbackError, fallbackSessionError, connect):
        start = time.time()
        packet = {"id": -1, # small hack to avoid writing new function (progress bar value)
                  "message": "Checking account name..."}
        print("Checking account name...")
        self.packet_signal.emit(packet)
        rr = requests.get("https://www.pathofexile.com/character-window/get-characters?accountName=" + accountName)
        if not rr.status_code == 200:
            fallbackError()
            packet["message"] = "Account name invalid."
            print("Account name invalid.")
            self.packet_signal.emit(packet)
            self.timePrint(start)
            # return False
        else:
            self.ACCOUNT_NAME = accountName
            packet["message"] = "Account name set to " + self.ACCOUNT_NAME + " , Time elapsed : " + self.timePrintStr \
                (start) + " ms"
            print("Account name set to " + self.ACCOUNT_NAME + " , Time elapsed : " + self.timePrintStr(start) + " ms")
            # characters = json.loads(json.dumps(rr.json()))
            self.packet_signal.emit(packet)
            start = time.time()
            packet["message"] = "Checking poesessid..."
            print("Checking poesessid...")
            self.packet_signal.emit(packet)
            rr = requests.post("https://www.pathofexile.com/character-window/get-stash-items?" +
                               "accountName=" + self.ACCOUNT_NAME +
                               "&league=" + "Standard" +
                               "&tabs=0"
                               , headers={'Cookie': 'POESESSID=' + poesessid}
                               )
            if not rr.status_code == 200:
                fallbackSessionError()
                packet["message"] = "poesessid invalid."
                print("poesessid invalid.")
                self.packet_signal.emit(packet)
                self.timePrint(start)
                # return False
            else:
                self.POESESSID = poesessid
                packet["message"] = "poesessid set to " + self.POESESSID + " , Time elapsed : " + self.timePrintStr \
                    (start) + " ms"
                print("poesessid set to " + self.POESESSID + " , Time elapsed : " + self.timePrintStr(start) + " ms")
                self.packet_signal.emit(packet)
                connect()
                # return True

    def fetchTabInfo(self):
        if not self.tabs_loaded:
            rr = requests.post("https://www.pathofexile.com/character-window/get-stash-items?" +
                               "accountName=" + self.ACCOUNT_NAME +
                               "&league=" + self.LEAGUE +
                               "&tabs=1"
                               , headers={'Cookie': 'POESESSID=' + self.POESESSID}
                               )
            tabs = json.loads(json.dumps(rr.json()))
            self.tabs_loaded = tabs["tabs"]
            self.selected_tabs = tabs["tabs"]
            self.TABS_NUMBER = tabs["numTabs"]

        return self.tabs_loaded

    def setTabsSelected(self, tabs):
        #this tabs argument is indexes
        self.selected_tabs = []
        for tab in self.tabs_loaded:
            if tab["i"] in tabs:
                self.selected_tabs.append(tab)
        self.TABS_NUMBER = len(self.selected_tabs)

    def fetchTabInfoGUI(self, eta):
        self.whitelist_tabs()
        self.TABS_NUMBER = len(self.whitelisted_tabs)
        print("Tabs found : " + str(self.TABS_NUMBER))
        print("Estimated waiting time : " + str(int(0.72 * self.TABS_NUMBER)) + " sec")
        eta(str(int(0.72 * self.TABS_NUMBER)), self.TABS_NUMBER)

    # maybe add thread here too
    def fetchLeagueInfo(self):
        start = time.time()
        # packet["message"] = "Retrieving League Information..."
        print("Retrieving League Information...")
        # self.packet_signal.emit(packet)
        # do stuff with characters
        rr = requests.get \
            ("https://www.pathofexile.com/character-window/get-characters?accountName=" + self.ACCOUNT_NAME)
        characters = json.loads(json.dumps(rr.json()))
        rr = requests.get("http://api.pathofexile.com/leagues?compact=1")
        # , headers = {'Cookie': 'POESESSID=' + POESESSID}
        league_info = json.loads(json.dumps(rr.json()))
        if characters:
            for character in characters:
                if character["league"] not in league_info:
                    league_info.append(character["league"])
        print("League Information retrieved, Time elapsed : " + self.timePrintStr(start) + " ms")
        league_info = json.loads(json.dumps(rr.json()))
        #apparently if you have never played a league you have no tabs in it.
        return league_info

    def timePrint(self, start):
        done = time.time()
        elapsed = done - start
        print("Call interval : " + str(int(elapsed * 1000)) + " ms")


    def timePrintStr(self, start):
        done = time.time()
        elapsed = done - start
        self.global_time_start = self.global_time_start + elapsed
        return str(int(elapsed * 1000))

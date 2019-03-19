import requests
import json

ACCOUNT_NAME = "name"
LEAGUE = "league"
TABS_NUMBER = 0
POESESSID = "poesessid"

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
        else:
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
        print("Rings : " + str(int(len(self.Rings)/2)))
        print("Amulets : " + str(len(self.Amulets)))
        print("1H-Weapons : " + str(int(len(self.Weapons1Slot)/2)))
        print("2H-Weapons : " + str(len(self.Helmets)))
        print("Weapons Combined : " + str(len(self.Helmets) + int(len(self.Weapons1Slot)/2)))

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
                print("Missing Helmet")
            try:
                Items.append(self.Boots.pop())
            except IndexError as e:
                stop = True
                print("Missing Helmet")
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
                #tried to find 2 handed weapon failed
                #fallback check for 2 1 handed weapons
                try:
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


rr = requests.post("https://pathofexile.com/character-window/get-stash-items?" +
                   "league=" + LEAGUE +
                   "&accountName=" + ACCOUNT_NAME
                   , headers={'Cookie': 'POESESSID='+POESESSID}
                   )
tabs_number = json.loads(json.dumps(rr.json()))
TABS_NUMBER = tabs_number["numTabs"]
print("Tabs found : " + str(TABS_NUMBER))

rare_items = []
chef = Chef()
counter = 0
for tab_index in range(0, TABS_NUMBER):
    rr = requests.post("https://www.pathofexile.com/character-window/get-stash-items?"+
                       "accountName=" + ACCOUNT_NAME +
                       "&tabIndex=" + str(tab_index) +
                       "&league=" + LEAGUE +
                       "&tabs=0"
                       , headers={'Cookie': 'POESESSID='+POESESSID}
                       )
    json_tab = json.loads(json.dumps(rr.json()))
    items = json_tab["items"]
    print("Tab ID: "
          + str(tab_index)
          + " : " + str(rr.json()))
    counter = counter + 1

    for rare_item in [item for item in items]:
        if rare_item["frameType"] == 2 \
                and not rare_item["identified"] \
                and not rare_item["category"] == "jewels" \
                and 74 >= rare_item["ilvl"] >= 60:
            cat = rare_item["category"]
            if cat == "accessories" and cat["accessories"] == "quiver":
                continue
            else:
                rare_items.append(rare_item)
                chef.append_item(rare_item)


counter = 0
for rare_item in rare_items:
    print("ID: "
          + str(counter)
          + " Base: "
          + str(rare_item["typeLine"]))
    counter = counter + 1

chef.list_recipes()
chef.make_recipes()






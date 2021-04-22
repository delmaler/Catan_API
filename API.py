from PIL import Image, ImageDraw, ImageFont
from Resources import Resource
import Auxilary
from Auxilary import cr_line_len

# ---- Images and Sizes---- #

# start image
background = Image.open('images/src/background2.jpg')

# terrain images and their mask
sheep = Image.open('images/src/Sheep.jpg')
wheat = Image.open('images/src/Wheat.jpg')
wood = Image.open('images/src/Wood.jpg')
dessert = Image.open('images/src/Dessert.jpg')
clay = Image.open('images/src/Clay.jpg')
iron = Image.open('images/src/Iron.jpg')
# mask
terrain_mask = Image.open('images/src/mask.jpg').convert('L')

# current proportion
cr_pr = 0.635 * 0.95
# the proportion of the board relative to original size
proportion = 0.635 * 0.95

# resizing the terrain and its mask by the proportion index
terrain_size = int(sheep.size[0] * proportion), int(sheep.size[1] * proportion)
sheep = sheep.resize(terrain_size)
wheat = wheat.resize(terrain_size)
wood = wood.resize(terrain_size)
dessert = dessert.resize(terrain_size)
clay = clay.resize(terrain_size)
iron = iron.resize(terrain_size)
terrain_mask = terrain_mask.resize(terrain_size)

# height of parts of the terrain after resizing
ter_top_mid_height = int(Image.open('images/src/sizeForY.jpg').size[1] * proportion)
ter_top_height = int(60 * proportion)
ter_mid_height = ter_top_mid_height - ter_top_height

# players colors backgrounds, crossroads masks and locations
yellow = Image.open('images/src/yellow square.jpg')
blue = Image.open('images/src/blue square.jpg')
red = Image.open('images/src/red square.jpg')
green = Image.open('images/src/green square.jpg')
# masks
village_mask = Image.open('images/src/village mask.jpg').convert('L')
city_mask = Image.open('images/src/city mask.jpg').convert('L')

# resizing players backgrounds and crossroads masks by the proportion index
crossroad_size = int(yellow.size[0] * proportion), int(yellow.size[1] * proportion)
yellow = yellow.resize(crossroad_size)
blue = blue.resize(crossroad_size)
red = red.resize(crossroad_size)
green = green.resize(crossroad_size)
village_mask = village_mask.resize(crossroad_size)
city_mask = city_mask.resize(crossroad_size)

# production number image, its mask, font and location
number_img = Image.open('images/src/yellow.jpg')
# mask
number_mask = Image.open('images/src/circle_mask.jpg').convert('L')
# font
font_size = int(48 * proportion)
font = ImageFont.truetype('Library/Fonts/Arial Bold.ttf', font_size)
# location relative to number image location
num_loc = (int(81 * proportion), int(108 * proportion))

# resizing production number and its mask by the terrain size
number_img = number_img.resize(terrain_size)
number_mask = number_mask.resize(terrain_size)

# getting down a line - space
line_space = int((50 / cr_pr) * proportion)

# ---- Locations ---- #

# starting location of the board
start_of_board_x = 165
start_of_board_y = 572

# starting location of the cross roads
start_cr = (int(start_of_board_x + terrain_size[0] * 1.5 - crossroad_size[0] / 2),
            int(start_of_board_y - ter_mid_height - crossroad_size[1] / 2))

# starting location of the log
log_loc = (870, 70)

# starting locations of stats
line_x = 1100
line_y = 500

# ---- Players API info ---- #

# associating players with colors
players = {1: {"background": yellow, "str": "yellow", "color": (255, 242, 0), "name": "none"},
           2: {"background": red, "str": "red", "color": (255, 0, 0), "name": "none"},
           3: {"background": green, "str": "green", "color": (35, 177, 77), "name": "none"},
           4: {"background": blue, "str": "blue", "color": (0, 162, 232)}, "name": "none"}

api_off = True


def turn_api_off():
    global api_off
    api_off = True


def turn_api_on():
    global api_off
    api_off = False


# ---- start of the game functions ---- #

# creating the API
def start_api(board):
    if api_off:
        return
    show_terrain(board.map)
    set_crossroads_locations(board.crossroads)
    set_roads_locations(board.roads, board.crossroads)


# creating the terrain in the start of the game and saving it in images/temp/background.jpg
def show_terrain(board):
    # open starting image of background
    curr_img = background.copy()
    # setting the y location of the start of the terrain
    y = start_of_board_y
    # printing the terrain
    for line in range(5):
        x = start_of_board_x
        if line == 0 or line == 4:
            x += terrain_size[0]
        if line == 1 or line == 3:
            x += int(terrain_size[0] / 2)

        for terrain in board[line]:

            if terrain.resource == Resource.IRON:
                curr_img.paste(iron, (x, y), terrain_mask)
            if terrain.resource == Resource.SHEEP:
                curr_img.paste(sheep, (x, y), terrain_mask)
            if terrain.resource == Resource.CLAY:
                curr_img.paste(clay, (x, y), terrain_mask)
            if terrain.resource == Resource.WHEAT:
                curr_img.paste(wheat, (x, y), terrain_mask)
            if terrain.resource == Resource.WOOD:
                curr_img.paste(wood, (x, y), terrain_mask)
            if terrain.resource == Resource.DESSERT:
                curr_img.paste(dessert, (x, y), terrain_mask)

            if terrain.num != 7:
                curr_num_img = number_img.copy()
                draw = ImageDraw.Draw(curr_num_img)
                if terrain.num == 6 or terrain.num == 8:
                    draw.multiline_text(num_loc, str(terrain.num), fill=(255, 0, 0), font=font)
                else:
                    draw.multiline_text(num_loc, str(terrain.num), fill=(0, 0, 0), font=font)
                curr_num_img.save('images/temp/temp.jpg')
                curr_num_img = Image.open('images/temp/temp.jpg')
                curr_img.paste(curr_num_img, (x, y), number_mask)
            x += terrain_size[0]
        y += ter_top_mid_height
    curr_img.save('images/temp/background.jpg', quality=95)


def set_crossroads_locations(crossroads):
    y = start_cr[1]
    even = False
    step = -int(terrain_size[0] / 2)
    start = start_cr[0]
    for i in range(12):
        x = start
        if even:
            y += ter_top_height
        else:
            start += step
            y += ter_mid_height
        if i == 5:
            step *= -1
        for j in range(len(crossroads[i])):
            crossroads[i][j].api_location = (x, y)
            x += terrain_size[0]
        even = not even


def set_roads_locations(roads, crossroads):
    for line in roads:
        for road in line:
            x1 = road.neighbors[0].api_location[0] + int(crossroad_size[0] / 2)
            y1 = road.neighbors[0].api_location[1] + int(crossroad_size[1] / 2)
            x2 = road.neighbors[1].api_location[0] + int(crossroad_size[0] / 2)
            y2 = road.neighbors[1].api_location[1] + int(crossroad_size[1] / 2)
            road.api_location = (x1, y1, x2, y2)


# ---- During the game functions ---- #


def print_crossroad(cr):
    if api_off:
        return
    curr_img = Image.open("images/temp/background.jpg")
    if cr.ownership is not None:
        color = players[cr.ownership + 1]["background"].copy()
        if cr.building == 1:
            curr_img.paste(color, cr.api_location, village_mask)
        if cr.building == 2:
            curr_img.paste(color, cr.api_location, city_mask)
    curr_img.save("images/temp/background.jpg")


def resize_road(percent, location):
    x1, y1, x2, y2 = location
    x1 += (x2 - x1) * percent
    x2 += (x1 - x2) * percent
    y1 += (y2 - y1) * percent
    y2 += (y1 - y2) * percent
    return x1, y1, x2, y2


def print_road(road):
    if api_off:
        return
    print("road : {(1) : " + str(road.neighbors[0].location) + " (2) : " + str(road.neighbors[1].location) + "}")
    curr_img = Image.open("images/temp/background.jpg")
    if road.owner is not None:
        draw = ImageDraw.Draw(curr_img)
        draw.line(resize_road(0.2, road.api_location), fill=players[road.owner + 1]["color"], width=10)
    curr_img.save("images/temp/background.jpg")


def next_turn(board, turn, rnd, hands, dice=None):
    if api_off:
        return
    # before the dice have been rolled
    img = Image.open("images/temp/background.jpg")
    img = print_log(board, img, rnd, hands[turn].name, dice)
    img = print_stats(img, hands)
    img.save("images/dst/game1/round" + str(rnd) + "turn" + str(turn) + ".jpg")


def print_log(board, img, rnd, turn, dice):
    draw = ImageDraw.Draw(img)
    log_str = "Log:\n\n"
    log_str += "This is round number : " + str(rnd) + ".\n\nNow it is " + turn + "'s turn.\n\n"
    if dice:
        log_str += "Sum of Dice : " + str(board.dice.sum) + "\n\n"
    else:
        log_str += "The dice have not yet been rolled."
    draw.multiline_text(log_loc, log_str, fill=(0, 0, 0), font=font)
    return img


def print_stat(draw, hand, location):
    text = hand.name + ":"
    text += "\n\n    Points: " + str(hand.points)
    text += "\n\n    Wheat: " + str(hand.resources[Resource.WHEAT])
    text += "\n\n    Sheep: " + str(hand.resources[Resource.SHEEP])
    text += "\n\n    Iron: " + str(hand.resources[Resource.IRON])
    text += "\n\n    Wood: " + str(hand.resources[Resource.WOOD])
    text += "\n\n    Clay: " + str(hand.resources[Resource.CLAY])
    text += "\n\n    Active knights: " + str(hand.largest_army)
    text += "\n\n    Sleeping nights: " + str(len(hand.cards["knight"]))
    text += "\n\n    Longest road: " + str(hand.longest_road)
    text += "\n\n    Victory points: " + str(len(hand.cards["victory points"]))
    text += "\n\n    Road builder: " + str(len(hand.cards["road builder"]))
    text += "\n\n    Monopoly: " + str(len(hand.cards["monopole"]))
    text += "\n\n    Year of prosper: " + str(len(hand.cards["year of prosper"])) + "\n\n"
    draw.multiline_text(location, text, fill=(0, 0, 0), font=font)


def print_stats(img, hands):
    draw = ImageDraw.Draw(img)
    draw.multiline_text((line_x, line_y), "Players Stats:", fill=(0, 0, 0), font=font)
    for i, hand in enumerate(hands):
        print_stat(draw, hand, (line_x + 450 * i, line_y + 1 * line_space))
    return img


def create_land_numbers():
    land_nums = {}
    for i in range(2, 13):
        if i != 7:
            land_nums[i] = Image.open('images/source/number' + str(i) + '.JPG')
    return land_nums


def create_profiles() -> list[Image]:
    profiles = [Image.open('images/source/shay_profile.JPG'),
                Image.open('images/source/snow_profile.JPG'),
                Image.open('images/source/shaked_profile.JPG'),
                Image.open('images/source/odeya_profile.JPG')]
    return profiles


def resize_img(path, size):
    img = Image.open(path)
    img = img.resize(size)
    img.save(path)


def resize_arrows(size):
    resize_img('images/source/give.png', size)
    resize_img('images/source/take.png', size)
    resize_img('images/source/give_mask.png', size)
    resize_img('images/source/take_mask.png', size)


class API:
    def __init__(self, names: list[str]):
        self.times = Image.open('images/source/times.png')
        self.times_mask = Image.open('images/source/times_mask.png').convert('L')
        self.give = Image.open('images/source/give.png')
        self.take = Image.open('images/source/take.png')
        self.give_mask = Image.open('images/source/give_mask.png').convert('L')
        self.take_mask = Image.open('images/source/take_mask.png').convert('L')
        self.tester_on = False
        self.names = names
        self.round = 0
        self.turn = 0
        self.action = 0
        self.num_of_players = len(names)
        self.start = Image.open('images/source/start.jpg')
        self.headline_y = 480
        self.font_size = 48
        self.font = ImageFont.truetype('Library/Fonts/Arial Bold.ttf', self.font_size)
        self.draw = ImageDraw.Draw(self.start)
        self.action_img = Image.open('images/source/action.JPG')
        self.action_location = (int((3160 - self.action_img.size[0]) / 2), 30)
        self.do_i_save_copy = False
        self.profiles = create_profiles()
        self.settlements = self.create_settlements()
        self.cities = self.create_cities()
        self.settlement_mask = Image.open('images/source/settlement_mask.png').convert('L')
        self.action_mask = Image.open('images/source/red mask.JPG').resize((1520, 440))
        self.headline_mask = Image.open('images/source/red mask.JPG').resize((250, 140))
        self.dice = []
        for i in range(1, 7):
            self.dice += [Image.open('images/source/die' + str(i) + '.jpg')]
        self.print_profiles()
        self.resource_locations = []
        self.resources = {Resource.CLAY: Image.open('images/source/mini clay.JPG'),
                          Resource.WOOD: Image.open('images/source/mini wood.JPG'),
                          Resource.SHEEP: Image.open('images/source/mini sheep.JPG'),
                          Resource.WHEAT: Image.open('images/source/mini wheat.JPG'),
                          Resource.IRON: Image.open('images/source/mini iron.JPG')}
        self.print_resources_imgs()
        self.resource_img = Image.open('images/source/resource.png')
        self.resource_mask = Image.open('images/source/resource_mask.png').convert('L')
        self.new_turn()
        self.cr_size_w, self.cr_size_h = self.settlement_mask.size
        self.land_w = 245
        self.land_mid_h = 142
        self.land_hat_h = 71
        self.crossroad_start_x = 965 + self.land_w * 1.5 - self.cr_size_w / 2
        self.crossroad_start_y = 765 - self.land_mid_h - self.cr_size_h / 2
        self.copy = None  # type: Image
        self.crossroads = self.set_crossroads_locations()
        self.colors = [(254, 242, 0), (0, 163, 232), (239, 227, 175), (255, 127, 38)]
        self.lands_imgs = {Resource.CLAY: Image.open('images/source/clay land.JPG').resize((246, 287)),
                           Resource.WOOD: Image.open('images/source/wood land.JPG').resize((246, 287)),
                           Resource.SHEEP: Image.open('images/source/sheep land.JPG').resize((246, 287)),
                           Resource.WHEAT: Image.open('images/source/wheat land.JPG').resize((246, 287)),
                           Resource.IRON: Image.open('images/source/iron land.JPG').resize((246, 287)),
                           Resource.DESSERT: Image.open('images/source/dessert.JPG').resize((246, 287))}
        self.land_mask = Image.open('images/source/land_mask.JPG').resize((246, 287)).convert('L')
        self.land_nums = create_land_numbers()
        self.number_mask = Image.open('images/source/number_mask.jpg').convert('L')

    def trade(self, buyer, seller, source, destination, give, take):
        self.tester_on = True
        if buyer == self.num_of_players:
            buyer_img = Image.open('images/source/bank.jpg').resize((111, 94))
        else:
            buyer_img = self.profiles[buyer].resize((111, 94))
        seller_img = self.profiles[seller].resize((111, 94))
        p_w, p_h = seller_img.size
        action_img, y = self.get_action("trade")
        w, h = action_img.size
        a_w, a_h = self.give.size
        action_img.paste(seller_img, (100, 110 + int((140 - p_h) / 2)))
        give_img = self.give.copy()
        self.print_trade_info(20, give_img, source, give)
        action_img.paste(give_img, (140 + p_w, 90 + int((200 - a_h) / 2)), self.give_mask)
        action_img.paste(buyer_img, (w - 100 - p_w, 190 + int((200 - p_h) / 2)))
        action_img.paste(self.take, (w - 140 - p_w - a_w, 203 + int((140 - a_h) / 2)), self.take_mask)
        self.start.paste(action_img, self.action_location)

    def print_trade_info(self, left, arrow, resource, number):
        resource_number = self.get_resource_number(number).resize((100, int(188 * 100 / 223)))
        number_mask = self.resource_mask.resize((100, int(188 * 100 / 223)))
        resource_img = self.resources[resource].resize((70, 60))
        r_w, r_h = resource_img.size
        t_w, t_h = self.times.size
        n_w, n_h = resource_number.size
        arrow.paste(resource_img, (left, 60))
        location_x, location_y = (left + r_w + 20, int(60 + (60 - t_h) / 2))
        arrow.paste(self.times, (location_x, location_y), self.times_mask)
        location_x += t_w + 20
        location_y = int(60 + (60 - n_h) / 2)
        arrow.paste(resource_number, (location_x, location_y), number_mask)

    def write_headline(self, text):
        w, h = self.draw.textsize(text, font=self.font)
        self.draw.multiline_text(((3160 - w) / 2, self.headline_y), text, fill=(255, 255, 255), font=self.font)
        self.headline_y += h * 1.5

    def write_from_right(self, text, line, above, index):
        w, h = self.draw.textsize(text, font=self.font)
        profile_y = 0 if above == -1 else self.profiles[0].size[1]
        self.start.paste(self.profiles[index],
                         (3257 - self.profiles[index].size[0], line + 10 - 50 * above - profile_y))
        self.draw.multiline_text((3237 - self.profiles[index].size[0] - w, line - 150 * above), text, fill=(0, 0, 0),
                                 font=self.font)

    def write_from_left(self, text, line, above, index):
        w, h = self.draw.textsize(text, font=self.font)
        profile_y = 0 if above == -1 else self.profiles[0].size[1]
        self.start.paste(self.profiles[index], (20, line + 10 - 50 * above - profile_y))
        self.draw.multiline_text((40 + self.profiles[index].size[0], line - 150 * above), text, fill=(0, 0, 0),
                                 font=self.font)

    def create_settlements(self):
        settlements = []
        for i in range(self.num_of_players):
            name = 'images/source/settlement' + str(i + 1) + '.png'
            settlements += [Image.open(name).convert("RGBA")]
        return settlements

    def create_cities(self):
        cities = []
        for i in range(self.num_of_players):
            name = 'images/source/city' + str(i + 1) + '.png'
            cities += [Image.open(name).convert("RGBA")]
        return cities

    def new_turn(self):
        self.new_turn_name(self.names[self.turn])

    def new_turn_name(self, name):
        self.action = 0
        self.headline_y = 480
        self.delete_turn()
        self.write_headline("Round " + str(self.round))
        self.write_headline(name)
        self.save_file()

    def show_dice(self, die1, die2):
        d1, d2 = self.dice[die1 - 1], self.dice[die2 - 1]
        w, h = d1.size
        self.start.paste(d1, (int(3160 / 2 - w - 50), 70))
        self.start.paste(d2, (int(3160 / 2 + 50), 70))

    def save_file(self):
        name = "images/destination/round " + str(self.round) + "  turn " + \
               str(self.turn) + "  action " + str(self.action) + ".jpg"
        if self.do_i_save_copy:
            self.copy.save(name)
            self.do_i_save_copy = False
        else:
            self.start.save(name)
        self.action += 1

    def delete_turn(self):
        w, h = self.headline_mask.size
        self.start.paste(self.headline_mask, (int((3160 - w) / 2), self.headline_y))

    def delete_action(self):
        x, y = self.action_location
        self.start.paste(self.action_mask, (x - 10, y - 10))

    def end_turn(self):
        self.round, self.turn = Auxilary.next_turn(self.num_of_players, self.round, self.turn)

    def print_profiles(self):
        self.write_from_left(self.names[0], 1320, 1, 0)
        self.write_from_left(self.names[1], 1320, -1, 1)
        if self.num_of_players > 2:
            self.write_from_right(self.names[2], 1320, 1, 2)
        if self.num_of_players > 3:
            self.write_from_right(self.names[3], 1320, -1, 3)

    def print_resources_imgs(self):
        resources = self.resources
        w, h = resources[Resource.CLAY].size
        profile_height = self.profiles[0].size[1]
        line = 1221 - profile_height
        player_resource_locations = {}
        for r in resources:
            player_resource_locations[r] = (46 + resources[r].size[0], line - h)
            self.start.paste(resources[r], (26, line - h))
            line -= (h + 20)
        self.resource_locations += [player_resource_locations]
        line = 1461 + profile_height
        player_resource_locations = {}
        for r in resources:
            player_resource_locations[r] = (46 + resources[r].size[0], line)
            self.start.paste(resources[r], (26, line))
            line += (h + 20)
        self.resource_locations += [player_resource_locations]
        if self.num_of_players > 2:
            line = 1221 - profile_height
            player_resource_locations = {}
            for r in resources:
                player_resource_locations[r] = (3227 - w - resources[r].size[0], line - h)
                self.start.paste(resources[r], (3247 - w, line - h))
                line -= (h + 20)
            self.resource_locations += [player_resource_locations]
        if self.num_of_players > 3:
            line = 1461 + profile_height
            player_resource_locations = {}
            for r in resources:
                player_resource_locations[r] = (3227 - w - resources[r].size[0], line)
                self.start.paste(resources[r], (3247 - w, line))
                line += (h + 20)
            self.resource_locations += [player_resource_locations]

    def print_action(self, action_name: str):
        w, h = self.action_img.size
        self.start.paste(self.get_action(action_name)[0], self.action_location)

    def get_action(self, action_name) -> (Image, int):
        copy = self.action_img.copy()
        # 1577 - 2333 = 756 * 2 = 1512
        # 443 -25 =~ 420
        w, h = copy.size
        draw = ImageDraw.Draw(copy)
        font = ImageFont.truetype('Library/Fonts/Arial Bold.ttf', 60)
        w_t, h_t = self.draw.textsize(action_name, font=font)
        draw.multiline_text(((w - w_t) / 2, 70), action_name, fill=(0, 0, 0), font=font)
        return copy, 70 + h_t

    def set_crossroads_locations(self):
        crossroads = []
        y = self.crossroad_start_y
        even = False
        step = -int(self.land_w / 2)
        start = self.crossroad_start_x
        for i in range(12):
            line = []
            x = start
            if even:
                y += self.land_hat_h
            else:
                start += step
                y += self.land_mid_h
            if i == 5:
                step *= -1
            for j in range(cr_line_len[i]):
                line.append((int(x), int(y)))
                x += self.land_w
            even = not even
            crossroads.append(line)
        return crossroads

    def get_crossroad_location(self, i, j):
        x, y = self.crossroads[i][j]
        w, h = self.settlement_mask.size
        x += w / 2
        y += h / 2
        return x, y

    def get_road_location(self, i0, j0, i1, j1):
        x0, y0 = self.get_crossroad_location(i0, j0)
        x1, y1 = self.get_crossroad_location(i1, j1)
        return x0, y0, x1, y1

    def point_with_circle(self, x, y, size):
        self.copy = self.start.copy()
        draw = ImageDraw.Draw(self.copy)
        draw.ellipse((x - size, y - size, x + size, y + size), outline=(255, 0, 0, 0), width=10)
        self.do_i_save_copy = True

    def point_on_crossroad(self, i, j):
        x, y = self.get_crossroad_location(i, j)
        self.point_with_circle(x, y, 100)

    def point_on_road(self, i0, j0, i1, j1):
        x0, y0 = self.get_crossroad_location(i0, j0)
        x1, y1 = self.get_crossroad_location(i1, j1)
        x, y = (x0 + x1) / 2, (y0 + y1) / 2
        self.point_with_circle(x, y, 100)

    def print_city(self, index, i, j):
        self.start.paste(self.cities[index], self.crossroads[i][j], self.settlement_mask)

    def print_settlement(self, index, i, j):
        self.start.paste(self.settlements[index], self.crossroads[i][j], self.settlement_mask)

    def print_road(self, index, i0, j0, i1, j1):
        self.draw.line(resize_road(0.2, self.get_road_location(i0, j0, i1, j1)), fill=self.colors[index], width=20)

    def print_resources(self, index, resources):
        for r in resources:
            copy = self.get_resource_number(resources[r])
            if self.do_i_save_copy:
                self.copy.paste(copy, self.resource_locations[index][r], self.resource_mask)
            self.start.paste(copy, self.resource_locations[index][r], self.resource_mask)

    def get_resource_number(self, number):
        w, h = self.resource_img.size
        copy = self.resource_img.copy()
        draw = ImageDraw.Draw(copy)
        font = ImageFont.truetype('Library/Fonts/Arial Bold.ttf', 60)
        w_t, h_t = self.draw.textsize(str(number), font=font)
        draw.multiline_text(((w - w_t) / 2, (h - h_t) / 2), str(number), fill=(0, 0, 0), font=font)
        return copy

    def show_terrain(self, lands):
        # setting the y location of the start of the terrain
        y = 768
        # printing the terrain
        for i, line in enumerate(lands):
            x = 965
            if i == 0 or i == 4:
                x += self.land_w
            if i == 1 or i == 3:
                x += self.land_w / 2
            for land in line:
                land_img = self.lands_imgs[land.resource].copy()
                if land.num != 7:
                    print("\n\n")
                    print(self.land_nums[land.num].size)
                    print(self.number_mask.size)
                    land_img.paste(self.land_nums[land.num], (83, 104), self.number_mask)
                self.start.paste(land_img, (int(x), int(y)), self.land_mask)
                x += self.land_w
            y += (self.land_mid_h + self.land_hat_h)
        self.save_file()

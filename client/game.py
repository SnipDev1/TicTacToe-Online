import threading

import pygame


class Button:
    def __init__(self, position, size, clr=None, cngclr=None, func=None, arg=None):
        if clr is None:
            clr = [100, 100, 100]
        self.clr = clr
        self.size = size
        self.func = func
        self.arg = arg
        self.surf = pygame.Surface(size)
        self.rect = self.surf.get_rect(center=position)

        if cngclr:
            self.cngclr = cngclr
        else:
            self.cngclr = clr

        if len(clr) == 4:
            self.surf.set_alpha(clr[3])

    def draw(self, screen):
        self.mouseover()

        self.surf.fill(self.curclr)
        screen.blit(self.surf, self.rect)

    def mouseover(self):
        self.curclr = self.clr
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.curclr = self.cngclr

    def call_back(self, *args):
        if self.func:
            return self.func(self.arg, *args)


class Text:
    def create_text(self, position, text, font, font_color, font_size, screen):
        font = pygame.font.SysFont(font, font_size)
        text = font.render(text, True, font_color)
        size = screen.get_size()
        text_rect = text.get_rect(center=(position[0], position[1]))

        screen.blit(text, text_rect)


class Game(threading.Thread):
    def func(self, btn_index: int):
        print('btn_index: ' + str(btn_index))
        # self.place_icon(btn_index, self.playerId)
        self.currentBtnClicked = btn_index

    def change_background(self, image):
        img = pygame.image.load(image)
        self.screen.blit(img, (0, 0))

    def change_turn(self, is_my_turn):
        if is_my_turn:
            text = "Your turn"
        else:
            text = "Enemy turn"
        if self.playerId == 0:
            font_color = self.oFontColor
            image = self.oTurnBgImg
        else:
            font_color = self.xFontColor
            image = self.xTurnBgImg
        self.change_background(image)
        created_text = Text()
        created_text.create_text(self.turn_text_position, text, self.turn_text_font, font_color, self.font_size,
                                 self.screen)

    def place_icon(self, btn_index: int, icon_id: int):
        icon = self.oImg
        if icon_id == 0:
            icon = self.oImg
        elif icon_id == 1:
            icon = self.xImg
        btn_coord = self.btn_positions[btn_index]
        image = pygame.image.load(icon).convert_alpha()

        rect = image.get_rect(center=btn_coord)
        pygame.draw.rect(image, (255, 255, 255), rect, 1)
        self.screen.blit(image, rect)

    def on_game_end(self, is_win):
        if is_win:
            self.change_background(self.win_screen_img)
        else:
            self.change_background(self.loose_screen_img)

    def update_graphics(self, game_field, is_my_turn):
        print(game_field)
        if self.playerId == 0:
            self.change_background(self.oTurnBgImg)
            if is_my_turn:
                self.change_background(self.xTurnBgImg)
        if self.playerId == 1:
            self.change_background(self.xTurnBgImg)
            if is_my_turn:
                self.change_background(self.oTurnBgImg)
        for i in range(len(game_field)):
            cell = game_field[i]
            if cell == 0:
                icon_id = 0
            elif cell == 1:
                icon_id = 1
            else:
                continue
            self.place_icon(i, icon_id)

    def load_game_assets(self, index: int):
        print(self.working_path)
        self.oTurnBgImg = f'{self.working_path}\\assets\\graphics\\o.png'
        self.xTurnBgImg = f'{self.working_path}\\assets\\graphics\\x.png'
        self.defaultBgImage = f'{self.working_path}\\assets\\graphics\\bg.png'
        self.oImg = f'{self.working_path}\\assets\\graphics\\o_player.png'
        self.xImg = f'{self.working_path}\\assets\\graphics\\x_player.png'
        self.win_screen_img = f'{self.working_path}\\assets\\graphics\\win_screen.png'
        self.loose_screen_img = f'{self.working_path}\\assets\\graphics\\loose_screen.png'
        self.turn_text_font = f'{self.working_path}\\asset\\fonts\\GOTHIC.ttf'
        self.oFontColor = (188, 75, 81)
        self.xFontColor = (8, 178, 227)

    def main_loop(self):
        crash = True
        while crash:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    crash = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        crash = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        for b in self.button_list:
                            if b.rect.collidepoint(pos):
                                b.call_back()

            for b in self.button_list:
                b.draw(self.screen)

            pygame.display.update()
            self.clock.tick(60)

    def button_initialization(self):
        counter = 0
        for btn_pos in self.btn_positions:
            new_button = Button(position=btn_pos, size=(160, 160), clr=(0, 0, 0, 0), cngclr=(255, 0, 0),
                                func=self.func,
                                arg=counter)
            self.button_list.append(new_button)
            counter += 1

    def run(self):

        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode(self.screen_size)
        self.change_background(self.defaultBgImage)

        self.button_initialization()
        self.main_loop()

    def __init__(self, index, working_path):
        threading.Thread.__init__(self)
        pygame.init()
        pygame.font.init()

        size = 10
        clr = [255, 0, 0]
        bg = (35, 17, 35)

        self.screen = None
        self.turn_text_font = None
        self.oTurnBgImg = None
        self.oImg = None
        self.xImg = None
        self.oFontColor = None
        self.xFontColor = None
        self.defaultBgImage = None
        self.xTurnBgImg = None
        self.clock = None
        self.loose_screen_img = None
        self.win_screen_img = None
        self.working_path = working_path
        self.btn_positions = [[135.78, 238.38], [299.66, 238.38], [462.53, 238.38],
                              [135.78, 399.69], [299.66, 399.69], [462.53, 399.69],
                              [135.78, 563.44], [299.66, 563.44], [462.53, 563.44],
                              ]
        self.game_field = [3, 3, 3,
                           3, 3, 3,
                           3, 3, 3]
        self.screen_size = (600, 700)
        self.turn_text_position = [301, 76.92]
        self.currentBtnClicked = -1
        self.button_list = []
        self.font_size = 55
        self.playerId = index
        self.load_game_assets(index)




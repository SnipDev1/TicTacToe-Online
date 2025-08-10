import os
import socket
import threading
import time

HOST = "192.168.0.105"  # Standard loopback interface address (localhost)
PORT = 5555  # Port to listen on (non-privileged ports are > 1023)

CLIENTS = []
CLIENTS_CLASSES = []
MAX_PLAYERS = 2
AMOUNT_OF_PLAYERS = 0
SYMBOL_LIST = ['O', 'X', '?']
SYMBOL_STRING = ''


class GameLogic:
    def __init__(self):
        # [0, 1, 2
        # 3, 4, 5
        # 6, 7, 8]
        self.game_field = [3, 3, 3,
                           3, 3, 3,
                           3, 3, 3]
        self.winning_combinations = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 4, 8],
            [2, 4, 6],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8]
        ]
        self.current_player = 0

    def player_move(self, figure, position_index):
        if -1 < position_index < len(self.game_field):
            if self.game_field[position_index] == 3:
                self.game_field[position_index] = figure
            else:
                print("Place has already been played")
                return -2
        else:
            print("Invalid position")
            return -2

    def output_gamefield(self):
        print(self.game_field)

    def next_player(self):
        if self.current_player == 0:
            self.current_player = 1
        else:
            self.current_player = 0

    def is_win(self):
        for combination in self.winning_combinations:
            if self.game_field[combination[0]] == 0 and self.game_field[combination[1]] == 0 and self.game_field[
                combination[2]] == 0:
                return 0
            elif self.game_field[combination[0]] == 1 and self.game_field[combination[1]] == 1 and self.game_field[
                combination[2]] == 1:
                return 1
        return -1

    def test_game(self):
        pass


class PlayerThread(threading.Thread):
    def initial_handshake(self):
        while True:
            data = self.connection.recv(1024).decode()
            print(data)
            if data.startswith('P C'):
                break
        print('FU')
        if self.thread_id >= MAX_PLAYERS:
            print("Too many players")
            self.connection.sendall("TMPC".encode())  # Too many players connected
            self.kick_player()
            return -1
        self.connection.sendall("A".encode())  # allowed


        self.connection.sendall(f"SB:{SYMBOL_STRING}".encode())
        while self.connection.recv(1024).decode() != 'recv':
            continue

        self.connection.sendall("SFT".encode())
        self.file_transmission()

        self.connection.sendall(f"PI {self.thread_id}\n".encode())  # giving player index by thread_id
        while self.connection.recv(1024).decode() != 'recv':
            continue





    def start_game(self):
        self.connection.sendall("GS".encode())

    def kick_player(self):
        global CLIENTS_CLASSES
        self.connection.close()
        CLIENTS_CLASSES.pop(self.thread_id)

    def set_turn(self, table):
        self.connection.sendall(f"YT:{table}".encode())
        while True:
            data = self.connection.recv(1024).decode()
            if data.startswith('MT'):
                turn = int(data.split()[1])
                return turn

    def file_transmission(self):
        while self.connection.recv(1024).decode() != "recv":
            continue

        def create_path(path):
            self.connection.sendall(f"crdir {path}".encode())
            while True:
                if self.connection.recv(1024).decode() == "path_created":
                    break



        def send_file(path_to_folder, filename):
            file_data = ''
            self.connection.sendall(f"ftr {path_to_folder} {filename}\n".encode())
            self.connection.sendall(f"start trans".encode())
            while True:
                if self.connection.recv(1024).decode() == "ready":
                    break
            with open(f'{path_to_folder}\\{filename}', 'rb') as f:
                while True:
                    file_data = f.read(1024)
                    if not file_data:
                        break
                    self.connection.sendall(file_data)

            print(file_data)
            self.connection.sendall('f_end'.encode())
            while True:
                if self.connection.recv(1024).decode() == "file_recv":
                    break

        def stop_trans():
            self.connection.sendall('Stop_transmission'.encode())
            while True:
                if self.connection.recv(1024).decode() == "recv":
                    break

        create_path(f'assets\\fonts')
        create_path(f'assets\\graphics')
        print(f'{self.working_path}\\assets\\graphics')
        print(os.listdir(f'{self.working_path}\\assets\\graphics'))
        for i in os.listdir(f'{self.working_path}\\assets\\graphics'):
            send_file(f'assets\\graphics', i)
        stop_trans()

    def send_table(self, table):
        self.connection.sendall(f"TAT:{table}".encode())

    def match_results(self, is_win: bool):
        if is_win:
            self.connection.sendall("YW".encode())
        else:
            self.connection.sendall("YL".encode())

    def __init__(self, client, thread_id):
        global AMOUNT_OF_PLAYERS
        threading.Thread.__init__(self)
        self.client = client
        self.working_path = os.getcwd()
        self.thread_id = thread_id
        connection, addr = client
        self.connection = connection
        if self.initial_handshake() != -1:
            AMOUNT_OF_PLAYERS += 1


class Server:
    def main_game(self):
        current_game = self.game
        players_dict = {0: CLIENTS_CLASSES[0],
                        1: CLIENTS_CLASSES[1]}
        current_player = 0
        while current_game.is_win() == -1:
            current_game.output_gamefield()

            current_player = current_game.current_player
            player_turn = players_dict[current_player].set_turn(current_game.game_field)
            turn_res = current_game.player_move(current_player, player_turn)
            print(player_turn)
            while turn_res == -2:
                player_turn = players_dict[current_player].set_turn(current_game.game_field)
                turn_res = current_game.player_move(current_player, player_turn)
            players_dict[current_player].send_table(current_game.game_field)
            current_game.next_player()
        current_game.output_gamefield()
        if current_game.is_win() == 1:
            players_dict[1].match_results(True)
            players_dict[0].match_results(False)
        if current_game.is_win() == 0:
            players_dict[1].match_results(False)
            players_dict[0].match_results(True)

    def is_game_need_to_start(self):
        global AMOUNT_OF_PLAYERS
        while True:
            time.sleep(0.5)
            if AMOUNT_OF_PLAYERS == MAX_PLAYERS:
                time.sleep(1)
                for client_thread in CLIENTS_CLASSES:
                    client_thread.start_game()
                break
        self.main_game()

    def split_symbols(self):
        global SYMBOL_LIST, SYMBOL_STRING
        res_string = ""
        for i in range(len(SYMBOL_LIST)):
            if i < len(SYMBOL_LIST) - 1:
                res_string += f'{SYMBOL_LIST[i]};'
            else:
                res_string += f'{SYMBOL_LIST[i]}'
        SYMBOL_STRING = res_string
        print(SYMBOL_STRING)

    def __init__(self):
        self.game = GameLogic()
        self.split_symbols()

        gameThread = threading.Thread(target=self.is_game_need_to_start)
        gameThread.start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            while True:
                client = s.accept()
                CLIENTS.append(client)
                thread_id = len(CLIENTS_CLASSES)
                playerThread = PlayerThread(client, thread_id)
                CLIENTS_CLASSES.append(playerThread)
                playerThread.start()

                # print(CLIENTS_THREADS)


Server = Server()
# game_logic = GameLogic()

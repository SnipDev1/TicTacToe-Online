import os
import socket
import time
import game

HOST = "89.189.177.216"  # The server's hostname or IP address
PORT = 5555  # The port used by the server

SYMBOL_DICT = {}


class ServerCommunication:
    def initial_handshake(self):
        global SYMBOL_DICT
        self.serverSocket.sendall("P C".encode())  # P C
        print(1)
        while True:
            data = self.serverSocket.recv(1024).decode()

            # print(f"Received {data}")
            if data == "TMPC":
                self.disconnect_from_server()
                break
            print('init while')
            if data.startswith("SB"):
                print(2)
                print(data)
                sb = data.split(':')[1]
                sb = sb.split(";")
                print(f"SB is {sb}")
                SYMBOL_DICT = {
                    0: sb[0],
                    1: sb[1],
                    3: sb[2],
                }
                self.serverSocket.sendall("recv".encode())

            if data.startswith("PI"):
                self.player_index = int(data.split()[1])
                print(f"Player index is {self.player_index}")
                self.serverSocket.sendall("recv".encode())
                break

            if data.startswith("PF"):
                self.player_figure = int(data.split()[1])
                print(f"Player figure is {self.player_figure}")

            if data.startswith("SFT"):  # start file transmission
                self.serverSocket.sendall("recv".encode())
                self.file_receiving()

    def waiting_for_game_to_start(self):
        while True:
            data = self.serverSocket.recv(1024).decode()
            if data.startswith("GS"):
                print('GAME STARTED')
                self.main_game()


    def file_receiving(self):
        while True:
            data = self.serverSocket.recv(1024).decode()
            if data.startswith("crdir"):

                path = f'{self.working_path}\\{data.split()[1]}'
                print('crdir ' + path)
                os.makedirs(path, exist_ok=True)
                self.serverSocket.sendall("path_created".encode())
            if data.startswith("ftr"):
                print('ftr')
                file_info = data.split('\n')[0]
                print(file_info)
                file_path = f'{self.working_path}\\{file_info.split()[1]}'
                file_name = file_info.split()[2]
                print(file_path, file_name)


                stop_word = 'f_end'

                is_receiving = True

                self.serverSocket.sendall('ready'.encode())
                with open(f'{file_path}\\{file_name}', 'wb') as f:
                    while True:
                        file_data = self.serverSocket.recv(1024)
                        if file_data.endswith(b"end"):
                            f.write(file_data[:-len(stop_word)])
                            break
                        f.write(file_data)

                self.serverSocket.sendall("file_recv".encode())

            if data.startswith("Stop_transmission"):
                self.serverSocket.sendall("recv".encode())
                break


    def main_game(self):
        def print_formatted_table(table: list):
            for i in range(len(table)):
                table[i] = SYMBOL_DICT[table[i]]
            rows = [table[i:i + 3] for i in range(0, len(table), 3)]
            for row in rows:
                print(" ".join(map(str, row)))

        main_game_class = game.Game(self.player_index, os.getcwd())
        main_game_class.start()

        while True:
            print('asd')
            data = self.serverSocket.recv(1024).decode()
            # if data != "":
            #     print(f"Received {data}")
            if data.startswith("YT"):  # your turn
                os.system('cls')
                print("Table:")
                current_table = data.split(":")[1]
                main_game_class.update_graphics(eval(current_table), True)

                # player_input = input("Position (0-9): ")
                while main_game_class.currentBtnClicked == -1:
                    time.sleep(0.1)
                self.serverSocket.sendall(f"MT {main_game_class.currentBtnClicked}".encode())
                main_game_class.currentBtnClicked = -1
            if data.startswith("TAT"):  # table after turn
                os.system('cls')
                current_table = data.split(":")[1]
                print("Table:")
                main_game_class.update_graphics(eval(current_table), False)

            if data.startswith("YL"):
                print("YOU LOSE")
                main_game_class.on_game_end(False)
                self.disconnect_from_server()
            if data.startswith("YW"):
                print("YOU WIN")
                main_game_class.on_game_end(True)
                self.disconnect_from_server()

    def disconnect_from_server(self):
        self.serverSocket.close()
        exit()

    def __init__(self):
        self.player_index = -1
        self.player_figure = -1
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.connect((HOST, PORT))
        self.working_path = os.getcwd()
        self.PyGame = None
        self.initial_handshake()
        self.waiting_for_game_to_start()


ServerCommunication = ServerCommunication()

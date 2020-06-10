
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import math
import game_module as gm
import sys
from rw_mod import *
import os
class Stream(QObject):
    out = Signal(str)

    def write(self, text):
        self.out.emit(str(text))


class main(QWidget):
    idle_si = Signal()
    allow_turn = Signal(int)

    def __init__(self):
        super().__init__()
        self.init_ui()
        stream = Stream()
        stream.out.connect(self.update_output)
        sys.stdout = stream

    def init_ui(self):
        self.setWindowTitle("2048")
        self.main_layout = QHBoxLayout()
        self.button_layout = QVBoxLayout()
        self.button_layout.setAlignment(Qt.AlignTop)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)

        self.player_box = QComboBox()
        self.player_box.addItem("2 players - one computer")
        self.player_box.addItem("1 player")

        self.online_check = QCheckBox("TCP/IP")
        self.ip_input = QLineEdit('localhost')
        self.port_input = QLineEdit('50001')
        self.ip_input.setFixedSize(200, 20)
        self.port_input.setFixedSize(200, 20)
        self.game = None
        self.online_game = False

        self.ip_input.setEnabled(False)
        self.port_input.setEnabled(False)
        self.online_check.stateChanged.connect(self.enable_online)

        self.new_game_button = QPushButton("New game")
        self.new_game_button.clicked.connect(self.new_game)
        self.new_game_button.setEnabled(False)

        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)

        self.button_layout.addWidget(self.online_check)
        self.button_layout.addWidget(QLabel("IP"))
        self.button_layout.addWidget(self.ip_input)
        self.button_layout.addWidget(QLabel("PORT"))
        self.button_layout.addWidget(self.port_input)
        self.button_layout.addWidget(self.player_box)
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.new_game_button)
        self.button_layout.addWidget(self.quit_button)

        # LAb 14
        self.load_config_button = QPushButton("Load config")
        self.load_config_button.setFixedSize(200, 20)
        self.save_config_button = QPushButton("Save config")
        self.save_config_button.setFixedSize(200, 20)
        self.load_saved_game = QPushButton("Load saved game")
        self.load_saved_game.setFixedSize(200, 20)
        
        self.save_game_filename = QLineEdit('default_name.xml')
        self.save_game_filename.setFixedSize(200, 20)
        self.next_replay_button = QPushButton("Next(replay)")
        self.next_replay_button.setFixedSize(200, 20)
        self.next_replay_button.setEnabled(False)
        self.next_replay_button.clicked.connect(self.next_replay)
        self.load_save_name = QLabel("-")
        self.load_save_name.setFixedSize(200, 20)

        self.jsoner = conf_dealer()
        self.xmler = xml_dealer()

        self.load_config_button.clicked.connect(lambda: self.load_file("json"))
        self.save_config_button.clicked.connect(lambda :self.save_file("json"))
        self.load_saved_game.clicked.connect(lambda: self.load_file("xml"))

        self.button_layout.addWidget(self.load_config_button)
        self.button_layout.addWidget(self.save_config_button)
        self.button_layout.addWidget(QLabel("Filename of saved game"))
        self.button_layout.addWidget(self.save_game_filename)
        self.button_layout.addWidget(QLabel("Load game"))
        self.button_layout.addWidget(self.load_saved_game)
        self.button_layout.addWidget(self.load_save_name)
        self.button_layout.addWidget(self.next_replay_button)
        
        self.pilot_layout = QGridLayout()
        self.up_left = QPushButton('key: Q')
        self.down_right = QPushButton('key: C')
        self.up_right = QPushButton('key: R')
        self.down_left = QPushButton('key: Z')
        self.left = QPushButton('key: A')
        self.right = QPushButton('key: D')
        self.center = QPushButton()
        self.up_left.clicked.connect(lambda: self.click('UL'))
        self.down_right.clicked.connect(lambda: self.click('DR'))
        self.up_right.clicked.connect(lambda: self.click('UR'))
        self.down_left.clicked.connect(lambda: self.click('DL'))
        self.left.clicked.connect(lambda: self.click('L'))
        self.right.clicked.connect(lambda: self.click('R'))
        self.center.setEnabled(False)
        self.button_array = [self.up_right, self.right, self.down_right,
                             self.down_left, self.left, self.up_left, self.center]
        for i in self.button_array:
            i.setFixedSize(QSize(50, 50))
            i.setEnabled(False)

        self.pilot_layout.addWidget(self.up_right, 0, 2)
        self.pilot_layout.addWidget(self.right, 1, 2)
        self.pilot_layout.addWidget(self.down_right, 2, 2)
        self.pilot_layout.addWidget(self.down_left, 2, 0)
        self.pilot_layout.addWidget(self.left, 1, 0)
        self.pilot_layout.addWidget(self.up_left, 0, 0)
        self.pilot_layout.addWidget(self.center, 1, 1)
        self.button_layout.addLayout(self.pilot_layout)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setFixedSize(300, 300)

        self.qscene = QGraphicsScene()
        self.view = QGraphicsView(self.qscene, self)

        self.game_ready = False
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addWidget(self.view)
        self.main_layout.addWidget(self.text_output)
        self.setLayout(self.main_layout)

        self.setFixedSize(1100, 650)
        self.MY_TURN = False

        self.show()
    
    def load_file(self,ext):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self,"Load file", "",f"{ext} files (*.{ext});;All Files (*)", options=options)
        if file_name:
            if(ext == "json"):
                try:
                    data = self.jsoner.load(file_name)
                    self.ip_input.setText(data["ip"])
                    self.port_input.setText(str(data["port"]))
                except:
                    print("błąd")
            if(ext == "xml"):
                try:
                    self.xmler.load_xml(file_name)
                    # self.xmler.show_xml()
                    self.load_save_name.setText(os.path.basename(file_name))
                    self.game = gm.game(self.xmler.get_player_count())
                    self.game.update_seed(self.xmler.get_seed())
                    self.game.board.random_field(self.game.turn)
                    self.game_ready = True
                    self.create_graphics_board()
                    self.start_button.setEnabled(False)
                    self.new_game_button.setEnabled(True)
                    self.next_replay_button.setEnabled(True)
                    self.save_game_filename.setEnabled(False)
                    self.game.xmler.load_xml(file_name)
                    self.game.replay = True
                    self.game.replay_index = 0
                    self.game.max_replay_index = self.game.xmler.get_move_count()
                    self.next_replay_button.setText(f"Next(replay) [{self.game.replay_index}/{self.game.max_replay_index}]")

                except Exception as e:
                    print(e)


            
    def save_file(self,ext):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self,"Load file", "",f"{ext} files (*.{ext});;All Files (*)", options=options)
        if file_name:
            file_name = file_name + f".{ext}"
            if(ext == "json"):
                self.jsoner.update(self.ip_input.text(),int(self.port_input.text()))
                self.jsoner.save(file_name)

    def next_replay(self):
        self.next_replay_button.setText(f"Next(replay) [{self.game.replay_index}/{self.game.max_replay_index}]")
        self.game_step()
        self.game.replay_index += 1
        if(self.game.replay_index >= self.game.max_replay_index):
            self.next_replay_button.setText(f"{self.game.replay_index}/{self.game.max_replay_index}")
            self.next_replay_button.setEnabled(False)


    def enable_online(self):
        checked = self.online_check.isChecked()
        self.player_box.setEnabled(not checked)
        self.ip_input.setEnabled(checked)
        self.port_input.setEnabled(checked)

    @Slot()
    def update_output(self, text):
        self.text_output.insertPlainText(text)
        self.text_output.ensureCursorVisible()

    def game_step(self):
        try:
            self.game.game_one_step()
            self.update()
        except:
            pass

    def keyPressEvent(self, event):
        mapping = {Qt.Key_A: ["z", 1], Qt.Key_D: ["z", -1], Qt.Key_Q: ["x", -1],
                   Qt.Key_C: ["x", 1], Qt.Key_Z: ["y", -1], Qt.Key_E: ["y", 1]}
        try:
            self.game.ax, self.game.dire = mapping.get(event.key())
            if(self.game.end_game == False and self.MY_TURN == True):
                self.game_step()
        except:
            pass

    def click(self, name):
        mapping = {"L": ["z", 1], "R": ["z", -1], "UL": ["x", -1],
                   "DR": ["x", 1], "DL": ["y", -1], "UR": ["y", 1]}
        self.game.ax, self.game.dire = mapping.get(name)
        if(self.game.end_game == False and self.MY_TURN == True):
            self.game_step()

    def new_game(self):
        self.start_button.setEnabled(True)
        self.new_game_button.setEnabled(False)
        self.save_game_filename.setEnabled(True)
        self.load_saved_game.setEnabled(True)
        self.online_check.setChecked(False)
        self.next_replay_button.setEnabled(False)

    def start(self):
        self.save_game_filename.setEnabled(False)
        self.load_saved_game.setEnabled(False)
        self.next_replay_button.setEnabled(False)
        if(self.online_check.isChecked() == False):
            self.MY_TURN = True
            for i in self.button_array:
                i.setEnabled(True)
            count = 1
            if self.player_box.currentIndex() == 0:
                count = 2
            self.game = gm.game(count)
            self.game.board.random_field(self.game.turn)
            self.game_ready = True
            self.create_graphics_board()
            self.start_button.setEnabled(False)
            self.new_game_button.setEnabled(True)
        else:
            print("creating online game")
            ip = str(self.ip_input.text())
            port = int(self.port_input.text())
            self.online_game = True
            self.game = gm.game(2)
            self.game.online = True
            self.game.host_ip = ip
            self.game.host_port = port
            self.game.idle_signal = self.idle_si
            self.allow_turn.connect(self.enable_turn)
            self.game.connect_to_server(self.allow_turn)
            self.game_ready = True
            self.create_graphics_board()
            self.start_button.setEnabled(False)
            self.new_game_button.setEnabled(True)
        self.game.xml_filename = self.save_game_filename.text()
        

    def enable_turn(self, mode):
        if(mode == 0):
            for i in self.button_array:
                i.setEnabled(False)
                self.MY_TURN = False
                self.kolej_text.setText("KOLEJ PRZECIWNIKA")

        if(mode == 1):
            for i in self.button_array:
                i.setEnabled(True)
                self.MY_TURN = True
                self.kolej_text.setText("TWOJA KOLEJ")
        if(mode == 2):
            for i in self.button_array:
                i.setEnabled(False)
                self.MY_TURN = False
                self.kolej_text.setText("Przeciwnik opuscil gre")


        self.update()

    def create_graphics_board(self):

        self.kolej_text = QGraphicsSimpleTextItem("")
        self.kolej_text.setPos(300, 20)
        self.qscene.addItem(self.kolej_text)

        brush = QBrush(QColor(0, 0, 0))
        pen = QPen(QColor(0, 0, 0))
        cur_row = sorted(self.game.board.board, key=lambda x: x.z)
        old_z = 10
        h = w = 0
        size = 25
        hex_w = math.sqrt(3) * size
        hex_h = 2 * size
        for c in cur_row:
            w += 1
            if(old_z - c.z != 0):
                w = 0
                h += 1
                if(c.z <= 0):
                    w += (self.game.board.size - 1 + c.x)/2
                else:
                    w += (self.game.board.size-1-c.y)/2

            px, py = hex_w*w + 200, (3/4)*hex_h*h + 100
            angle_deg = [60*x - 30 for x in range(6)]
            angle_rad = [math.pi/180 * ang for ang in angle_deg]
            point = [(px + size * math.cos(angl), py + size * math.sin(angl))
                     for angl in angle_rad]
            polygon = QPolygonF()
            for p in point:
                ps = QPointF(p[0], p[1])
                polygon.append(ps)
            hexx = QGraphicsPolygonItem(polygon)
            hexx.setPen(pen)
            hexx.setBrush(brush)
            number = QGraphicsTextItem(str(c.v))
            number.setPos(px-3*len(str(c.v)), py-15)
            self.qscene.addItem(hexx)
            self.qscene.addItem(number)
            old_z = c.z
        # print(self.qscene.items())

    def paintEvent(self, event):
        size = 25
        hex_w = math.sqrt(3) * size
        old_z = 10
        hex_h = 2 * size
        old_z = 10
        h = w = 0
        if(self.game_ready == True):
            colors = [QColor(250, 100, 120), QColor(
                100, 250, 100), QColor(250, 250, 250)]
            if(self.online_game == False):
                self.kolej_text.setText(f"Turn: player:{self.game.turn}")
            self.kolej_text.setPen(QPen(colors[self.game.turn], 1))
            cur_row = sorted(self.game.board.board, key=lambda x: x.z)
            for index, c in enumerate(cur_row):
                w += 1
                if(old_z - c.z != 0):
                    w = 0
                    h += 1
                    if(c.z <= 0):
                        w += (self.game.board.size - 1 + c.x)/2
                    else:
                        w += (self.game.board.size-1-c.y)/2
                px, py = hex_w*w + 200, (3/4)*hex_h*h + 100
                ind = len(cur_row) - index - 1
                hexx = self.qscene.items()[ind*2 + 1]
                number = self.qscene.items()[ind*2]
                brush = QBrush(colors[c.id])
                hexx.setBrush(brush)
                number.setPlainText(str(c.v))
                old_z = c.z


app = QApplication([])
ex = main()
ex.show()
app.exec_()
sys.exit()

import random
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QLineEdit, QFontDialog, QToolButton,
    QPushButton, QWidget, QHBoxLayout, QVBoxLayout,
    QComboBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QIntValidator, QPixmap, QColor
from supabase import create_client

url = "http://localhost:8000"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJzZXJ2aWNlX3JvbGUiLAogICAgImlzcyI6ICJzdXBhYmFzZS1kZW1vIiwKICAgICJpYXQiOiAxNjQxNzY5MjAwLAogICAgImV4cCI6IDE3OTk1MzU2MDAKfQ.DaYlNEoUrrEn2Ig7tqibS-PHK5vgusbcbo7X36XVt4Q"

supabase = create_client(url, key)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(1500, 750)
        self.mainscreen()
        self.username = 'anon'
        self.make_start_params()

    def create_elem_for_mainscreen(self):
        self.active_elements = {}
        self.active_elements['play_btn'] = QPushButton('Play')
        self.active_elements['hst_btn'] = QPushButton('History')
        self.active_elements['font_btn'] = QPushButton('Font')
        self.active_elements['welcome_lbl'] = QLabel('Welcome, ')
        self.active_elements['enter_lbl'] = QLabel('Enter name: ')
        self.active_elements['name_edit'] = QLineEdit()
        self.active_elements['color_btn'] = QToolButton()

        moon_icon = QIcon("sun.png")
        self.active_elements.get('color_btn').setIcon(moon_icon)

        self.active_elements.get('play_btn').clicked.connect(self.go_to_playview)
        self.active_elements.get('name_edit').textChanged.connect(self.name_edit_handler)
        self.active_elements.get('font_btn').clicked.connect(self.font_btn_clicked)
        self.active_elements.get('color_btn').clicked.connect(self.color_btn_clicked)
        self.active_elements.get('hst_btn').clicked.connect(self.go_to_history)

    def create_elem_for_playview(self):
        self.active_elements = {}
        self.game_status_label_text = 'game settings: number from {0} to {1}. Game type: {2}. Timer {3}'

        self.active_elements['go_back_btn'] = QToolButton()
        self.active_elements['start_btn'] = QPushButton('Start')
        self.active_elements['number_lbl'] = QLabel(f'{self.username}, enter number range: ')
        self.active_elements['min_number'] = QLineEdit()
        self.active_elements['max_number'] = QLineEdit()
        self.active_elements['game_type'] = QComboBox()
        self.active_elements['game_status_lbl'] = QLabel(self.game_status_label_text.format(self.now_game_settings['start_num'], self.now_game_settings['end_num'], self.now_game_settings['game_type'], self.now_game_settings['time']))
        self.active_elements['game_type_lbl'] = QLabel('Chose game type: ')
        self.active_elements['time_lbl'] = QLabel('Chose game duration: ')
        self.active_elements['time'] = QLineEdit()

        self.active_elements.get('go_back_btn').setIcon(QIcon("back.png"))

        self.active_elements['game_type'].addItem('Substract')
        self.active_elements['game_type'].addItem('Add')
        self.active_elements['game_type'].setCurrentIndex(1)
        self.active_elements['game_type'].currentIndexChanged.connect(self.game_type_change)

        self.active_elements.get('min_number').setValidator(QIntValidator())
        self.active_elements.get('max_number').setValidator(QIntValidator())
        self.active_elements.get('time').setValidator(QIntValidator())

        self.active_elements.get('go_back_btn').clicked.connect(self.go_to_mainscreen)
        self.active_elements.get('min_number').textChanged.connect(self.change_min_range)
        self.active_elements.get('max_number').textChanged.connect(self.change_max_range)
        self.active_elements.get('start_btn').clicked.connect(self.go_to_play)
        self.active_elements.get('time').textChanged.connect(self.change_time)

    def create_elem_for_play(self):
        self.now_time = self.now_game_settings['time']

        self.active_elements['go_back_btn'] = QToolButton()
        self.active_elements['game_status_lbl'] = QLabel(
            self.game_status_label_text.format(self.now_game_settings['start_num'], self.now_game_settings['end_num'],
                                               self.now_game_settings['game_type'], self.now_game_settings['time']))
        self.active_elements['timer'] = QTimer()
        self.active_elements['timer_lbl'] = QLabel(f'You have {self.now_time} seconds')
        self.active_elements['eq_lbl'] = QLabel(self.gen_eq())
        self.active_elements['eq_ans'] = QLineEdit()
        self.active_elements['finish_btn'] = QPushButton('Finish')

        self.active_elements.get('eq_ans').setValidator(QIntValidator())

        self.active_elements['timer'].setInterval(1000)
        self.active_elements['timer'].timeout.connect(self.update_timer)
        self.active_elements['timer'].start()

        self.active_elements.get('go_back_btn').setIcon(QIcon("back.png"))
        self.active_elements.get('finish_btn').clicked.connect(self.go_to_endplay)
        self.active_elements.get('go_back_btn').clicked.connect(self.go_to_playview)

    def create_elem_for_endplay(self):
        self.active_elements['im_lbl'] = QLabel()
        self.active_elements['go_to_main'] = QPushButton('Go to main screen')
        self.active_elements['play_one_more'] = QPushButton('Play one more game')
        data = {
            'username': self.username,
            'time': self.now_game_settings['time'],
            'start': self.now_game_settings['start_num'],
            'stop': self.now_game_settings['end_num'],
            'game_type': self.now_game_settings['game_type'],
            'eq': self.now_eq,
            'correct_answer': self.now_res,
            'user_answer': self.user_answer
            }
        if self.now_res == self.user_answer:
            pixmap = QPixmap("good.jpg")
            self.active_elements['result_lbl'] = QLabel('Вы ответили верно')
            data['is_correct'] = True
            _, _ = supabase.table('entry').insert(data).execute()
        else:
            pixmap = QPixmap("bad.jpeg")
            self.active_elements['result_lbl'] = QLabel(f'Вы ответили неверно, правильный ответ был {self.now_res}')
            data['is_correct'] = False
            _, _ = supabase.table('entry').insert(data).execute()
        self.active_elements['im_lbl'].setPixmap(pixmap)
        self.active_elements.get('go_to_main').clicked.connect(self.go_to_mainscreen)
        self.active_elements.get('play_one_more').clicked.connect(self.go_to_play)


    def history_screen(self):
        self.setWindowTitle('History')
        self.active_elements['go_back_btn'] = QToolButton()
        self.active_elements.get('go_back_btn').setIcon(QIcon("back.png"))
        self.active_elements.get('go_back_btn').clicked.connect(self.go_to_mainscreen)
        self.active_elements['table'] = QTableWidget()

        response = supabase.table('entry').select('username', 'time', 'start', 'stop', 'game_type', 'eq', 'correct_answer', 'user_answer', 'is_correct').order('id', desc=True).execute()
        data = response.data
        rows = len(data) + 1
        columns = 8
        self.active_elements['table'].setRowCount(rows)
        self.active_elements['table'].setColumnCount(columns)

        column_names = ['username', 'duration', 'start', 'stop', 'game_type', 'eq', 'correct_answer', 'user_answer']

        for i in range(rows):
            for j in range(columns):
                if i == 0:
                    self.active_elements['table'].setItem(0, j, QTableWidgetItem(f'{column_names[j]}'))
                else:
                    self.active_elements['table'].setItem(i, j, QTableWidgetItem(f'{data[i - 1].get(column_names[j])}'))
                    item = self.active_elements['table'].item(i, j)
                    if data[i - 1].get('is_correct'):
                        item.setBackground(QColor(0, 220, 0))
                    else:
                        item.setBackground(QColor(220, 0, 0))

        for column in range(self.active_elements['table'].columnCount()):
            self.active_elements['table'].setColumnWidth(column, 150)

        vert_layout = QVBoxLayout()
        vert_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        vert_layout.addWidget(self.active_elements['go_back_btn'])
        vert_layout.addWidget(self.active_elements['table'])

        self.container = QWidget()
        self.container.setLayout(vert_layout)
        self.setCentralWidget(self.container)

    def playscreen(self):
        self.setWindowTitle("Play!!!")
        self.create_elem_for_play()

        vert_layout = QVBoxLayout()
        vert_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        hor_layout = QHBoxLayout()
        hor_layout.addWidget(self.active_elements.get('go_back_btn'))
        hor_layout.addStretch(1)
        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('game_status_lbl'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('timer_lbl'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)


        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('eq_lbl'))
        hor_layout.addWidget(self.active_elements.get('eq_ans'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('finish_btn'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        self.container = QWidget()
        self.container.setLayout(vert_layout)
        self.setCentralWidget(self.container)


    def playview(self):
        self.setWindowTitle("Game settings")
        self.now_game_settings = {
            'game_type': 'add',
            'start_num': 0,
            'end_num': 10,
            'time': 10
        }
        self.create_elem_for_playview()

        vert_layout = QVBoxLayout()
        vert_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        hor_layout = QHBoxLayout()
        hor_layout.addWidget(self.active_elements.get('go_back_btn'))
        hor_layout.addStretch(1)
        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('game_status_lbl'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('number_lbl'))
        hor_layout.addWidget(self.active_elements.get('min_number'))
        hor_layout.addWidget(self.active_elements.get('max_number'))
        hor_layout.addWidget(self.active_elements.get('game_type_lbl'))
        hor_layout.addWidget(self.active_elements.get('game_type'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('time_lbl'))
        hor_layout.addWidget(self.active_elements.get('time'))
        hor_layout.addStretch(1)
        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('start_btn'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        self.container = QWidget()
        self.container.setLayout(vert_layout)
        self.setCentralWidget(self.container)

    def mainscreen(self):
        self.setWindowTitle("Game menu")
        self.create_elem_for_mainscreen()

        vert_layout = QVBoxLayout()
        vert_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('welcome_lbl'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('enter_lbl'))
        hor_layout.addWidget(self.active_elements.get('name_edit'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('font_btn'))
        hor_layout.addWidget(self.active_elements.get('play_btn'))
        hor_layout.addWidget(self.active_elements.get('hst_btn'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('color_btn'))

        vert_layout.addLayout(hor_layout)


        self.container = QWidget()
        self.container.setLayout(vert_layout)
        self.setCentralWidget(self.container)

    def endplay_screen(self):
        self.setWindowTitle("Game results")
        self.create_elem_for_endplay()

        vert_layout = QVBoxLayout()
        vert_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('result_lbl'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('im_lbl'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        hor_layout = QHBoxLayout()
        hor_layout.addStretch(1)
        hor_layout.addWidget(self.active_elements.get('go_to_main'))
        hor_layout.addWidget(self.active_elements.get('play_one_more'))
        hor_layout.addStretch(1)

        vert_layout.addLayout(hor_layout)
        vert_layout.addStretch(1)

        self.container = QWidget()
        self.container.setLayout(vert_layout)
        self.setCentralWidget(self.container)

    def go_to_endplay(self):
        self.centralWidget().deleteLater()
        try:
            self.user_answer = int(self.active_elements['eq_ans'].text())
            self.now_eq = self.active_elements.get('eq_lbl').text()
        except:
            self.user_answer = 0
        self.active_elements = {}
        self.endplay_screen()

    def go_to_mainscreen(self):
        self.centralWidget().deleteLater()
        self.active_elements = {}
        self.mainscreen()

    def go_to_playview(self):
        self.centralWidget().deleteLater()
        self.playview()

    def go_to_play(self):
        if self.now_game_settings['start_num'] > self.now_game_settings['end_num']:
            self.now_game_settings['start_num'], self.now_game_settings['end_num'] = self.now_game_settings['end_num'], self.now_game_settings['start_num']
        self.centralWidget().deleteLater()
        self.active_elements = {}
        self.playscreen()

    def go_to_history(self):
        self.centralWidget().deleteLater()
        self.active_elements = {}
        self.history_screen()

    def gen_eq(self):
        first_num = random.randint(self.now_game_settings['start_num'], self.now_game_settings['end_num'])
        second_num = random.randint(self.now_game_settings['start_num'], self.now_game_settings['end_num'])
        if self.now_game_settings['game_type'].lower() == 'add':
            self.now_res = first_num + second_num
            return f'{first_num} + {second_num}'
        self.now_res = first_num - second_num
        return f'{first_num} - {second_num}'

    def name_edit_handler(self):
        self.username = self.active_elements.get('name_edit').text()
        self.active_elements.get('welcome_lbl').setText('Welcome, ' + self.username)

    def update_timer(self):
        if self.now_time == 0:
            self.go_to_endplay()
        else:
            self.now_time -= 1
            self.active_elements.get('timer_lbl').setText(f'You have {self.now_time} seconds')

    def change_time(self):
        try:
            self.now_game_settings['time'] = int(self.active_elements.get('time').text())
        except ValueError:
            self.now_game_settings['time'] = 10
        if self.now_game_settings['time'] <= 0:
            self.now_game_settings['time'] = 10
        self.rewrite_game_status_lbl()

    def rewrite_game_status_lbl(self):
        self.active_elements['game_status_lbl'].setText(self.game_status_label_text.format(self.now_game_settings['start_num'], self.now_game_settings['end_num'], self.now_game_settings['game_type'], self.now_game_settings['time']))

    def change_min_range(self):
        try:
            self.now_game_settings['start_num'] = int(self.active_elements.get('min_number').text())
        except ValueError:
            self.now_game_settings['start_num'] = 0
        self.rewrite_game_status_lbl()

    def change_max_range(self):
        try:
            self.now_game_settings['end_num'] = int(self.active_elements.get('max_number').text())
        except ValueError:
            self.now_game_settings['end_num'] = 0
        self.rewrite_game_status_lbl()

    def game_type_change(self):
        if self.active_elements['game_type'].currentText() == 'Add':
            self.now_game_settings['game_type'] = 'add'
        else:
            self.now_game_settings['game_type'] = 'substact'
        self.rewrite_game_status_lbl()

    def make_start_params(self):
        self.font_size = '14'
        self.font_family = 'Ubuntu'
        self.font_weight = '900'
        self.style_sheet = "background-color: #{0}; color: {1}; font: {2}pt '{3}', {4}; padding: 12px; margin: 5px"
        self.color_black = True
        self.make_black()
        self.setStyleSheet(self.style_sheet.format(self.background_color, self.font_color, self.font_size, self.font_family, self.font_weight))

    def make_black(self):
        self.background_color = '333333'
        self.font_color = 'white'

    def make_white(self):
        self.background_color = 'F2F2F2'
        self.font_color = 'black'

    def font_btn_clicked(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.font_size = font.pointSize()
            self.font_family = font.family()
            self.font_weight = font.weight()
            self.setStyleSheet(
                self.style_sheet.format(self.background_color, self.font_color, self.font_size, self.font_family,
                                        self.font_weight))

    def color_btn_clicked(self):
        if self.color_black:
            icon = QIcon("moon.png")
            self.make_white()
        else:
            icon = QIcon("sun.png")
            self.make_black()
        self.setStyleSheet(self.style_sheet.format(self.background_color, self.font_color, self.font_size, self.font_family, self.font_weight))
        self.color_black = not self.color_black
        self.active_elements.get('color_btn').setIcon(icon)


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
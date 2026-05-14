import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QScrollArea, QLabel
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QTextOption
from .Agent import Agent
from .CastomErr import *
from QMarkdownWidget import QMLabel


class ChatMessage(QWidget):
    
    def __init__(self, text, is_user=True):
        super().__init__()
        self.is_user = is_user
        self.init_ui(text)

    def init_ui(self, text):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)

        message_view = QMLabel(text)
        message_view.setTextInteractionFlags(Qt.TextSelectableByMouse)

        message_label = QLabel(text)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Arial", 10))
        

        if self.is_user:
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #B22222;
                    color: 	#FFFFFF;
                    padding: 8px 12px;
                    border-radius: 10px;
                    max-width: 500%;
                }
            """)
            layout.addStretch()
            layout.addWidget(message_label)
            
        else:
            message_view.setStyleSheet("""
                QMLabel {
                    background-color: #2E2E2E;
                    color: #FFFFFF;
                    padding: 8px 12px;
                    border-radius: 10px;
                    max-width: 500px;
                }
            """)
            layout.addWidget(message_view)
            layout.addStretch()

        self.setLayout(layout)

class GenerateAnswer(QThread):

    answer_ready = Signal(str)

    def __init__(self, prompt, agent):
        super().__init__()
        self.prompt = prompt
        self.agent = agent
    
    def run(self):
        agent = Agent()
        answer = self.get_response(self.prompt)
        self.answer_ready.emit(answer)

    def get_response(self, prompt):
        response = self.agent.run(prompt)
        return response
    

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bot_worker = None
        self.agent = Agent()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SciAssist")
        self.setGeometry(100, 100, 700, 600)
        

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet('''
                                     background-color: #141414;''')

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ========== ОБЛАСТЬ ЧАТА ==========
        # Используем QScrollArea для прокручивания сообщений
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid #CCCCCC; }")

        # Контейнер для сообщений
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setSpacing(5)
        self.chat_layout.setContentsMargins(5, 5, 5, 5)
        self.chat_layout.addStretch()  # Добавляем растягиваемое пространство в конец

        self.chat_container.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.chat_container)

        main_layout.addWidget(self.scroll_area, 1)  # Даём максимум пространства чату

        # ========== ОБЛАСТЬ ВВОДА ==========
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)

        # Поле ввода текста
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Введите ваше сообщение...")
        self.input_field.setMaximumHeight(60)
        self.input_field.setFont(QFont("Arial", 10))
        self.input_field.setStyleSheet('''
                                       QTextEdit{color: #FFFFFF}
                                       QTextEdit:focus{
                                       border: 2px solid #C72C2C;
                                       color: #FFFFFF;
                                       }
                                       ''')

        # Кнопка отправки
        self.send_button = QPushButton("Отправить")
        self.send_button.setMaximumWidth(100)
        self.send_button.setMaximumHeight(60)
        self.send_button.setStyleSheet('''
                                       QPushButton{
                                       background-color: #C72C2C;
                                       color: #FFFFFF;}
                                       QPushButton:pressed{
                                       background-color: #4B0000;
                                       color: #FFFFFF;}
                                       QPushButton:disabled{
                                       background-color: #302222;
                                       color: #999999;}
                                       ''' )
        self.send_button.clicked.connect(self.send_user_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

        central_widget.setLayout(main_layout)

    def send_user_message(self):
        """Отправить сообщение"""
        text = self.input_field.toPlainText().strip()

        if not text:
            return

        # Добавляем сообщение пользователя
        self.add_message(text, is_user=True)

        # Очищаем поле ввода
        self.input_field.clear()
        self.input_field.setFocus()

        self.send_button.setEnabled(False)
        self.send_button.setText('Думаю')    

        self.bot_worker = GenerateAnswer(text, self.agent)
        self.bot_worker.answer_ready.connect(self.send_bot_message)
        self.bot_worker.start()

    def send_bot_message(self, response):
        self.add_message(response, is_user=False)

        # Включаем кнопку обратно
        self.send_button.setEnabled(True)
        self.send_button.setText("Отправить")

    def add_message(self, text, is_user=True):
        """Добавить сообщение в чат"""
        # Удаляем растягивающийся элемент перед добавлением нового сообщения
        if self.chat_layout.count() > 0:
            self.chat_layout.takeAt(self.chat_layout.count() - 1)

        # Добавляем новое сообщение
        message = ChatMessage(text, is_user)
        self.chat_layout.addWidget(message)

        # Добавляем растяжение в конец
        self.chat_layout.addStretch()

        # Прокручиваем вниз к последнему сообщению
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )


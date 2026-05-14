from src.AgentState import AgentState
from PySide6.QtWidgets import QApplication
from src.ui import ChatWindow
import sys

def main():
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

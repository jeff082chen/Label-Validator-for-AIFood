# Author: Jeffrey Chen
# Last Modified: 08/02/2023
import os, json, atexit, time, threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap

div_size = 224
pad = 3

# Root window
class Root(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Label Validator")
        self.setFixedSize(div_size * 2 + pad * 2, int(div_size * 1.25) + pad * 3)  # 454 x 283
        self.setStyleSheet("background-color: white")

# Backend logic
class ControlSystem:
    def __init__(self):
        # image paths
        self.current_image_index = 0
        self.images = [f"./app/images/image_{i}.png" for i in range(1, 31)]

        # Validators
        self.validators = ["Jeffrey Chen", "Nancy Li", "Zoe Wang", "Vivian Wu"]
        self.current_validator_index = 0

        # Validate Results
        if not os.path.exists("./app/validate_results.json"):
            with open("./app/validate_results.json", "w") as f:
                json.dump({}, f, indent = 4, ensure_ascii = False)
        with open("./app/validate_results.json", "r") as f:
            self.validate_results = json.load(f)

        # prevent data loss
        atexit.register(self.exit)
        self.heartbeat_file = "./app/.heartbeat.json"

        # Check for unclean shutdown
        if self.was_unclean_shutdown():
            self.recover_from_unclean_shutdown()

        # Start heartbeat in a separate thread
        threading.Thread(target = self.start_heartbeat, daemon = True).start()

    def start_heartbeat(self):
        while True:
            time.sleep(60)  # update heartbeat file every minute
            with open(self.heartbeat_file, 'w') as file:
                json.dump(self.validate_results, file, indent = 4, ensure_ascii = False)

    def was_unclean_shutdown(self):
        return os.path.exists(self.heartbeat_file)

    def recover_from_unclean_shutdown(self):
        with open(self.heartbeat_file, 'r') as file:
            self.validate_results = json.load(file)

    def current_validator(self):
        return self.validators[self.current_validator_index]
    
    def current_image(self):
        return self.images[self.current_image_index]
        
    def next_image(self):
        self.current_image_index += 1
        if self.current_image_index >= len(self.images):
            self.current_image_index = 0
        return self.images[self.current_image_index]
    
    def previous_image(self):
        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = len(self.images) - 1
        return self.images[self.current_image_index]
    
    def record_result(self, result):
        if self.current_image() not in self.validate_results:
            self.validate_results[self.current_image()] = {}
        self.validate_results[self.current_image()][self.current_validator()] = result
    
    def exit(self):
        with open("./app/validate_results.json", "w") as f:
            json.dump(self.validate_results, f, indent = 4, ensure_ascii = False)
        if os.path.exists(self.heartbeat_file):
            os.remove(self.heartbeat_file)
        exit()

# Main application
class App:
    def __init__(self, root: Root):
        self.root = root
        self.control = ControlSystem()

        # rewrite closeEvent
        self.root.closeEvent = self.exit

        # create frames
        self.root_div1 = QWidget(self.root)
        self.root_div1.setStyleSheet("background-color: #f5f5dc")
        self.root_div1.setFixedSize(div_size, div_size) # 224 x 224

        self.root_div2 = QWidget(self.root)
        self.root_div2.setStyleSheet("background-color: #f5f5dc")
        self.root_div2.setFixedSize(div_size - pad, int(div_size * 0.25)) # 224 x 56

        self.root_div3 = QWidget(self.root)
        self.root_div3.setStyleSheet("background-color: #f5f5dc")
        self.root_div3.setFixedSize(div_size - pad, int(div_size * 0.75) - pad) # 224 x 168

        self.root_div4 = QWidget(self.root)
        self.root_div4.setStyleSheet("background-color: #f5f5dc")
        self.root_div4.setFixedSize(div_size * 2, int(div_size * 0.25)) # 448 x 56

        # position frames
        self.root_div1.move(pad, pad)
        self.root_div2.move(div_size + pad * 2, pad)
        self.root_div3.move(div_size + pad * 2, int(div_size * 0.25) + pad * 2)
        self.root_div4.move(pad, div_size + pad * 2)

        # create items in root_div1
        # image
        self.label = QLabel(self.root_div1)
        self.label.setPixmap(QPixmap(self.control.current_image()))
        self.label.setScaledContents(True)
        self.label.resize(div_size, div_size)

        # position items in root_div1
        self.label.move(0, 0)

        # create items in root_div2
        # validator
        self.validator_label = QLabel(self.root_div2)
        self.validator_label.setText(f"Validator: {self.control.current_validator()}")
        self.validator_label.setStyleSheet("background-color: #f5f5dc; color: black;")

        # dropdown menu
        self.validator_dropdown = QtWidgets.QComboBox(self.root_div2)
        self.validator_dropdown.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding-left: 10px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(./app/system_img/dropdown_arrow.png);
                width: 12px;
                height: 12px;
                margin-right: 15px;
            }
            QComboBox:on {
                border: 2px solid #f1e1ff;
            }
            QComboBox::item:selected {
                color: #b177ff;
            }
            """
        )
        self.validator_dropdown.setFixedSize(int(div_size * 0.75), int(div_size * 0.09375)) # 168 x 21
        self.validator_dropdown.addItems(self.control.validators)
        self.validator_dropdown.currentIndexChanged.connect(self.on_validator_changed)

        # position items in root_div2
        self.validator_label.move(pad, pad)
        self.validator_dropdown.move(pad, int(div_size * 0.09375) + pad * 2)

        # create items in root_div4
        # buttons
        self.next_image_button = QtWidgets.QPushButton(self.root_div4)
        self.next_image_button.setText("Next Image")
        self.next_image_button.setStyleSheet("background-color: white")
        self.next_image_button.setFixedSize(int(div_size * 0.5), int(div_size * 0.09375)) # 112 x 21
        self.next_image_button.clicked.connect(self.next_image)

        self.previous_image_button = QtWidgets.QPushButton(self.root_div4)
        self.previous_image_button.setText("Previous Image")
        self.previous_image_button.setStyleSheet("background-color: white")
        self.previous_image_button.setFixedSize(int(div_size * 0.5), int(div_size * 0.09375)) # 112 x 21
        self.previous_image_button.clicked.connect(self.previous_image)

        self.accept_button = QtWidgets.QPushButton(self.root_div4)
        self.accept_button.setText("Accept")
        self.accept_button.setStyleSheet("background-color: white")
        self.accept_button.setFixedSize(int(div_size * 0.5), int(div_size * 0.09375)) # 112 x 21
        self.accept_button.clicked.connect(lambda: self.record_result("accept"))

        self.incorrect_button = QtWidgets.QPushButton(self.root_div4)
        self.incorrect_button.setText("Incorrect")
        self.incorrect_button.setStyleSheet("background-color: white")
        self.incorrect_button.setFixedSize(int(div_size * 0.5), int(div_size * 0.09375)) # 112 x 21
        self.incorrect_button.clicked.connect(lambda: self.record_result("incorrect"))

        self.reject_button = QtWidgets.QPushButton(self.root_div4)
        self.reject_button.setText("Reject")
        self.reject_button.setStyleSheet("background-color: white")
        self.reject_button.setFixedSize(int(div_size * 0.5), int(div_size * 0.09375)) # 112 x 21
        self.reject_button.clicked.connect(lambda: self.record_result("reject"))

        # position items in root_div4
        self.next_image_button.move(pad, pad)
        self.previous_image_button.move(int(div_size * 0.5) + pad * 2, pad)
        self.accept_button.move(pad, int(div_size * 0.09375) + pad * 2)
        self.incorrect_button.move(int(div_size * 0.5) + pad * 2, int(div_size * 0.09375) + pad * 2)
        self.reject_button.move(int(div_size * 0.5) * 2 + pad * 3, int(div_size * 0.09375) + pad * 2)

    def on_validator_changed(self, index):
        self.control.current_validator_index = index
        self.validator_label.setText(f"Validator: {self.control.current_validator()}")

    def next_image(self):
        new_image_path = self.control.next_image()
        self.label.setPixmap(QPixmap(new_image_path))

    def previous_image(self):
        new_image_path = self.control.previous_image()
        self.label.setPixmap(QPixmap(new_image_path))

    def record_result(self, result):
        self.control.record_result(result)

    def exit(self, event):
        self.control.exit()
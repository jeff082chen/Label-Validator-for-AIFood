# Author: Jeffrey Chen
# Last Modified: 08/23/2023
import os, json, atexit, time, threading, re, random
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal

div_size = 224
pad = 3

background_color_dark = "rgb(73, 131, 154)"
background_color_light = "rgb(232, 243, 243)"
text_color = "rgb(124, 166, 215)"
selected_border_color = "rgb(59, 47, 133)"
inactivated_color = "gray"

button_style_active = f"""
    QPushButton {{
        background-color: {background_color_light};
        color: {text_color};
        border: 1px solid {text_color};
    }}
    QPushButton:hover {{
        background-color: {text_color};
        color: {background_color_light};
    }}
"""

button_style_inactive = f"""
    QPushButton {{
        background-color: {background_color_light};
        color: {inactivated_color};
        border: 1px solid {inactivated_color};
    }}
"""

img_style_selected = f"border: 5px solid {selected_border_color};"
img_style_unselected = f"border: 0px;"

class ClickableLabel(QLabel):
    # Define a new signal called 'clicked'
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # Emit the 'clicked' signal when the label is pressed
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

# Root window
class Root(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Label Validator")
        self.setFixedSize(int(div_size * 6) + pad * 5, div_size * 4 + int(div_size * 0.09375) + pad * 8) # 1344 x 672
        self.setStyleSheet(f"background-color: {background_color_dark};")

# Backend logic
class ControlSystem:

    catagory2food = {
        'A01': '米食',
        'A02': '麵食',
        'B01': '豬肉',
        'B02': '雞肉',
        'B03': '牛肉',
        'B04': '羊肉',
        'B05': '鴨肉',
        'B06': '鵝肉',
        'C01': '水果類',
        'C02': '葉菜類',
        'C03': '瓜果類',
        'C04': '花菜花瓣類',
        'C05': '根莖類',
        'C06': '種子核果類',
        'C07': '海菜菇蕈類',
        'C08': '蒟蒻',
        'D01': '魚肉',
        'D02': '貝類',
        'D03': '甲殼類',
        'D04': '頭足軟體',
        'E01': '蛋',
        'E02': '豆腐',
        'E03': '豆乾豆包',
        'F01': '奶類'
    }

    def __init__(self):
        # image paths
        self.images_folder = os.path.join(os.path.dirname(__file__), "images")
        # all images in the folder that fit the name format
        # format: <food labels>_<image id>_<dataset id>.jpg
        # food labels: Capital letter + 2 digit number, if multiple, no sperator
        # image id: a sequence of digits
        # dataset id: single digit
        regex = re.compile(r"([A-Z]\d{2})+_\d+_\d\.jpg")
        self.images = [os.path.join(self.images_folder, image) for image in os.listdir(self.images_folder) if regex.match(image)]

        # Validators
        self.validators = ["Jeffrey Chen", "Nancy Li", "Zoe Wang", "Vivian Wu"]
        self.current_validator_index = 0

        # placeholder image
        self.placeholder_image = os.path.join(os.path.dirname(__file__), "system_img", "placeholder.png")

        # selected image
        self.selected_image_div = None

        # Validate Results
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "validate_results.json")):
            with open(os.path.join(os.path.dirname(__file__), "validate_results.json"), "w") as f:
                json.dump({}, f, indent = 4, ensure_ascii = False)
        with open(os.path.join(os.path.dirname(__file__), "validate_results.json"), "r") as f:
            self.validate_results = json.load(f)

        # prevent data loss
        atexit.register(self.exit)
        self.heartbeat_file = os.path.join(os.path.dirname(__file__), ".heartbeat.json")

        # Check for unclean shutdown
        if self.was_unclean_shutdown():
            self.recover_from_unclean_shutdown()

        # Start heartbeat in a separate thread
        threading.Thread(target = self.start_heartbeat, daemon = True).start()

        '''
        # print selected image in a separate thread for debugging
        def print_selected_image():
            while True:
                time.sleep(1)
                print(self.selected_image_div.current_image)

        threading.Thread(target = print_selected_image, daemon = True).start()
        '''

    def start_heartbeat(self):
        last_saved = self.validate_results.copy()
        while True:
            time.sleep(60)  # update heartbeat file every minute
            if self.validate_results != last_saved:
                with open(self.heartbeat_file, 'w') as file:
                    json.dump(self.validate_results, file, indent = 4, ensure_ascii = False)
                last_saved = self.validate_results.copy()

    def was_unclean_shutdown(self):
        return os.path.exists(self.heartbeat_file)

    def recover_from_unclean_shutdown(self):
        with open(self.heartbeat_file, 'r') as file:
            self.validate_results = json.load(file)

    def current_validator(self):
        return self.validators[self.current_validator_index]
    
    def labels_of(self, image_path):
        if image_path == self.placeholder_image:
            return ["None"]
        image_name = os.path.basename(image_path)
        # if has file extension, remove it
        if '.' in image_name:
            image_name = image_name[:image_name.index('.')]
        labels = image_name.split('_')[0]
        labels = [labels[i:i+3] for i in range(0, len(labels), 3)]
        return [f"{label}: {self.catagory2food[label]}" for label in labels]
    
    def record_result(self, result, remark):
        current_image_name = os.path.basename(self.selected_image_div.current_image)
        # if has file extension, remove it
        if '.' in current_image_name:
            current_image_name = current_image_name[:current_image_name.index('.')]
        if current_image_name not in self.validate_results:
            self.validate_results[current_image_name] = {}
        if remark == "":
            remark = "None"
        self.validate_results[current_image_name][self.current_validator()] = result + " - " + remark

    def random_images(self, num = 1):
        images = []
        random.shuffle(self.images)
        for image in self.images:
            if image not in images and not self.is_already_validated_by_current_validator(image):
                images.append(image)
            if len(images) == num:
                return images
        # if not enough images, return placeholder image
        return images + [self.placeholder_image] * (num - len(images))
    
    # remove file extension & char before first underscore
    def id_of(self, image_path):
        if image_path == self.placeholder_image:
            return "No."
        image_name = os.path.basename(image_path)
        # if has file extension, remove it
        if '.' in image_name:
            image_name = image_name[:image_name.index('.')]
        image_name = image_name[image_name.index('_') + 1:]
        return image_name
    
    def is_already_validated_by_current_validator(self, image_path):
        if image_path == self.placeholder_image:
            return False
        image_name = os.path.basename(image_path)
        # if has file extension, remove it
        if '.' in image_name:
            image_name = image_name[:image_name.index('.')]
        if image_name not in self.validate_results:
            return False
        return self.current_validator() in self.validate_results[image_name]
    
    def exit(self):
        with open(os.path.join(os.path.dirname(__file__), "validate_results.json"), "w") as f:
            json.dump(self.validate_results, f, indent = 4, ensure_ascii = False)
        if os.path.exists(self.heartbeat_file):
            os.remove(self.heartbeat_file)
        exit()

# Main application
class App:

    # create image div
    def create_img_div(self, root, *, is_temp = False):
        img_div = QWidget(root)
        img_div.setStyleSheet(f"background-color: {background_color_light};")
        img_div.setFixedSize(int(div_size * 1.5), div_size) # 336 x 224

        # image
        img_div.label = ClickableLabel(img_div)
        img_div.label.setPixmap(QPixmap(self.control.placeholder_image))
        img_div.label.setScaledContents(True)
        img_div.label.resize(div_size, div_size)
        img_div.label.clicked.connect(lambda: self.image_clicked(img_div))

        img_div.current_image = self.control.placeholder_image
        img_div.is_selected = False

        # button
        img_div.to_temp_button = QtWidgets.QPushButton(img_div)
        img_div.to_temp_button.setStyleSheet(button_style_inactive)
        img_div.to_temp_button.setFixedSize(int(div_size * 0.5) - pad * 2, int(div_size * 0.09375)) # 112 x 21
        if is_temp:
            img_div.to_temp_button.setText("Clear")
            img_div.to_temp_button.clicked.connect(lambda: self.clear_image_div(img_div))
        else:
            img_div.to_temp_button.setText("Swap to Temp")
            img_div.to_temp_button.clicked.connect(lambda: self.swap_image_with_temp(img_div))

        # text label
        img_div.title_text = QLabel(img_div)
        img_div.title_text.setText("No.")
        img_div.title_text.setStyleSheet(f"background-color: {background_color_light}; color: {text_color};")
        img_div.title_text.setFixedSize(int(div_size * 0.5) - pad * 2, int(div_size * 0.09375)) # 112 x 21

        # label text
        img_div.label_text = QLabel(img_div)
        img_div.label_text.setText("Current labels: ")
        img_div.label_text.setStyleSheet(f"background-color: {background_color_light}; color: {text_color};")
        img_div.label_text.setFixedSize(int(div_size * 0.5) - pad * 2, int(div_size * 0.09375)) # 112 x 21

        # current labels
        img_div.current_label_list = QtWidgets.QListWidget(img_div)
        img_div.current_label_list.addItems([
            "None"
        ])
        img_div.current_label_list.setFixedSize(int(div_size * 0.5) - pad * 2, int(((div_size - pad * 5 - int(div_size * 0.09375) * 3) - pad) * 0.4)) # 112 x 21
        img_div.current_label_list.setStyleSheet(f"color: {text_color};")

        # remark (A text box for the validator to write down remarks)
        img_div.remark_text = QtWidgets.QTextEdit(img_div)
        img_div.remark_text.setFixedSize(int(div_size * 0.5) - pad * 2, int(((div_size - pad * 5 - int(div_size * 0.09375) * 3) - pad) * 0.6)) # 112 x 21
        img_div.remark_text.setReadOnly(True)
        img_div.remark_text.setStyleSheet(f"color: {text_color};")

        # position items in img_div
        img_div.label.move(0, 0)
        img_div.to_temp_button.move(div_size + pad, pad)
        img_div.title_text.move(div_size + pad, int(div_size * 0.09375) + pad * 2)
        img_div.label_text.move(div_size + pad, int(div_size * 0.09375) * 2 + pad * 3)
        img_div.current_label_list.move(div_size + pad, int(div_size * 0.09375) * 3 + pad * 4)
        img_div.remark_text.move(div_size + pad, int(div_size * 0.09375) * 3 + pad * 4 + int(((div_size - pad * 5 - int(div_size * 0.09375) * 3) - pad) * 0.4) + pad)
        return img_div

    def __init__(self, root: Root):
        self.root = root
        self.control = ControlSystem()

        # rewrite closeEvent
        self.root.closeEvent = self.exit

        # create frames
        # - top bar
        self.top_bar = QWidget(self.root)
        self.top_bar.setStyleSheet(f"background-color: {background_color_light};")
        self.top_bar.setFixedSize(int(div_size * 6) + pad * 3, int(div_size * 0.09375) + pad * 2) # 1344 x 27
        self.top_bar.move(pad, pad)

        # - random image section
        self.rand_img_div = [self.create_img_div(self.root) for _ in range(3)]
        for i, div in enumerate(self.rand_img_div):
            div.move(int(div_size * 1.5) * i + pad * (i + 1), int(div_size * 0.09375) + pad * 4)

        # - temp image section
        self.temp_img_div = self.create_img_div(self.root, is_temp = True)
        self.temp_img_div.move(int(div_size * 1.5) * len(self.rand_img_div) + pad * (len(self.rand_img_div) + 1), int(div_size * 0.09375) + pad * 4)
        
        # - main image section
        self.main_img_div = [self.create_img_div(self.root) for _ in range(12)]
        for i, div in enumerate(self.main_img_div):
            # 4 images per row, 3 rows
            x, y = i % 4, i // 4
            div.move(int(div_size * 1.5) * x + pad * (x + 1), int(div_size * 0.09375) + pad * 4 + (div_size + pad) * (y + 1))

        # items in top bar
        # - validator label
        self.validator_label = QLabel(self.top_bar)
        self.validator_label.setText("Validator:")
        self.validator_label.setStyleSheet(f"background-color: {background_color_light}; color: {text_color};")
        self.validator_label.setFixedSize(int(div_size * 0.25), int(div_size * 0.09375)) # 168 x 21
        self.validator_label.move(pad, pad)

        # - validator dropdown
        self.validator_dropdown = QtWidgets.QComboBox(self.top_bar)
        self.validator_dropdown.setStyleSheet(f""" 
            QComboBox {{
                border: 1px solid {background_color_dark};
                border-radius: 4px;
                padding-left: 10px;
                color: {text_color};
            }}
            QComboBox::drop-down {{
                border: 0px;
            }}
            QComboBox::down-arrow {{
                image: url(./app/system_img/dropdown_arrow.png);
                width: 12px;
                height: 12px;
                margin-right: 15px;
            }}
            QComboBox:on {{
                border: 2px solid {text_color};
            }}
            QComboBox::item:selected {{
                color: {background_color_dark};
            }}
            """
        )
        self.validator_dropdown.setFixedSize(int(div_size * 0.75), int(div_size * 0.09375)) # 168 x 21
        self.validator_dropdown.addItems(self.control.validators)
        self.validator_dropdown.currentIndexChanged.connect(self.on_validator_changed)
        self.validator_dropdown.move(int(div_size * 0.25) + pad * 2, pad)

        # - generate random image button
        self.generate_random_image_button = QtWidgets.QPushButton(self.top_bar)
        self.generate_random_image_button.setText("Random")
        self.generate_random_image_button.setStyleSheet(button_style_active)
        self.generate_random_image_button.setFixedSize(int(div_size * 0.4), int(div_size * 0.09375)) # 168 x 21
        self.generate_random_image_button.move(div_size + pad * 6, pad)
        self.generate_random_image_button.clicked.connect(self.random_image)

        # - accept button
        self.accept_button = QtWidgets.QPushButton(self.top_bar)
        self.accept_button.setText("Accept")
        self.accept_button.setStyleSheet(button_style_inactive)
        self.accept_button.setFixedSize(int(div_size * 0.4), int(div_size * 0.09375)) # 168 x 21
        self.accept_button.move(div_size + int(div_size * 0.4) + pad * 8, pad)
        self.accept_button.clicked.connect(lambda: self.record_result("accept"))

        # - incorrect button
        self.incorrect_button = QtWidgets.QPushButton(self.top_bar)
        self.incorrect_button.setText("Incorrect")
        self.incorrect_button.setStyleSheet(button_style_inactive)
        self.incorrect_button.setFixedSize(int(div_size * 0.4), int(div_size * 0.09375)) # 168 x 21
        self.incorrect_button.move(div_size + int(div_size * 0.8) + pad * 10, pad)
        self.incorrect_button.clicked.connect(lambda: self.record_result("incorrect"))

        # - reject button
        self.reject_button = QtWidgets.QPushButton(self.top_bar)
        self.reject_button.setText("Reject")
        self.reject_button.setStyleSheet(button_style_inactive)
        self.reject_button.setFixedSize(int(div_size * 0.4), int(div_size * 0.09375)) # 168 x 21
        self.reject_button.move(div_size + int(div_size * 1.2) + pad * 12, pad)
        self.reject_button.clicked.connect(lambda: self.record_result("reject"))

        # - save button
        # save main image section
        self.save_main_button = QtWidgets.QPushButton(self.top_bar)
        self.save_main_button.setText("Save")
        self.save_main_button.setStyleSheet(button_style_active)
        self.save_main_button.setFixedSize(int(div_size * 0.4), int(div_size * 0.09375)) # 168 x 21
        self.save_main_button.move(div_size + int(div_size * 1.6) + pad * 14, pad)
        self.save_main_button.clicked.connect(self.save_main)
        
        # - load button
        # load main image section
        self.load_main_button = QtWidgets.QPushButton(self.top_bar)
        self.load_main_button.setText("Load")
        self.load_main_button.setStyleSheet(button_style_active)
        self.load_main_button.setFixedSize(int(div_size * 0.4), int(div_size * 0.09375)) # 168 x 21
        self.load_main_button.move(div_size + int(div_size * 2.0) + pad * 16, pad)
        self.load_main_button.clicked.connect(self.load_main)

    def on_validator_changed(self, index):
        self.control.current_validator_index = index

    def random_image(self):
        # set images
        rand_img = self.control.random_images(num = self.rand_img_div.__len__())
        for i, div in enumerate(self.rand_img_div):
            self.set_image_div(div, rand_img[i])

    def swap_image_with_temp(self, img_div):
        # if this is the temp image, do nothing
        if img_div is self.temp_img_div:
            return

        temp_image = self.temp_img_div.current_image
        image = img_div.current_image

        # record if image is selected
        image_was_selected = img_div.is_selected
        temp_was_selected = self.temp_img_div.is_selected

        # record image remark
        image_remark = img_div.remark_text.toPlainText()
        temp_remark = self.temp_img_div.remark_text.toPlainText()

        # swap images
        self.set_image_div(self.temp_img_div, image)
        self.set_image_div(img_div, temp_image)

        # swap remarks
        img_div.remark_text.setText(temp_remark)
        self.temp_img_div.remark_text.setText(image_remark)

        # reselect image
        if image_was_selected:
            self.image_clicked(self.temp_img_div)
        if temp_was_selected:
            self.image_clicked(img_div)


    def image_clicked(self, image_div):
        # if no image, do nothing
        if image_div.current_image == self.control.placeholder_image:
            return
        
        if image_div.is_selected:
            # unselect image
            image_div.label.setStyleSheet(img_style_unselected)
            image_div.is_selected = False

            # deactivate buttons
            self.deactivate_validate_buttons()

            # clear selected image
            self.control.selected_image_div = None
            return
        
        # activate buttons
        self.activate_validate_buttons()

        # update selected image
        self.control.selected_image_div = image_div

        # unselect all other images
        for div in self.rand_img_div:
            div.label.setStyleSheet(img_style_unselected)
            div.is_selected = False

        for div in self.main_img_div:
            div.label.setStyleSheet(img_style_unselected)
            div.is_selected = False

        self.temp_img_div.label.setStyleSheet(img_style_unselected)
        self.temp_img_div.is_selected = False

        # select this image
        image_div.label.setStyleSheet(img_style_selected)
        image_div.is_selected = True

    def record_result(self, result):
        if self.control.selected_image_div is None:
            return
        remark = self.control.selected_image_div.remark_text.toPlainText()
        self.control.record_result(result, remark)

    def save_main(self):
        # save into {date}_{time}.data
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        #save_file = os.path.join(save_location, f"{current_time}.data")

        # pop out a dialog to ask for save location and file name
        save_file = QFileDialog.getSaveFileName(self.root, "Save File", f"./{current_time}.data",filter = "Data Files (*.data)")[0]
        if save_file == "":
            return

        with open(save_file, 'w') as f:
            images = [(div.current_image, div.remark_text.toPlainText()) for div in self.main_img_div]
            json.dump(images, f, indent = 4, ensure_ascii = False)

    def load_main(self):
        # select a .data file
        load_file = QFileDialog.getOpenFileName(self.root, "Select File", filter = "Data Files (*.data)")[0]
        if load_file == "":
            return
        
        with open(load_file, 'r') as f:
            images = json.load(f)
            for img_div, (image, remark) in zip(self.main_img_div, images):
                self.set_image_div(img_div, image, remark = remark)

    def set_image_div(self, image_div, image_path, remark = ""):
        # if image is placeholder, clear image div
        if image_path == self.control.placeholder_image:
            self.clear_image_div(image_div)
            return
        
        image_div.label.setPixmap(QPixmap(image_path))
        image_div.current_image = image_path

        # update title
        image_div.title_text.setText(f"No.{self.control.id_of(image_path)}")

        # update current labels
        image_div.current_label_list.clear()
        image_div.current_label_list.addItems(self.control.labels_of(image_path))

        # update remark
        image_div.remark_text.setText(remark)
        image_div.remark_text.setReadOnly(False)

        # activate swap button
        if image_div is self.temp_img_div:
            self.activate_clear_button()
            for div in self.rand_img_div + self.main_img_div + [self.temp_img_div]:
                self.activate_swap_button(div)
        else:
            self.activate_swap_button(image_div)

        # update selected image
        if image_div.is_selected:
            image_div.is_selected = False
            self.image_clicked(image_div)

    def clear_image_div(self, image_div):
        image_div.label.setPixmap(QPixmap(self.control.placeholder_image))
        image_div.current_image = self.control.placeholder_image
        image_div.title_text.setText("No.")
        image_div.current_label_list.clear()
        image_div.current_label_list.addItems(["None"])
        image_div.remark_text.clear()
        image_div.remark_text.setReadOnly(True)

        # unselect image
        if image_div.is_selected:
            self.control.selected_image_div = None
            image_div.label.setStyleSheet(img_style_unselected)
            image_div.is_selected = False

            # deactivate buttons
            self.deactivate_validate_buttons()

        if image_div is self.temp_img_div:
            self.deactivate_clear_button()
            for div in self.rand_img_div + self.main_img_div + [self.temp_img_div]:
                if div.current_image == self.control.placeholder_image:
                    self.deactivate_swap_button(div)
        else:
            if self.temp_img_div.current_image == self.control.placeholder_image:
                self.deactivate_swap_button(image_div)

    def activate_swap_button(self, image_div):
        image_div.to_temp_button.setStyleSheet(button_style_active)

    def deactivate_swap_button(self, image_div):
        image_div.to_temp_button.setStyleSheet(button_style_inactive)

    def activate_clear_button(self):
        self.temp_img_div.to_temp_button.setStyleSheet(button_style_active)

    def deactivate_clear_button(self):
        self.temp_img_div.to_temp_button.setStyleSheet(button_style_inactive)

    def activate_validate_buttons(self):
        self.accept_button.setStyleSheet(button_style_active)
        self.incorrect_button.setStyleSheet(button_style_active)
        self.reject_button.setStyleSheet(button_style_active)

    def deactivate_validate_buttons(self):
        self.accept_button.setStyleSheet(button_style_inactive)
        self.incorrect_button.setStyleSheet(button_style_inactive)
        self.reject_button.setStyleSheet(button_style_inactive)

    def exit(self, event):
        self.control.exit()

# Read Me: Label Validator

## Structure:

1. **Imports and Constants**:
    - Essential libraries like `os`, `json`, `atexit`, `time`, `threading`, `re`, and `random` are imported.
    - PyQt5, a popular GUI library in Python, is imported for building the interface.
    - Various constants like `div_size`, `pad`, and different color schemes for the GUI are defined.

2. **Styling**:
    - CSS-like styles are provided for buttons and images within the interface. These dictate the visual appearance of active and inactive buttons, as well as selected and unselected images.

3. **ClickableLabel**:
    - A subclass of QLabel, designed to emit a signal when the label is clicked.
    
    - **Variables**:
        - `clicked`: A signal that is emitted when the label is clicked.

    - **Functions**:
        - `mousePressEvent(event)`: Handles the mouse press event on the label. If the left button is clicked, it emits the `clicked` signal.

4. **Root**:
    - Represents the main window of the application.
    
    - **Variables**: None.
    
    - **Functions**:
        - `__init__()`: Initializes the Root window with the title "Label Validator" and sets its size and background color.

5. **ControlSystem**:
    - This class manages the backend logic of the application, including loading images, tracking validators, and recording validation results.
    
    - **Variables**:
        - `catagory2food`: A dictionary that maps category codes to food names.
        - `images_folder`: The path to the folder containing all the images.
        - `images`: A list containing paths to all valid images in the `images_folder`.
        - `validators`: A list of validator names.
        - `current_validator_index`: An index that keeps track of the current selected validator.
        - `placeholder_image`: The path to the placeholder image.
        - `selected_image`: The path to the currently selected image.
        - `validate_results`: A dictionary that holds the validation results for each image.
        - `heartbeat_file`: The path to the heartbeat file used to check for unclean shutdowns and save data periodically.
        
    - **Functions**:
        - `__init__()`: Initializes the ControlSystem by loading image paths, setting up validators, and other initial tasks.
        - `start_heartbeat()`: Continuously saves `validate_results` to the heartbeat file in a separate thread.
        - `was_unclean_shutdown()`: Checks if there was an unclean shutdown based on the presence of the heartbeat file.
        - `recover_from_unclean_shutdown()`: Recovers validation results from the heartbeat file after an unclean shutdown.
        - `current_validator()`: Returns the name of the current validator.
        - `labels_of(image_path)`: Returns the labels associated with the given image.
        - `record_result(result)`: Records the validation result of the currently selected image for the current validator.
        - `random_image()`: Returns a random image path from the `images` list.
        - `id_of(image_path)`: Returns the id of the provided image path.
        - `exit()`: Saves the validation results, removes the heartbeat file, and exits the application.

6. **App**:
    - This class represents the main application interface. It provides GUI elements and functionalities for handling images, including creating, loading, saving, and displaying them in a structured layout.

    - **Variables**:
        - `root`: The root widget for the application.
        - `control`: An instance of the ControlSystem, which likely handles logic and data related to the application.
        - `top_bar`: The top bar widget of the application, which contains multiple buttons and other GUI elements.
        - `rand_img_div`: A list of widgets representing random image sections.
        - `temp_img_div`: A widget representing the temporary image section.
        - `main_img_div`: A list of widgets representing the main image sections.
        - `validator_label`: A label indicating the current validator.
        - `validator_dropdown`: A dropdown menu to select a validator.
        - `generate_random_image_button`: A button to generate random images.
        - `accept_button`: A button to accept the current image.
        - `incorrect_button`: A button to label the image as incorrect.
        - `reject_button`: A button to reject the current image.
        - `save_main_button`: A button to save the main image.
        - `load_main_button`: A button to load a saved main image.
        
    - **Functions**:
        - `create_img_div(root, *, is_temp = False)`: Creates an image widget with related controls, where images can be loaded and displayed.
        - `__init__(root: Root)`: Initializes the App class with the main GUI layout and related functionalities.
        - `on_validator_changed(index)`: Updates the selected validator when a different validator is chosen from the dropdown.
        - `random_image()`: Generates three random images and displays them in their respective sections.
        - `swap_image_with_temp(img_div)`: Swaps the provided image with the temporary image.
        - `image_clicked(image_div)`: Handles the image click event to select or deselect an image.
        - `record_result(result)`: Records the result (e.g., "accept", "incorrect", "reject") for the currently selected image.
        - `save_main()`: Saves the main image set to a specified location.
        - `load_main()`: Loads a previously saved main image set from a specified location.
        - `set_image_div(image_div, image_path)`: Sets the image of the provided image widget with the given image path.

---

## Author:
Jeffrey Chen

## Prerequisites:
To run this code, you need:
- Python 3.x
- PyQt5 library installed
- Properly set path to the images directory in the `ControlSystem` class.

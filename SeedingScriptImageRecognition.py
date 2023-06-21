from PIL import Image
import easyocr
import pyautogui
import numpy as np
import cv2


def find_string_on_screen(text):
    # Take a screenshot
    screenshot = pyautogui.screenshot()

    # Convert the PIL Image to OpenCV format (numpy array)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'])

    # Perform OCR using EasyOCR
    result = reader.readtext(screenshot, detail=1)

    # Look for the text
    for item in result:
        if text.lower() in item[1].lower():
            # Calculate the center position of the found text
            bounding_box = item[0]
            x = (bounding_box[0][0] + bounding_box[2][0]) / 2
            y = (bounding_box[0][1] + bounding_box[2][1]) / 2

            # Return the coordinates
            return x, y

    # Return None if the text is not found
    return None, None


def main():
    # test = 'server browser'
    test = 'servers'

    x, y = find_string_on_screen(test)
    if x and y:
        pyautogui.click(x, y)


if __name__ == '__main__':
    main()

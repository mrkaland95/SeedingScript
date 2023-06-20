import pyautogui
import pytesseract
from PIL import Image

def get_text_location_from_image(image, text_to_find: str):
    # Open the image and convert it to grayscale
    # image = Image.open(img)
    image = image.convert('L')

    # Extract the text and location data from the image
    data = pytesseract.image_to_data(image)
    x, y, w, h = None, None, None, None
    # Find the location of the specific text you are looking for
    for i in range(len(data['text'])):
        if data['text'][i] == text_to_find:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            print(f'The specific text was found at x={x}, y={y}, w={w}, h={h}')

    return (x, y, w, h)

def take_screenshot_and_get_text_location(text_to_find_str):
    screenshot = pyautogui.screenshot()
    x, y, w, h = get_text_location_from_image(screenshot, text_to_find_str)
    print(screenshot)


def main():
    text = 'main'
    take_screenshot_and_get_text_location(text)



if __name__ == '__main__':
    main()

import requests
from bs4 import BeautifulSoup
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract
import re
import pprint
import pickle
from pathlib import Path

def get_list_of_items():
    url = r'https://www.lidl.co.uk/en/All-Wines-3601.htm'
    page = requests.get(url)

    try:
        soup = BeautifulSoup(page.text,'html.parser')
        list_of_items = soup.find_all(class_='productgrid__item')
    except:
        print('could not parse html')
    return list_of_items

def remove_temp_files():
    try:
        os.remove('temp.jpg')
    except OSError:
        pass
    try:
        os.remove('extracted_digits.png')
    except OSError:
        pass
    try:
        os.remove('results.png')
    except OSError:
        pass

def parse_list_of_items(list_of_items):
    list_of_dicts = []
    list_of_prices = []
    list_of_scores = []
    for item_count in range(len(list_of_items)):
        list_of_item_image_urls = list_of_items[item_count].find_all('a')

        item_dict = {}
        item_dict['price'] = float(list_of_items[item_count]['data-price'])
        item_dict['name'] = list_of_items[item_count]['data-name']

        image_urls = [i for i in list_of_item_image_urls[0].find_all('img')[0]['data-srcset'].split(' ') if '.jpg' in i]
        image_url = [i for i in image_urls if 'lg-retina' in i]

        remove_temp_files()

        try:
            f = open('temp.jpg','wb')
            f.write(requests.get(image_url[0]).content)
            f.close()
        except:
            print('could not retrieve image')

        image = cv2.imread('temp.jpg')

        image_copy = image.copy()
        gray = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)

        try:
            circles = np.round(circles[0, :]).astype("int")
        except TypeError:
            continue

        for (x, y, r) in circles:
        	cv2.circle(image_copy, (x, y), r, (0, 255, 0), 4)

        circle_coords = circles[0]
        crop_img = image[(circle_coords[1]-circle_coords[2]):(circle_coords[1]+circle_coords[2]),
                         (circle_coords[0]-circle_coords[2]):(circle_coords[0]+circle_coords[2])]

        resized_image = cv2.resize(crop_img, (200, 200))
        extracted_digits = resized_image[40:125,30:175]
        cv2.imwrite('extracted_digits.png',extracted_digits)

        pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
        extracted_digits = pytesseract.image_to_string(Image.open('extracted_digits.png'))

        try:
            wine_score = int(re.findall(r'\d+',extracted_digits)[0])
            if len(str(wine_score)) == 2:
                item_dict['score'] = wine_score
                list_of_dicts.append(item_dict)
                list_of_prices.append(item_dict['price'])
                list_of_scores.append(wine_score)
                pprint.pprint(item_dict)
        except:
            pass
    remove_temp_files()
    return list_of_dicts, list_of_prices, list_of_scores

def save_data(list_of_dicts, list_of_prices, list_of_scores):
    with open('results.pkl', 'wb') as f:
        pickle.dump([list_of_dicts, list_of_prices, list_of_scores], f)


def check_if_data_exists():
    my_file = Path("results.pkl")
    if my_file.is_file():
        return True
    else:
        return False

def load_data():
    with open('results.pkl','rb') as f:
        list_of_dicts, list_of_prices, list_of_scores = pickle.load(f)
    return list_of_dicts, list_of_prices, list_of_scores

def plot_data(list_of_prices, list_of_scores):
    plt.figure(figsize=(9, 6))
    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    plt.ylabel("Price (£)", fontsize=16)
    plt.title("Lidl Wine Scores vs. Price", fontsize=22)
    plt.xlabel("Wine score", fontsize=16)
    plt.scatter(list_of_scores, list_of_prices)
    plt.grid(linestyle='dotted')
    plt.savefig('results.png', bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    if check_if_data_exists():
        list_of_dicts, list_of_prices, list_of_scores = load_data()
    else:
        list_of_items = get_list_of_items()
        list_of_dicts, list_of_prices, list_of_scores = parse_list_of_items(list_of_items)
        save_data(list_of_dicts, list_of_prices, list_of_scores)

    plot_data(list_of_prices, list_of_scores)

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
import mpld3


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

def fetch_image_from_url(image_url):
    remove_temp_files()
    try:
        f = open('temp.jpg','wb')
        f.write(requests.get(image_url).content)
        f.close()
    except:
        print('could not retrieve image')
    image = cv2.imread('temp.jpg')
    return image

def analyse_circle(circle, image):
    circle_coords = circle
    crop_img = image[(circle_coords[1]-circle_coords[2]):(circle_coords[1]+circle_coords[2]),
                     (circle_coords[0]-circle_coords[2]):(circle_coords[0]+circle_coords[2])]
    resized_image = cv2.resize(crop_img, (200, 200))
    extracted_digits = resized_image[35:130,30:175]
    extracted_digits = cv2.cvtColor(extracted_digits, cv2.COLOR_BGR2GRAY)
    extracted_digits = cv2.bitwise_not(extracted_digits)
    extracted_digits_resize = cv2.resize(extracted_digits, (200, 200))
    cv2.imwrite('extracted_digits.png',extracted_digits_resize)
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
    extracted_digits_vals = pytesseract.image_to_string(Image.open('extracted_digits.png'))
    try:
        wine_score = int(re.sub("\D", "", extracted_digits_vals))
        if len(str(wine_score)) == 2:
            if 79 <= wine_score <= 100:
                return wine_score
        else:
            import ipdb; ipdb.set_trace()
            return None
    except:
        return None

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

        image = fetch_image_from_url(image_url[0])
        image_copy = image.copy()
        gray = cv2.cvtColor(image_copy, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)

        try:
            circles = np.round(circles[0, :]).astype("int")
        except TypeError:
            continue

        # for (x, y, r) in circles:
        # 	cv2.circle(image_copy, (x, y), r, (0, 255, 0), 4)

        for circle in circles:
            wine_score = analyse_circle(circle, image)
            if wine_score:
                item_dict['score'] = wine_score
                list_of_dicts.append(item_dict)
                list_of_prices.append(item_dict['price'])
                list_of_scores.append(wine_score)
                pprint.pprint(item_dict)

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

def plot_data(list_of_dicts, list_of_prices, list_of_scores):
    fig, ax = plt.subplots(subplot_kw=dict(axisbg='#f7f8f9'))
    N = len(list_of_prices)
    scatter = ax.scatter([i['score'] for i in list_of_dicts],
                         [i['price'] for i in list_of_dicts],
                         c=np.random.random(size=N),
                         alpha=0.7,
                         cmap=plt.cm.brg)
    ax.grid(color='white', linestyle='solid')
    ax.set_title("Lidl Wine vs. Score", size=30)
    ax.set_xlabel('Score',fontsize=20)
    ax.set_ylabel('Price (£)',fontsize=20)
    ax.set_xlim([82, 89])
    labels = ['{0}'.format(i['name']) for i in list_of_dicts]
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    mpld3.plugins.connect(fig, tooltip)
    html_string = mpld3.fig_to_d3(fig, template_type="simple")
    Html_file= open("results.html","w")
    Html_file.write(html_string)
    Html_file.close()
    mpld3.show()

if __name__ == "__main__":
    if check_if_data_exists():
        list_of_dicts, list_of_prices, list_of_scores = load_data()
    else:
        list_of_items = get_list_of_items()
        list_of_dicts, list_of_prices, list_of_scores = parse_list_of_items(list_of_items)
        save_data(list_of_dicts, list_of_prices, list_of_scores)

    plot_data(list_of_dicts,list_of_prices, list_of_scores)

# Lidl Wine Optimiser

## About

I wondered whether the score that Lidl assigns to some of its wines was directly correlated with their price. This code uses `requests` and `BeautifulSoup` combined with the amazing OCR library `pytesseract` to find out!

## Installation

```
pip install -r requirements.txt
```

## Running
The repository already contains the results (`results.pkl`) and plot of the data (`results.png`) so if you run the code it will just plot out the data. However, if you delete those files the script will start afresh and print out its results as they are scraped from the Lidl website.

```
python main.py
```

## Results
Can be viewed [here]( http://htmlpreview.github.com/?https://github.com/bartaz/impress.js/blob/master/index.html)

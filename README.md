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
As can be seen in the figure below, all scores were between 83 to 89. The outlier at score 83 (Cimarosa South African Cabernet, £14.65) is in fact a wine box, which is why it's more expensive. I should really normalise to volume, but that is beyond the scope of this project (!). If you were trying to optimise your wine buying I'd recommend either the Late Harvest Tokaji (score = 89, £7.99) or the Forteza dei Colli Chianti Classico (score = 88, £5.49) as they're the two highest scoring, lowest price wines. In general there's a positive correlation between score and price - producing a curve fit is also left for the interested reader. 

![Results](results.png?raw=true "Results")

Interactive version can be viewed [here]( https://cdn.rawgit.com/vcc-LG/lidl-wine/d56debf1/results.html)

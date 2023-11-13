# Scrap(e)s of Democracy

A GUI app and scraping library to scrape and view government consultations.

![image](https://github.com/philippgovernale/Scrapes-of-democracy/assets/16997121/2ce1507a-7da8-46d1-9c75-80ef1bde7e1f)


## Features
* View and scrape consultations in a familiar email-like interface
* Includes library 'polis' that performs scraping that can be used in other project
* Polis can be easily extended with new scripts for government organisations
* Minimal dependencies (only BeautifulSoup)
* Cross-platform (theoretically!)

## Run
```pip install -r requirements.txt```

```python app.py```

**Note** Requires Python 3.11

## Polis scripts
Currently scripts exist for the following NZ government organisations:
* Ministry for the Environment
* Climate Change Commission
* Ministry of Transport
* Ministry for Primary Industries
* Ministry for Business, Innovation and Employment
* Ministry of Justice
* Ministry of Education
* Oranga Tamariki

## FAQ

**A script fails with HTTP forbidden error**
The server has blocked your access. Currently there is no workaround, so you will need to disable the script. Press 'refresh' and uncheck the failing script. 

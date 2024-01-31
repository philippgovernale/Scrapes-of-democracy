# Scrap(e)s of Democracy

A GUI app and scraping library to scrape, collate and view government consultations. While the NZ government has [its own cross-government consultation platform](https://www.govt.nz/browse/engaging-with-government/consultations-have-your-say/consultations-listing/?status=Open), at the moment the service only collates consultations from a limited number of agencies.

![image](https://github.com/philippgovernale/Scrapes-of-democracy/assets/16997121/2ce1507a-7da8-46d1-9c75-80ef1bde7e1f)


## Features
* View and scrape consultations in a familiar email-like interface
* Includes scraping library 'polis' that can be used in other projects
* Polis can be easily extended with new scripts for government organisations
* Mailservice allows you to automatically send emails with any new consulations to a mailing list on a recurring basis
* Minimal dependencies (only BeautifulSoup)
* Cross-platform (theoretically!)

## Setup
**Note** Requires Python 3.11
```pip install -r requirements.txt```

## Run

### GUI scraper and viewer
```python app.py```

### Mailservice
Mailservice sends an email with new consultations from an email account with smptp server support. To set it up follow the below instructions:

1. Create a plain text file called CREDENTIALS
2. Insert each of the following data on a newline in the CREDENTIALS file
   - smtp server address (i.e. smtp.gmail.com)
   - smtp server port (i.e. 587)
   - email address
   - password (this should ideally be an app password. See [here](https://support.google.com/mail/answer/185833?hl=en) how to do this with gmail)
3. Your file should look something like this
   ```
   smtp.****.com
   587
   example@email.com
   ghvd hfjs hfjs kfks
   ```
4. Create a RECIPIENTS plain text file and append each recipient email address on a newline
5. If you don't want to configure when and how often the mailservice should send updates with new emails you can skip this step. By default it sends one email every week on a Wednesday at 1 pm. If you do wish to configure this and you are on WINDOWS, you will need to edit the fourth line of the batch script which runs the inbuilt schtasks command. You can find documentation on schtasks [here](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create). If you are on GNU/LINUX, then open the crontab file and edit it according to your needs. The ubuntu [crontab howto](https://help.ubuntu.com/community/CronHowto) may be of help 
6. If you are on on WINDOWS, run task_schedule.bat by double clicking on the file in explorer. If you are on GNU/LINUX, run ```crontab consultations_crontab```

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
* Ministry of Housing and Urban Development

## FAQ

**A script fails with HTTP forbidden error**
The server has blocked your access. Currently there is no workaround, so you will need to disable the script if you do not wish to see the error.

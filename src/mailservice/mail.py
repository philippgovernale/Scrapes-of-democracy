import model
import polis

import smtplib
import email.mime.multipart
import email.mime.text
import pathlib
import bs4

# Run with python -m mailservice.mail

def create_html(consultations: list[model.Entry]):
    soup = bs4.BeautifulSoup()

    html_tag = bs4.Tag(soup, name='html')
    soup.append(html_tag)

    if not consultations:
        no_consultations_tag = bs4.Tag(soup, name='p')
        no_consultations_tag.append("No new consultations :)")
        html_tag.append(no_consultations_tag)

    for consultation in consultations:
        entry_data = consultation.entry_data

        div_tag = bs4.Tag(soup, name='div')
        title_tag = bs4.Tag(soup, name='h2')
        org_tag = bs4.Tag(soup, name='h3')
        expiry_tag = bs4.Tag(soup, name='p')
        bold_tag = bs4.Tag(soup, name='b')
        link_tag = bs4.Tag(soup, name='a')
        blurb_tag = bs4.Tag(soup, name='p')

        html_tag.append(div_tag)
        div_tag.append(title_tag)
        div_tag.append(org_tag)
        div_tag.append(expiry_tag)
        expiry_tag.append(bold_tag)
        div_tag.append(blurb_tag)
        div_tag.append(link_tag)
        link_tag['href'] = entry_data.url

        entry_data = consultation.entry_data
        date_formatted, calendar_date = entry_data.date_formatted, entry_data.date
        blurb_formatted = "No blurb available. Check website." if not entry_data.blurb else entry_data.blurb

        title_tag.append(consultation.entry_data.title)
        org_tag.append(consultation.entry_data.org.value.name)
        bold_tag.append('Closes: ')
        expiry_tag.append(f"{date_formatted} {calendar_date}")
        blurb_tag.append(blurb_formatted)
        link_tag.append('See more')

    return soup

def send_email(
    html_msg: str,
    smtp_server_address: str,
    smtp_server_port: int,
    sender_email: str,
    sender_password: str,
    recipient_addresses: list[str]
    ) -> tuple:

    SUBJECT = 'New Government Consultations'

    msg = email.mime.multipart.MIMEMultipart('alternative')
    msg['from'] = sender_email
    msg['to'] = ", ".join(recipient_addresses)
    msg['subject'] = SUBJECT

    part1 = email.mime.text.MIMEText("You need an email client which can display HTML to read this message", 'plain')
    part2 = email.mime.text.MIMEText(html_msg, 'html')
    msg.attach(part1)
    msg.attach(part2)

    server = smtplib.SMTP(smtp_server_address, smtp_server_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()

def read_email_data(credentials_filename: str, recipients_filename: str):
    smtp_server_address, smtp_server_port = None, None
    sender_email, sender_password = None, None
    recipient_addresses = None

    credentials_filepath = pathlib.Path(__file__).with_name(credentials_filename)
    with open(credentials_filepath, 'r') as fp:
        smtp_server_address = fp.readline().strip()
        smtp_server_port = fp.readline().strip()
        sender_email = fp.readline().strip()
        sender_password = fp.readline().strip()

    recipients_filepath = pathlib.Path(__file__).with_name(recipients_filename)
    with open(recipients_filepath, 'r') as fp:
        recipient_addresses = list()

        for address in fp:
            recipient_address = address.strip()
            recipient_addresses.append(recipient_address)

    if None in {sender_email, sender_password, smtp_server_address, smtp_server_port} or not recipient_addresses:
        raise ValueError(f"Missing data in {credentials_filename} or {recipients_filename} file")

    smtp_server_port = int(smtp_server_port)

    return (smtp_server_address, smtp_server_port, sender_email, sender_password, recipient_addresses)

def main():
    data_path = pathlib.Path(__file__).with_name('mailservice.pickle')
    mod = model.Model(data_path)

    mod.scrape(polis.SCRAPERS)
    new_consultations = mod.scraper_data.get_new_entries()

    html_msg = create_html(new_consultations)
    email_data = read_email_data('CREDENTIALS', 'RECIPIENTS')
    send_email(html_msg, *email_data)

    mod.scraper_data.save_data()

if __name__ == '__main__':
    main()

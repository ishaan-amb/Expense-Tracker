# import packages required
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER = "expensetracker269@gmail.com"

def send_mail(user_mail = "examplemail@mail.com", amount = 2500):

    # Create message container - the MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "EXPENSE TRACKER - Daily Limit Exceeded"
    msg['From'] = SENDER
    msg['To'] = user_mail

    # Create the body of the message
    html = """\
    <html>
      <head></head>
      <body>
      <H1>Expense Tracker</H1>
      <h2>Daily Limit Exceeded!</H2>
        <p>Hi!<br>
           Your daily limit is exceeded <br>
           You spent """+ str(amount) + """ today.
        </p>
      </body>
    </html>
    """
    # Record the MIME type the html
    part = MIMEText(html, 'html')

    # Attach parts into message container.
    msg.attach(part)

    # Send the message via Gmail SMTP server
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    # Admin credentials
    mail.login('expensetracker269@gmail.com', 'bh@vit!@#')
    mail.sendmail(SENDER, user_mail, msg.as_string())

    print("MAIL: Mail sent successfully")
    mail.quit()

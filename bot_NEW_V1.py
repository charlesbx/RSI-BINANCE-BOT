from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from subprocess import check_call
import websocket, json, pprint, talib, numpy, sys
import config
from binance.client import Client
from binance.enums import SIDE_SELL, SIDE_BUY, ORDER_TYPE_MARKET
import percent
import time
import email
from datetime import datetime, timedelta
import imaplib

############################## TODO ##############################
## MID I = 100 + BYPASS BUY IF PRICE >0.5% LOWEST_PRICE
# LOWEST_PRICE IS ticker["lowPrice"] UNTIL 120 KLINE CLOSED
# AFTER THAT LOWEST_PRICE IS THE LOWEST PRICE SINCE THE EXECUTION
# OF THE BOT
##################################################################

if len(sys.argv) == 1:
    #### Input section
    RSI_PERIOD = int(input("RSI_PERIOD : "))
    RSI_OVERBOUGHT = int(input("RSI_OVERBOUGHT : "))
    RSI_OVERSOLD = int(input("RSI_OVERSOLD : "))
    symbol1 = input("Symbol pair:\n First currency : ")
    symbol2 = input(" Second currency : ")
    TRADE_SYMBOL = (symbol1 + symbol2).upper()
    walletUSD = float(input("Wallet USD : "))
    reportFilename = input("Report filename : ")
    sessionName = input("Session name : ")
    if reportFilename == "":
        reportFilename = datetime.now().strftime("%d-%m") + "log" + TRADE_SYMBOL + "_" + str(RSI_PERIOD) + "_" + str(RSI_OVERBOUGHT) + "_" + str(RSI_OVERSOLD)
elif len(sys.argv) > 6 and len(sys.argv) < 10:
    #### Help display
    if sys.argv[1] == "-h":
        print("Usage:\n\n python bot.py SYMBOL1 SYMBOL2 RSI_VALUE RSI_OVERBOUGHT RSI_OVERSOLD WALLET_USD LOG_FILENAME\n")
        print("SYMBOL1 = First trade symbol\nSYMBOL2 = Second trade symbol\nRSI_VALUE = Number of value to base the RSI (Change a lot the programm behaviour)")
        print("RSI_OVERBOUGHT = Value of the RSI at which the currency is considered as overbought\nRSI_OVERSOLD = Value of the RSI at which the currency is considered as oversold")
        print("WALLET_USD = Value in USDT of your wallet for testing mode\nLOG_FILENAME = Name of the log file in which the final report will be stored (if blank autofills with the date, symbol and RSI values)")
        exit()
    RSI_PERIOD = sys.argv[3]
    RSI_OVERBOUGHT = sys.argv[4]
    RSI_OVERSOLD = sys.argv[5]
    RSI_PERIOD = int(RSI_PERIOD)
    RSI_OVERBOUGHT = int(RSI_OVERBOUGHT)
    RSI_OVERSOLD = int(RSI_OVERSOLD)
    TRADE_SYMBOL = sys.argv[1] + sys.argv[2]
    symbol1 = sys.argv[1]
    symbol2 = sys.argv[2]
    walletUSD = float(sys.argv[6])
    if len(sys.argv) > 7:
        reportFilename = sys.argv[7]
    else:
        reportFilename = datetime.now().strftime("%d-%m") + "log" + TRADE_SYMBOL + "_" + str(RSI_PERIOD) + "_" + str(RSI_OVERBOUGHT) + "_" + str(RSI_OVERSOLD)
    if len(sys.argv) > 8:
        sessionName = sys.argv[8]
    else:
        sessionName = ""
else:
    print("Usage:\n\n python bot.py SYMBOL1 SYMBOL2 RSI_VALUE RSI_OVERBOUGHT RSI_OVERSOLD\n")
    print("SYMBOL1 = First trade symbol\nSYMBOL2 = Second trade symbol\nRSI_VALUE = Number of value to base the RSI (Change a lot the programm behaviour)")
    print("RSI_OVERBOUGHT = Value of the RSI at which the currency is considered as overbought\nRSI_OVERSOLD = Value of the RSI at which the currency is considered as oversold")
    print("WALLET_USD = Value in USDT of your wallet for testing mode\nLOG_FILENAME = Name of the log file in which the final report will be stored (if blank autofills with the date, symbol and RSI values)")
    exit()

client = Client(config.API_KEY, config.API_SECRET, tld='com')

#### RSI variable 
closes = []
closes.append(0.0000000)
buy_time = datetime.now()

#### Statistics variable
bad_trade_count = 0
start_time = datetime.now()

#### Trade variable 
TRADE_SYMBOL = TRADE_SYMBOL.upper()
TRADE_QUANTITY = 0.0000000

#### Test variable
if reportFilename.find("/") != -1:
    name = reportFilename.split("/")[1]
else:
    name = reportFilename
dataFile = open("DATASAVE/" + name + "DATA", "w")
reportFile = open(reportFilename, "w")
MovementNbr = 0
start_price = 0
low_price = 0
price_swap2 = True
price_swap = True
top_price = 0
temp_top = 0
temp_lowest = 100000000000
minute_limit = timedelta(minutes=5)
spended = 0
timeElapsed = timedelta(minutes=0)
last_time_check = datetime.now()
sell_time = datetime.now()
sell_time = sell_time - timedelta(minutes=30)
highest_price = 0
highest_rsi = 0
lowest_price = 1111111111111111
sell_at_buyprice = False
sellVeryFast = False
sell_fast = False
lowest_rsi = 99

#### Email variable
##### smtplip variable
port = 465
emailPassword = config.EMAIL_PASS
emailContent = ""
finalContent = "Final Report " + sessionName + " :<br>RSI = " + str(RSI_PERIOD) + " | RSI_OVERBOUGHT = " + str(RSI_OVERBOUGHT) + " | RSI_OVERSOLD = " + str(RSI_OVERSOLD) + "<br>" + TRADE_SYMBOL + "<br>"
finalContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]opened connection<br>\
VENTE SI last_rsi < RSI_OVERSOLD<br>\
EXPRESS SELL TIME 1hrs -0.5% | 2hrs -1%<br>\
-0.5% -> +0.15% | -1% -> -0.75%<br>\
EXTREME COND 3hrs -2.5% -> -2.5%<br>\
WIN WITH RSI : +1%<br>\
WIN NO RSI : +3%<br>\
LOWESTRSI for buy<br>\
SELL_TIME + 10minutes for buy<br>\
if last_rsi > RSI_OVERBOUGHT then i = 0<br>\
LAST_RSI + 5 <= highest_rsi<br>"
mail_server = smtplib.SMTP_SSL("smtp.gmail.com", int(config.EMAIL_PORT))
final_server = smtplib.SMTP_SSL("smtp.gmail.com", port)
mail_server.login(config.EMAIL, config.EMAIL_PASS)
final_server.login(config.FINAL_EMAIL, config.FINAL_PASS)
html = """\
"""
##### imaplib variable
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(config.EMAIL, config.EMAIL_PASS)
mail.list()
mail.select('inbox')

#### Condition variable
last_buy_close = 0.0
last_sell_price = 1000000000000000
i = 0
was_closed = False
in_position = False

#### Wallet variable
walletBASE = walletUSD
balancecrypto = client.get_asset_balance(asset=symbol1)
walletETH = 0
# walletETH = float(balancecrypto['free'])

SOCKET = "wss://stream.binance.com:9443/ws/" + TRADE_SYMBOL.lower() + "@kline_1m"

def buy_writer():
    global closes, in_position, was_closed, walletUSD, walletETH, last_buy_close, i, \
    last_sell_price, close, emailContent, buy_time, symbol1, symbol2, last_time_check, minute_limit, \
    bad_trade_count, start_price, MovementNbr, timeElapsed, spended
    spended = round(walletUSD, 2)
    order_succeeded = fake_order(SIDE_BUY, close)
    # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]---------------START--------------")
    # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Buy Price : " + str(round(last_buy_close, 3)) + " " + symbol2)
    # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletETH, 4)) + " " + symbol1)
    # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(spended, 4)) + " " + symbol2.upper())

    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]---------------START--------------\n")
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Buy Price : " + str(round(last_buy_close, 3)) + " " + symbol2 + '\n')
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Lowest Price + 0.25% : " + str(round(low_price, 2)) + "\n")
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Highest Price - 0.5% :" + str(round(top_price, 2)) + "\n")
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletETH, 4)) + " " + symbol1 + "\n")
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(spended, 4)) + " " + symbol2 + "\n")
    
    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]---------------START--------------" + '<br>'
    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Buy Price : " + str(round(last_buy_close, 3)) + " " + symbol2.upper() + '<br>'
    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Lowest Price + 0.25% : " + str(round(low_price, 2)) + "<br>"
    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Highest Price - 0.5% :" + str(round(top_price, 2)) + "<br>"
    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletETH, 4)) + " " + symbol1.upper() + '<br>'
    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(spended, 4)) + " " + symbol2.upper() + "<br>"

def check_email():
    # print("Checking Email")
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(config.EMAIL, config.EMAIL_PASS)
    mail.list()
    mail.select('inbox')
    mail_subject = ""
    result, data = mail.search(None, "ALL")
    mail_ids = []
    for block in data:
        mail_ids += block.split()
    status, data = mail.fetch(mail_ids[-1], '(RFC822)')
    for response_part in data:
        if isinstance(response_part, tuple):
            message = email.message_from_bytes(response_part[1])
            mail_from = message['from']
            mail_subject = message['subject']
    if mail_subject.upper() == 'STOP ' + sessionName.upper():
        mail.store(mail_ids[-1], "+FLAGS", "\\DELETED")
        mail.expunge()
        mail.close()
        closed()
    elif mail_subject.upper() == 'SEND REPORT ' + sessionName.upper():
        mail.store(mail_ids[-1], "+FLAGS", "\\DELETED")
        mail.expunge()
        mail.close()
        send_bigreport()
    elif mail_subject.upper() == 'SEND REPORT BYPASS':
        mail.store(mail_ids[-1], "+FLAGS", "\\DELETED")
        mail.expunge()
        mail.close()
        send_bigreport()
    elif mail_subject.upper() == 'STOP ALL BYPASS':
        mail.expunge()
        mail.close()
        closed()
    else :
        mail.close()
    # mail.logout() 
    
    return

def send_bigreport():
    global finalContent, emailContent, bad_trade_count, start_time, MovementNbr, sessionName, closes, in_position, was_closed, walletUSD, walletETH, last_buy_close, i, \
    last_sell_price, close, buy_time, symbol1, symbol2, last_time_check, minute_limit, walletBASE, start_price, final_server, html, reportFilename, lowest_price, highest_price
    # newFinalContent = finalContent
    # newFinalContent += emailContent + "\n"
    Finalhtml = f"""\
    <html>
        <body>
        <FONT face="arial">
        <h3><b>{finalContent}</b></h3>
    """
    Finalhtml += html
    tailHtml = """\
    <p style="color:blue"><b>""" if round(walletUSD - walletBASE, 2) > 0 else """\
    <p style="color:orange"><b>"""
    MovementNbr += 1
    if walletUSD < 20:
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Benef: " + str(round((walletETH * float(close)) - walletBASE, 2)) + "$ | " + str(round((((walletETH * float(close)) / walletBASE) * 100) - 100, 2)) + "%<br>"
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]USDT: " + str(round(walletETH * float(close), 2)) + "$<br>"
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Total time of execution: " + str(datetime.now() - start_time).split(".")[0] + "<br>"
    else:
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Benef: " + str(round(walletUSD - walletBASE, 2)) + '$ | ' + str(round((walletUSD / walletBASE * 100) - 100, 2)) + "% <br>"
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]USDT: " + str(round(walletUSD, 2)) + '<br>'
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Total time of execution: " + str(datetime.now() - start_time).split(".")[0] + "<br>"
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Current Move: " + str(MovementNbr) + "<br>"
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Total movement: " + str(MovementNbr) + "<br>"
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Movement per hour: " + str(round(MovementNbr / ((datetime.now() - start_time).total_seconds() / 3600), 2)) + "mvt/hrs<br>"
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Win: " + str(MovementNbr - bad_trade_count) + " times | Lose: " + str(bad_trade_count) + " times<br>"
    if MovementNbr == 1:
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Start price: " + str(round(start_price, 2)) + "$<br>"
    else:
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Start price: " + str(round(start_price, 2)) + "$ | End price: " + str(round(float(close), 2)) + "$<br>"
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Difference: " + str(round(percent.percentage_diff(start_price, round(float(close), 2)), 2)) + "%<br>"
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Variation: " + str(round(percent.percentage_diff(lowest_price, highest_price), 2)) + "%<br>"
    # newFinalContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Win %: " + str(round((MovementNbr - bad_trade_count) / MovementNbr * 100, 2)) + "% | Lose %: " + str(round(bad_trade_count / MovementNbr * 100, 2)) + "%\n"
    tailHtml +="""</b></p>
        </body>
        </FONT>
    </html>"""
    Finalhtml += tailHtml
    with open(f"{reportFilename}.html", "w") as f:
        f.write(Finalhtml)
    final_server = smtplib.SMTP_SSL("smtp.gmail.com", port)
    final_server.login(config.FINAL_EMAIL, config.FINAL_PASS)
    finalEmail = MIMEMultipart('alternative')
    finalEmail['Subject'] = sessionName + ' Report'
    finalEmail['From'] = config.EMAIL
    finalEmail['To'] = config.TO_EMAIL
    finalEmail.attach(MIMEText(Finalhtml, "html"))
    final_server.send_message(finalEmail)
    final_server.close()

def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
       print("sending order")
       order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
       print(order)
    except Exception as e:
       print("an exception occured - {}".format(e))
       return False

    return True

def sendmail():
    global mail_server, emailContent, finalContent, MovementNbr
    mail_server = smtplib.SMTP_SSL("smtp.gmail.com", int(config.EMAIL_PORT))
    mail_server.login(config.EMAIL, config.EMAIL_PASS)
    email = EmailMessage()
    email['Subject'] = "Movement n°" + str(MovementNbr) + " from " + sessionName
    email['From'] = config.EMAIL
    email['To'] = config.TO_EMAIL
    email.set_content(emailContent)
    mail_server.send_message(email)
    finalContent += emailContent + '\n'
    emailContent = ""
    mail_server.close()
    # print("email has been sent")

def fake_order(side, close):
    global walletUSD, walletETH, in_position
    if side == SIDE_BUY:
        walletETH = walletUSD / float(close)
        walletUSD = 0
        in_position = True
    elif side == SIDE_SELL:
        walletUSD = walletETH * float(close)
        walletETH = 0
        in_position = False
    return True
    
def on_open(ws):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    # print("Final Report " + sessionName + " :\nRSI = " + str(RSI_PERIOD) + " | RSI_OVERBOUGHT = " + str(RSI_OVERBOUGHT) + " | RSI_OVERSOLD = " + str(RSI_OVERSOLD) + "\n" + TRADE_SYMBOL)
    # print(str(round(walletUSD, 2)))
    print("[" + datetime.now().strftime("%H:%M|%b%d") + "]opened connection")
    reportFile.write("Final Report " + sessionName + " :\nRSI = " + str(RSI_PERIOD) + " | RSI_OVERBOUGHT = " + str(RSI_OVERBOUGHT) + " | RSI_OVERSOLD = " + str(RSI_OVERSOLD) + "\n" + TRADE_SYMBOL + "\n")
    reportFile.write(str(round(walletUSD, 2)) + '\n')
    reportFile.write(\
    "VENTE SI last_rsi < RSI_OVERSOLD\
    \nEXPRESS SELL TIME 1hrs -0.5% | 2hrs -1%\
    \n-0.5% -> +0.15% | -1% -> -0.75%\
    \nEXTREME COND 3hrs -2.5% -> -2.5%\
    \nWIN WITH RSI : +1%\
    \nWIN NO RSI : +3%\
    \nLOWESTRSI for buy\
    \nSELL_TIME + 10minutes for buy\
    \nif last_rsi > RSI_OVERBOUGHT then i = 0\
    \nLAST_RSI + 5 <= highest_rsi\n")
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]opened connection\n")
    start_price = 0
    reportFile.flush()

def closed():
    global closes, in_position, was_closed, walletUSD, walletETH, last_buy_close, i, \
    last_sell_price, close, emailContent, buy_time, symbol1, symbol2, last_time_check, minute_limit, \
    bad_trade_count, start_price, MovementNbr, finalContent, html, highest_price, lowest_price
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    Finalhtml = f"""\
    <html>
        <body>
        <FONT face="arial">
        <h3><b>{finalContent}</b></h3>
    """
    final_server = smtplib.SMTP_SSL("smtp.gmail.com", port)
    final_server.login(config.FINAL_EMAIL, config.FINAL_PASS)
    if in_position == True:
        TRADE_QUANTITY = walletETH
        fake_order(SIDE_SELL, close)
        last_sell_price = float(close)
        timeElapsed = datetime.now() - buy_time
        
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletUSD, 2)) + " " + symbol2 + '\n')
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(TRADE_QUANTITY, 4)) + " " + symbol1.upper() + "\n")
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Sell Price : " + str(round(last_sell_price, 3)) + " " + symbol2 + "\n")
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]+ " + str(round(walletUSD - (TRADE_QUANTITY * last_buy_close), 2)) + "$! | + " + str(round((walletUSD - (TRADE_QUANTITY * last_buy_close)) / (TRADE_QUANTITY * last_buy_close) * 100, 2)) + "%!" + '\n')
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Begin Time : " + buy_time.strftime("%H:%M:%S") + '\n')
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "End Time : " + datetime.now().strftime("%H:%M:%S") + "\n")
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Time Elapsed : " + str(timeElapsed).split('.')[0] + '\n')
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]----------------END---------------\n\n")
        
        emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletUSD, 2)) + " " + symbol2 + '<br>'
        emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(TRADE_QUANTITY, 4)) + " " + symbol1.upper() + '<br>'
        emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Sell Price :" + str(round(last_sell_price, 3)) + " " + symbol2.upper() + "<br>"
        emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]+ " + str(round(walletUSD - (TRADE_QUANTITY * last_buy_close), 2)) + "$! | + " + str(round((walletUSD - (TRADE_QUANTITY * last_buy_close)) / (TRADE_QUANTITY * last_buy_close) * 100, 2)) + "%!" + '<br>'
        emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Begin Time : " + buy_time.strftime("%H:%M:%S") + "<br>"
        emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "End Time : " + datetime.now().strftime("%H:%M:%S") + "<br>"
        emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Time Elapsed : " + str(timeElapsed).split('.')[0] + "<br>"
        emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]----------------END---------------<br><br>"
        
        html += f"""orange">{emailContent}</p>\n"""
        emailContent = ""
        reportFile.flush()
        in_position = False
    else:
        html += """    <p style="color:"""
        html += """blue">"""
    Finalhtml = Finalhtml + html
    tailHtml = """"""
    # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]Benef: " + str(round(walletUSD, 1) - round(walletBASE, 1)))
    # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]USDT: " + str(round(walletUSD, 1)))
    reportFile.write("\n[" + datetime.now().strftime("%H:%M|%b%d") + "]Benef: " + str(round(walletUSD - walletBASE, 2)) + '$ | ' + str(round((walletUSD / walletBASE * 100) - 100, 2)) + "% \n")
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]USDT: " + str(round(walletUSD, 2)) + '$\n')    
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Total time of execution: " + str(datetime.now() - start_time).split(".")[0] + "\n")
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Total movement: " + str(MovementNbr) + "\n")
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Movement per hour: " + str(round(MovementNbr / ((datetime.now() - start_time).total_seconds() / 3600), 2)) + "mvt/hrs\n")
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Win: " + str(MovementNbr - bad_trade_count) + " times | Lose: " + str(bad_trade_count) + " times\n")
    # reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Win %: " + str(round((MovementNbr - bad_trade_count) / MovementNbr * 100, 2)) + "% | Lose %: " + str(round(bad_trade_count / MovementNbr * 100, 2)) + "%\n")
    # finalContent += emailContent + '\n' 
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Benef: " + str(round(walletUSD - walletBASE, 2)) + '$ | ' + str(round((walletUSD / walletBASE * 100) - 100, 2)) + "% <br>"
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]USDT: " + str(round(walletUSD, 2)) + '$<br>'
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Total time of execution: " + str(datetime.now() - start_time).split(".")[0] + "<br>"
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Total movement: " + str(MovementNbr) + "<br>"
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Movement per hour: " + str(round(MovementNbr / ((datetime.now() - start_time).total_seconds() / 3600), 2)) + "mvt/hrs<br>"
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Win: " + str(MovementNbr - bad_trade_count) + " times | Lose: " + str(bad_trade_count) + " times<br>"
    if MovementNbr <= 1:
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Start price: " + str(round(start_price, 2)) + "$<br>"
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Start price: " + str(round(start_price, 2)) + "$\n")
    else:
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Start price: " + str(round(start_price, 2)) + "$ | End price: " + str(round(float(close), 2)) + "$<br>"
        tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Difference: " + str(round(percent.percentage_diff(start_price, round(float(close), 2)), 2)) + "%<br>"
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Start price: " + str(round(start_price, 2)) + "$ | End price: " + str(round(float(close), 2)) + "$\n")
        reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Difference: " + str(round(percent.percentage_diff(start_price, round(float(close), 2)), 2)) + "%\n")
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Variation: " + str(round(percent.percentage_diff(lowest_price, highest_price), 2)) + "%<br>"
    tailHtml += "[" + datetime.now().strftime("%H:%M|%b%d") + "]closed connection<br>"
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Variation: " + str(round(percent.percentage_diff(lowest_price, highest_price), 2)) + "%\n")
    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]closed connection\n")
    # mail_server.login(config.EMAIL, config.EMAIL_PASS)
    tailHtml +="""</b></p>
        </body>
        </FONT>
    </html>"""
    Finalhtml += tailHtml
    with open(f"{reportFilename}.html", "w") as f:
        f.write(Finalhtml)
    finalEmail = MIMEMultipart('alternative')
    finalEmail['Subject'] = 'Final Report ' + sessionName
    finalEmail['From'] = config.EMAIL
    finalEmail['To'] = config.TO_EMAIL
    finalEmail.attach(MIMEText(Finalhtml, "html"))
    final_server.send_message(finalEmail)
    final_server.close()
    reportFile.flush()
    exit()

def on_close(ws):
    closed()

def on_message(ws, message):
    global closes, in_position, was_closed, walletUSD, walletETH, last_buy_close, i, \
    last_sell_price, close, emailContent, buy_time, symbol1, symbol2, last_time_check, minute_limit, \
    bad_trade_count, start_price, low_price, temp_lowest, price_swap, price_swap2, temp_top, top_price, \
    sell_time, MovementNbr, timeElapsed, spended, html, highest_price, lowest_price, highest_rsi, sell_at_buyprice, sell_fast, lowest_rsi, sellVeryFast, dataFile

    dataFile.write(message)
    dataFile.flush()
    #### Retrieving informations from the websocket given in JSON format
    json_message = json.loads(message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    ticker = client.get_ticker(symbol=TRADE_SYMBOL)
    # top_price = float(ticker["highPrice"])
    # top_price = top_price - percent.percentage(0.25, top_price)
    close = candle['c']
    if start_price == 0:
        start_price = float(close)
    if top_price == 0:
        top_price = float(ticker["highPrice"])
        top_price = top_price - percent.percentage(0.75, top_price)
    elif float(close) - percent.percentage(0.75, float(close)) > top_price:
        top_price = float(close)
        top_price = top_price - percent.percentage(0.75, top_price)
    elif len(closes) == 300 and price_swap2:
        top_price = temp_top
        top_price = top_price - percent.percentage(0.75, top_price)
        price_swap2 = False
    if float(close) > temp_top:
        temp_top = float(close)
    if low_price == 0:
        low_price = float(ticker["lowPrice"])
        low_price = low_price + percent.percentage(0.25, low_price)
    elif float(close) + percent.percentage(0.25, float(close)) < low_price:
        low_price = float(close)
        low_price = low_price + percent.percentage(0.25, low_price)
    elif len(closes) == 300 and price_swap:
        low_price = temp_lowest
        low_price = low_price + percent.percentage(0.25, low_price)
        price_swap = False
    elif float(close) < temp_lowest:
        temp_lowest = float(close)
    if last_time_check + minute_limit < datetime.now():
        check_email()
        last_time_check = datetime.now()
    # check_email()
    percentage = percent.percentage(1, last_buy_close)
    high = candle['h']
    # balancecrypto = client.get_asset_balance(asset=symbol1)
    # walletETH = float(balancecrypto['free'])
    if float(close) > highest_price:
        highest_price = float(close)
    if float(close) < lowest_price:
        lowest_price = float(close)
    
    #### Append a value in the closes array when a candle closes 
    #### Otherwise it's updating the last value of the array to the current value
    if was_closed:
        closes.append(float(close))
    else:
        closes[-1] = float(close)
    #### Condition to exit the program when a certain amount has been lost or win
    # if walletUSD > 50 and walletUSD <= walletBASE - 150:
    #     closed()
    # if walletUSD - walletBASE >= percent.percentage(3, walletBASE):
    #     closed()
    # if walletUSD > walletBASE + 500:
    #     closed()
    #### Handling the fact that there is no value in the aray at the beggining
    if len(closes) > RSI_PERIOD:
        
        #### Calculate using the talib the RSI based on the values we got before
        np_closes = numpy.array(closes)
        rsi = talib.RSI(np_closes, RSI_PERIOD)
        last_rsi = rsi[-1]
########################################################################################################################################################################
############################################################################## LOSE NO RSI #############################################################################
########################################################################################################################################################################
        if not in_position:
            sell_at_buyprice = False
            sell_fast = False
            sellVeryFast = False
        if in_position and float(close) <= last_buy_close - percent.percentage(0.5, last_buy_close) and buy_time + timedelta(hours=1) <= datetime.now():
            sell_at_buyprice = True
        if in_position and float(close) <= last_buy_close - percent.percentage(1, last_buy_close) and buy_time + timedelta(hours=2) <= datetime.now():
            sell_fast = True
        if in_position and float(close) <= last_buy_close - percent.percentage(2.5, last_buy_close) and buy_time + timedelta(hours=5) <= datetime.now():
            sellVeryFast = True
        if last_rsi < RSI_OVERSOLD and \
        ((in_position and sell_at_buyprice and float(close) >= (last_buy_close + percent.percentage(0.15, last_buy_close))) or\
        (in_position and sell_fast and float(close) >= last_buy_close - percent.percentage(0.75, last_buy_close)) or\
        (in_position and sellVeryFast)):
            TRADE_QUANTITY = walletETH
            last_sell_price = float(close)
            bad_trade_count += 1
            order_succeeded = fake_order(SIDE_SELL, close)
            timeElapsed = datetime.now() - buy_time
            sell_time = datetime.now()
            sell_at_buyprice = False
            sellVeryFast = False
            sell_fast = False
            html += """    <p style="color:"""
            
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletUSD, 2)) + " " + symbol2.upper() + "\n")
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(TRADE_QUANTITY, 4)) + " " + symbol1.upper() + "\n")
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Sell Price : " + str(round(last_sell_price, 3)) + " " + symbol2.upper() + "\n")
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]- " + str(round((last_buy_close * float(TRADE_QUANTITY)) - walletUSD, 2)) + "$! | - " + str(round(((last_buy_close * float(TRADE_QUANTITY)) - walletUSD) / (TRADE_QUANTITY * last_buy_close) * 100, 2)) + "%!" + '\n')
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Begin Time : " + buy_time.strftime("%H:%M:%S") + '\n')
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "End Time : " + datetime.now().strftime("%H:%M:%S") + "\n")
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Time Elapsed : " + str(timeElapsed).split('.')[0] + '\n')
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]-------------END-LOSE------------\n\n")
            
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletUSD, 2)) + " " + symbol2 + '<br>'
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(TRADE_QUANTITY, 4)) + " " + symbol1.upper() + '<br>'
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Sell Price :" + str(round(last_sell_price, 3)) + " " + symbol2.upper() + "<br>"
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]- " + str(round((last_buy_close * float(TRADE_QUANTITY)) - walletUSD, 2)) + "$! | - " + str(round(((last_buy_close * float(TRADE_QUANTITY)) - walletUSD) / (TRADE_QUANTITY * last_buy_close) * 100, 2)) + "%!" + '<br>'
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Begin Time : " + buy_time.strftime("%H:%M:%S") + "<br>"
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "End Time : " + datetime.now().strftime("%H:%M:%S") + "<br>"
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Time Elapsed : " + str(timeElapsed).split('.')[0] + "<br>"
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]--------------END-LOSE------------<br><br>"
            
            html += f"""red">{emailContent}</p>\n"""
            emailContent = ""
            
            send_bigreport()
            reportFile.flush()
            in_position = False
            return
########################################################################################################################################################################
############################################################################## WIN NO RSI ##############################################################################
########################################################################################################################################################################
        if in_position and float(close) > last_buy_close + percent.percentage(3, last_buy_close):
            # balancecrypto = client.get_asset_balance(asset=symbol1)
            # walletETH = float(balancecrypto['free'])
            TRADE_QUANTITY = walletETH
            last_sell_price = float(close)
            order_succeeded = fake_order(SIDE_SELL, close)
            timeElapsed = datetime.now() - buy_time
            sell_time = datetime.now()
            # walletUSD = walletETH * round(float(close), 2)
            html += """    <p style="color:"""
            
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletUSD, 2)) + " " + symbol2 + '\n')
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(TRADE_QUANTITY, 4)) + " " + symbol1.upper() + "\n")
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Sell Price : " + str(round(last_sell_price, 3)) + " " + symbol2 + "\n")
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]+ " + str(round(walletUSD - (TRADE_QUANTITY * last_buy_close), 2)) + "$! | + " + str(round((walletUSD - (TRADE_QUANTITY * last_buy_close)) / (TRADE_QUANTITY * last_buy_close) * 100, 2)) + "%!" + '\n')
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Begin Time : " + buy_time.strftime("%H:%M:%S") + '\n')
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "End Time : " + datetime.now().strftime("%H:%M:%S") + "\n")
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Time Elapsed : " + str(timeElapsed).split('.')[0] + '\n')
            reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]--------------END-WIN-------------\n\n")
            
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletUSD, 2)) + " " + symbol2 + '<br>'
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(TRADE_QUANTITY, 4)) + " " + symbol1.upper() + '<br>'
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Sell Price : " + str(round(last_sell_price, 3)) + " " + symbol2.upper() + "<br>"
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]+ " + str(round(walletUSD - (TRADE_QUANTITY * last_buy_close), 2)) + "$! | + " + str(round((walletUSD - (TRADE_QUANTITY * last_buy_close)) / (TRADE_QUANTITY * last_buy_close) * 100, 2)) + "%!" + '<br>'
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Begin Time : " + buy_time.strftime("%H:%M:%S") + '<br>'
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "End Time : " + datetime.now().strftime("%H:%M:%S") + "<br>"
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Time Elapsed : " + str(timeElapsed).split('.')[0] + '<br>'
            emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]--------------END-WIN-------------<br><br>"
            
            html += f"""green">{emailContent}</p>\n"""
            emailContent = ""
            
            send_bigreport()
            reportFile.flush()
            in_position = False
            return
########################################################################################################################################################################
############################################################################## WIN WITH RSI ############################################################################
########################################################################################################################################################################
        if last_rsi >= RSI_OVERBOUGHT:
            if in_position and float(close) >= last_buy_close + percent.percentage(0.75, last_buy_close):
                if last_rsi > highest_rsi:
                    highest_rsi = last_rsi
                if last_rsi + 5 < highest_rsi:
                    # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]Overbought! Sell! Sell! Sell!")
                    # emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Overbought! Sell! Sell! Sell!" + '\n'
                    # print(last_buy_close)
                    # balancecrypto = client.get_asset_balance(asset=symbol1)
                    # walletETH = float(balancecrypto['free'])
                    highest_rsi = 0
                    TRADE_QUANTITY = walletETH
                    last_sell_price = float(close)
                    order_succeeded = fake_order(SIDE_SELL, close)
                    timeElapsed = datetime.now() - buy_time
                    sell_time = datetime.now()
                    # walletUSD = walletETH * round(float(close), 2)
                    html += """    <p style="color:"""
                    
                    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletUSD, 2)) + " " + symbol2 + '\n')
                    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(TRADE_QUANTITY, 4)) + " " + symbol1.upper() + "\n")
                    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Sell Price : " + str(round(last_sell_price, 3)) + " " + symbol2 + "\n")
                    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]+ " + str(round(walletUSD - (TRADE_QUANTITY * last_buy_close), 2)) + "$! | + " + str(round((walletUSD - (TRADE_QUANTITY * last_buy_close)) / (TRADE_QUANTITY * last_buy_close) * 100, 2)) + "%!" + '\n')
                    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Begin Time : " + buy_time.strftime("%H:%M:%S") + '\n')
                    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "End Time : " + datetime.now().strftime("%H:%M:%S") + "\n")
                    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Time Elapsed : " + str(timeElapsed).split('.')[0] + '\n')
                    reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]--------------END-WIN-------------\n\n")
                    
                    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletUSD, 2)) + " " + symbol2 + '<br>'
                    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(TRADE_QUANTITY, 4)) + " " + symbol1.upper() + '<br>'
                    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Sell Price : " + str(round(last_sell_price, 3)) + " " + symbol2.upper() + "<br>"
                    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]+ " + str(round(walletUSD - (TRADE_QUANTITY * last_buy_close), 2)) + "$! | + " + str(round((walletUSD - (TRADE_QUANTITY * last_buy_close)) / (TRADE_QUANTITY * last_buy_close) * 100, 2)) + "%!" + '<br>'
                    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Begin Time : " + buy_time.strftime("%H:%M:%S") + '<br>'
                    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "End Time : " + datetime.now().strftime("%H:%M:%S") + "<br>"
                    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Time Elapsed : " + str(timeElapsed).split('.')[0] + '<br>'
                    emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]--------------END-WIN-------------<br><br>"
                    
                    html += f"""green">{emailContent}</p>\n"""
                    emailContent = ""
                    send_bigreport()
                    reportFile.flush()
                    in_position = False
                    return
            else:
                i = 0
                # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]It is overbought, but we don't own any or price is under " + str(last_buy_close + (percentage / 2)) + ". Nothing to do.")
        #### Reset the i counter if the RSI goes too high after not being low long enough to place an order
        if last_rsi > RSI_OVERBOUGHT:
            i = 0
        #### If the RSI is less than the limit given by the user
        if (last_rsi < RSI_OVERSOLD or float(close) <= low_price) and sell_time < datetime.now() - timedelta(minutes=10):
            #### If we don't own crypto and the i counter is greater than the hard-coded value
            #### it means that the RSI has been i times under the limit given by the user and not
            #### higher than the value defined in the previous condition
            if in_position:
                i = i
                # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]It is oversold, but you already own it, nothing to do.")
            else:
                # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]Oversold! Buy! Buy! Buy! " + str(i) + " " + str(last_buy_close + percentage))
                i += 1
                # reportFile.write(str(i) + '\n')
                # print(i)
########################################################################################################################################################################
############################################################################## BUY WITH RSI ############################################################################
########################################################################################################################################################################
                if (i > 300 and float(close) <= top_price) or float(close) <= low_price: #and float(close) <= top_price:
                    if last_rsi < lowest_rsi:
                        lowest_rsi = last_rsi
                    if last_rsi - 5 >= lowest_rsi:
                        TRADE_QUANTITY = round(walletUSD,2) / round(float(close), 2)
                        last_buy_close = float(close)
                        buy_time = datetime.now()
                        lowest_rsi = 99
                        # spended = round(walletUSD, 2)
                        # order_succeeded = fake_order(SIDE_BUY, close)
                        # # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]---------------START--------------")
                        # # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Buy Price : " + str(round(last_buy_close, 3)) + " " + symbol2)
                        # # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletETH, 4)) + " " + symbol1)
                        # # print("[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(spended, 4)) + " " + symbol2.upper())
                        
                        # reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]---------------START--------------\n")
                        # reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Buy Price : " + str(round(last_buy_close, 3)) + " " + symbol2 + '\n')
                        # reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Lowest Price + 0.25% : " + str(round(low_price, 2)) + "\n")
                        # reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Highest Price - 0.5% :" + str(round(top_price, 2)) + "\n")
                        # reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletETH, 4)) + " " + symbol1 + "\n")
                        # reportFile.write("[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(spended, 4)) + " " + symbol2 + "\n")
                        
                        # emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]---------------START--------------" + '\n'
                        # emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]" + "Buy Price : " + str(round(last_buy_close, 3)) + " " + symbol2.upper() + '\n'
                        # emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Lowest Price + 0.25% : " + str(round(low_price, 2)) + "\n"
                        # emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Highest Price - 0.5% :" + str(round(top_price, 2)) + "\n"
                        # emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Owned : " + str(round(walletETH, 4)) + " " + symbol1.upper() + '\n'
                        # emailContent += "[" + datetime.now().strftime("%H:%M|%b%d") + "]Spend : " + str(round(spended, 4)) + " " + symbol2.upper() + "\n"
                        # balancecrypto = client.get_asset_balance(asset=symbol1)
                        # walletETH = float(balancecrypto['free'])
                        # summary_update()
                        
                        buy_writer()
                        highest_rsi = 0
                        reportFile.flush()
                        in_position = True
                        i = 0

    was_closed = is_candle_closed
                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_close)
ws.run_forever()
if websocket.WebSocketConnectionClosedException:
    reportFile.write("CONNECTION ERROR")

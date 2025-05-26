Stellar Trading Bot
This is a simple Python script (buybot.py) that automates buying and selling a specific asset (e.g., LMNR) with XLM on the Stellar network. It’s designed for beginners, using a configuration file (.env) to set up trading parameters. This guide provides step-by-step instructions to set up and run the bot on Windows, even if you’ve never used a command terminal or coded before.
What the Bot Does

Buys and Sells Assets: Alternates between buying and selling a chosen asset (e.g., LMNR) with XLM at set intervals.
Configurable: Uses a .env file to specify the asset, trade amounts, timing, and buy/sell cycle.
Keypair Generator: Includes newwallet.py to create a Stellar account.
Logs Trades: Displays balances and trade results in the terminal for easy monitoring.

Important Notes

Funds: Your Stellar account needs at least 2.5 XLM (2 XLM for reserves, ~0.5 XLM for fees and trades). Add more XLM for larger trades.
Liquidity: The asset (e.g., LMNR) must have active buy/sell offers on Stellar’s decentralized exchange (check on StellarExpert).
Safety: Keep your .env file and stellar_keypair.txt secure, as they contain your Stellar secret key. Never share them.
Stopping the Bot: Press Ctrl+C in the terminal to stop the bot.

Requirements

Windows 10 or 11.
Internet connection.
A Stellar account with a secret key and XLM (you’ll create one).

Step-by-Step Setup Instructions
1. Install Git
Git is needed to download the bot from GitHub.

Download Git:
Open your web browser and go to git-scm.com/download/win.
Click the “64-bit Git for Windows Setup” link to download the .exe file.
Save it to your Downloads folder.


Install Git:
Double-click the downloaded .exe file.
Click “Next” through the prompts, accepting default settings.
When asked about “Adjusting your PATH environment,” select “Git from the command line and also from 3rd-party software.”
Click “Install”, then “Finish”.


Verify Installation:
Press Win + S, type “cmd”, and press Enter to open Command Prompt.
Type git --version and press Enter. You should see git version 2.x.x.
Close Command Prompt.



2. Install Python
Python is required to run the bot.

Download Python:
Go to python.org/downloads.
Click the yellow “Download Python 3.13.x” button (or the latest 3.x version).
Save the .exe file to your Downloads folder.


Install Python:
Double-click the downloaded .exe file.
Check the box “Add Python to PATH” at the bottom of the installer window.
Click “Install Now” and wait for the installation to complete.
Click “Close” when done.


Verify Installation:
Open Command Prompt (press Win + S, type “cmd”, press Enter).
Type python --version and press Enter. You should see Python 3.13.x.
Type pip --version and press Enter to confirm pip is installed.
Close Command Prompt.



3. Install Visual Studio Code (VS Code)
VS Code is a free code editor to edit and run the bot.

Download VS Code:
Go to code.visualstudio.com.
Click “Download for Windows” and save the .exe file.


Install VS Code:
Double-click the downloaded .exe file.
Accept the license agreement and click “Next” through the prompts.
Check “Add to PATH” and “Register Code as an editor for supported file types”.
Click “Install”, then “Finish”.


Install Python Extension:
Open VS Code (search “Visual Studio Code” in the Start menu).
Click the Extensions icon on the left sidebar (square with four squares).
Search for “Python” and click “Install” on the “Python” extension by Microsoft.



4. Clone the Bot from GitHub
The bot is hosted on GitHub. You’ll download it to your computer.

Create a Project Folder:
Open File Explorer (Win + E) and navigate to C:\Users\YourUsername.
Right-click, select “New > Folder”, and name it BUYBOT.


Clone the Repository:
Open Command Prompt (press Win + S, type “cmd”, press Enter).
Navigate to your folder by typing:cd C:\Users\YourUsername\BUYBOT

Replace YourUsername with your Windows username.
Type the following command and press Enter:git clone https://github.com/lumenbro/buybot.git

(Replace yourusername with the actual GitHub username hosting the repository.)
Wait for the download to complete. You’ll see files appear in C:\Users\YourUsername\BUY BOT\buybot


Move Files (if needed):
If you want files directly in C:\Users\YourUsername\BUYBOT, move the contents of C:\Users\YourUsername\BUY BOT\stellar-trading-bot to C:\Users\YourUsername\BUYBOT.
In File Explorer, open C:\Users\YourUsername\BUYBOT\stellar-trading-bot, select all files (Ctrl+A), cut (Ctrl+X), go to C:\Users\YourUsername\BUYBOT, and paste (Ctrl+V).
Delete the empty buybot folder.



5. Generate a Stellar Keypair
You need a Stellar account to run the bot. Use newwallet.py to create one.

Open VS Code:
Open VS Code and click File > Open Folder.
Select C:\Users\YourUsername\BUY BOT.


Run newwallet.py:
In VS Code, click Terminal > New Terminal.
Ensure the terminal shows C:\Users\YourUsername\BUY BOT>.
Type:python newwallet.py

Press Enter. You’ll see output like:New Stellar Wallet Keypair Generated:
Public Key: GA123...
Secret Key: SB123...
WARNING: Save your secret key securely! Do NOT share it.
Keypair saved to 'stellar_keypair.txt'




Save the Keypair:
Open stellar_keypair.txt in C:\Users\YourUsername\BUY BOT (double-click in VS Code’s Explorer).
Copy the Secret Key (starts with S, 56 characters).
Store it securely (e.g., in a password manager).
Note the Public Key (starts with G) for funding.



6. Configure the Bot

Edit .env File:
In VS Code, double-click .env in C:\Users\YourUsername\BUY BOT. If .env doesn’t exist, create it:
Right-click in the Explorer pane, select “New File,” and name it .env.

*NOTE: SEE .envexample FOR CORRECT .env FORMAT TO POPULATE YOUR OWN VARIABLES* (readme.md screws up the format here)


Copy and paste the following template into .env:
```SECRET_KEY=your_secret_key_here
ASSET_CODE=LMNR
ASSET_ISSUER=GALUVE2YREE6NU4T2746XL7XORCEY5NVDJ7WADGWANUZWQJZ3PTP5PHB
TRADE_INTERVAL=30
BUY_ASSET_AMOUNT=100
SELL_ASSET_AMOUNT=100
BUY_SELL_CYCLE=1```


Alternatively, if an .env.example file is provided, copy it, rename the copy to .env, and edit it.
Update the following fields:
```SECRET_KEY: Paste your secret key from stellar_keypair.txt.
ASSET_CODE: The asset to trade (e.g., LMNR).
ASSET_ISSUER: The asset issuer’s public key (e.g., for LMNR).
TRADE_INTERVAL: Seconds between trades (e.g., 30).
BUY_ASSET_AMOUNT: Amount of the asset to buy per trade (e.g., 100 LMNR).
SELL_ASSET_AMOUNT: Amount of the asset to sell per trade (e.g., 100 LMNR).
BUY_SELL_CYCLE: Controls the buy/sell pattern:
1: Buy, sell, buy, sell (alternating).
2: Buy, buy, sell, buy, buy, sell.
0: Sell only (no buys).
-1: Buy only (no sells).```




Save the file (Ctrl+S).



7. Install Dependencies

Open Terminal in VS Code:
Click Terminal > New Terminal.
Ensure the terminal shows C:\Users\YourUsername\BUY BOT>.


Install Dependencies:
Type:pip install -r requirements.txt

Press Enter. Wait for the installation to complete.



8. Fund Your Stellar Account

Fund with XLM:
Send at least 2.5 XLM to your public key (from stellar_keypair.txt) via an exchange (e.g., Coinbase, Binance) or wallet (e.g., Lobstr).
Verify funding on StellarExpert by entering your public key.


Check Liquidity:
On StellarExpert, search for your asset (e.g., LMNR-GALUVE...).
Ensure the XLM/LMNR (buy) and LMNR/XLM (sell) order books have offers for at least 100 LMNR.



9. Run the Bot

Start the Bot:
In VS Code’s terminal (C:\Users\YourUsername\BUY BOT), type:python buybot.py

Press Enter. You’ll see logs like:INFO:__main__:Loaded environment variables:
INFO:__main__:SECRET_KEY: SBHD... (hidden for security)
INFO:__main__:ASSET_CODE: LMNR
...
INFO:__main__:Buy successful: <transaction_hash>




Monitor Trades:
The bot logs balances and trades every 30 seconds.
Trades follow the BUY_SELL_CYCLE (e.g., buy, sell for 1; buy, buy, sell for 2; sell only for 0; buy only for -1).
If trades fail (e.g., “No paths found”), check liquidity on StellarExpert.



10. Stop the Bot

Press Ctrl+C in the terminal. You’ll see:INFO:__main__:Bot stopped by user.



Troubleshooting

“No paths found” Error:
Check XLM/LMNR and LMNR/XLM liquidity on StellarExpert.
Add buy/sell offers using a wallet or reduce BUY_ASSET_AMOUNT/SELL_ASSET_AMOUNT in .env (e.g., to 10).


“Insufficient XLM” Error:
Send more XLM to your public key (aim for 5 XLM total).


Command Not Found:
Ensure Python and Git are added to PATH (reinstall with “Add to PATH” checked).
Verify you’re in C:\Users\YourUsername\BUY BOT in the terminal.


Need Help?
Contact the bot provider with your terminal logs.



Files Included

buybot.py: The main bot script.
newwallet.py: Generates a Stellar keypair.
requirements.txt: Lists required Python libraries.
.env: Configuration file for your settings (create this).
.env.example: Template for .env (optional, copy and rename to .env).
README.md: This guide.
.gitignore: Excludes sensitive files (e.g., stellar_keypair.txt).

Safety Reminder

Secret Key: Store .env and stellar_keypair.txt securely. If compromised, someone could access your Stellar account.
Backup: Save your secret key in a safe place (e.g., password manager).
Liquidity: Ensure the asset has enough trading activity to avoid failed trades.




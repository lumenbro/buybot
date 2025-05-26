import os
import time
from dotenv import load_dotenv
from stellar_sdk import Keypair, Asset, Network, TransactionBuilder, Server, ChangeTrust, PathPaymentStrictReceive, PathPaymentStrictSend, Account
from stellar_sdk.client.requests_client import RequestsClient
from decimal import Decimal
import logging

# Set up logging to display info in the console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeBot:
    def __init__(self):
        # Load settings from .env file
        load_dotenv()
        self.secret_key = os.getenv("SECRET_KEY")
        self.asset_code = os.getenv("ASSET_CODE")
        self.asset_issuer = os.getenv("ASSET_ISSUER")
        self.trade_interval = os.getenv("TRADE_INTERVAL")
        self.buy_asset_amount = os.getenv("BUY_ASSET_AMOUNT")
        self.sell_asset_amount = os.getenv("SELL_ASSET_AMOUNT")
        self.buy_sell_cycle = os.getenv("BUY_SELL_CYCLE")
        
        # Debug: Print environment variables
        logger.info("Loaded environment variables:")
        logger.info(f"SECRET_KEY: {self.secret_key[:4]}... (hidden for security)")
        logger.info(f"ASSET_CODE: {self.asset_code}")
        logger.info(f"ASSET_ISSUER: {self.asset_issuer}")
        logger.info(f"TRADE_INTERVAL: {self.trade_interval}")
        logger.info(f"BUY_ASSET_AMOUNT: {self.buy_asset_amount}")
        logger.info(f"SELL_ASSET_AMOUNT: {self.sell_asset_amount}")
        logger.info(f"BUY_SELL_CYCLE: {self.buy_sell_cycle}")
        
        # Validate inputs
        if not self.secret_key:
            raise ValueError("SECRET_KEY not found in .env file.")
        if not self.asset_code or not self.asset_issuer:
            raise ValueError("ASSET_CODE or ASSET_ISSUER not found in .env file.")
        try:
            self.trade_interval = int(self.trade_interval)
            self.buy_asset_amount = float(self.buy_asset_amount)
            self.sell_asset_amount = float(self.sell_asset_amount)
            self.buy_sell_cycle = int(self.buy_sell_cycle) if self.buy_sell_cycle is not None else 1
            if self.buy_sell_cycle < -1:  # Allow -1 for buy-only
                raise ValueError("BUY_SELL_CYCLE must be -1 (buy-only), 0 (sell-only), or a positive number.")
        except (TypeError, ValueError) as e:
            raise ValueError(f"TRADE_INTERVAL, BUY_ASSET_AMOUNT, SELL_ASSET_AMOUNT, and BUY_SELL_CYCLE must be numbers. Error: {str(e)}")
        
        # Initialize Stellar SDK
        self.keypair = Keypair.from_secret(self.secret_key)
        self.public_key = self.keypair.public_key
        self.horizon_url = "https://horizon.stellar.org"
        self.server = Server(horizon_url=self.horizon_url, client=RequestsClient())
        self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
        self.asset = Asset(self.asset_code, self.asset_issuer)
        
        logger.info(f"Starting Trade Bot for {self.asset_code}")
        logger.info(f"Buy Amount: {self.buy_asset_amount} {self.asset_code} per buy trade (paid with XLM)")
        logger.info(f"Sell Amount: {self.sell_asset_amount} {self.asset_code} per sell trade (converted to XLM)")
        logger.info(f"Trade Interval: Every {self.trade_interval} seconds")
        if self.buy_sell_cycle == -1:
            logger.info("Cycle: Buy-only mode (no sells)")
        elif self.buy_sell_cycle == 0:
            logger.info("Cycle: Sell-only mode (no buys)")
        else:
            logger.info(f"Cycle: {self.buy_sell_cycle} buy trade(s) followed by one sell trade")

    def run(self):
        cycle_count = 0
        while True:
            try:
                self.log_balances()
                if self.buy_sell_cycle == -1:
                    self.perform_buy()  # Buy-only mode
                elif self.buy_sell_cycle == 0:
                    self.perform_sell()  # Sell-only mode
                elif cycle_count < self.buy_sell_cycle:
                    self.perform_buy()
                    cycle_count += 1
                else:
                    self.perform_sell()
                    cycle_count = 0
            except Exception as e:
                logger.error(f"Trade failed: {str(e)}")
                time.sleep(10)  # Wait before retrying
            time.sleep(self.trade_interval)

    def perform_buy(self):
        native_asset = Asset.native()
        public_key = self.public_key
        account = self.load_account(public_key)

        # Check and create trustline if needed
        if not self.has_trustline(account, self.asset):
            logger.info(f"Adding trustline for {self.asset_code}:{self.asset_issuer}")
            available_xlm = self.calculate_available_xlm(account)
            if available_xlm < 0.6:  # 0.5 for trustline + 0.1 for fee
                raise ValueError(f"Insufficient XLM for trustline: need 0.6 XLM, available {available_xlm:.7f}")
            operations = [ChangeTrust(asset=self.asset, limit="1000000000.0")]
            response = self.build_and_submit_transaction(account, operations, memo=f"Add Trust {self.asset_code}")
            logger.info(f"Trustline created: {response['hash']}")
            account = self.load_account(public_key)

        available_xlm = self.calculate_available_xlm(account)
        dest_amount = Decimal(str(self.buy_asset_amount)).quantize(Decimal('0.0000001'))
        dest_amount_str = format(dest_amount, 'f')
        if float(dest_amount) <= 0:
            raise ValueError(f"Invalid buy amount: {dest_amount}")

        # Find paths (simplified from trade_services.py)
        paths_response = self.server.strict_receive_paths(
            source=[native_asset],
            destination_asset=self.asset,
            destination_amount=dest_amount_str
        ).limit(10).call()
        paths = paths_response.get("_embedded", {}).get("records", [])
        if not paths:
            raise ValueError(f"No paths found to buy {dest_amount} {self.asset_code}. Check liquidity for XLM/{self.asset_code} on StellarExpert.")

        # Log available paths
        for path in paths:
            logger.info(f"Path found: {path['source_amount']} XLM for {dest_amount} {self.asset_code} (hops: {len(path['path'])})")

        # Select path with lowest source amount
        selected_path = min(paths, key=lambda p: float(p["source_amount"]))
        max_source_amount = Decimal(selected_path["source_amount"])
        slippage = Decimal('0.05')  # 5% slippage
        max_source_amount_with_slippage = (max_source_amount * (1 + slippage)).quantize(Decimal('0.0000001'))
        max_source_amount_str = format(max_source_amount_with_slippage, 'f')

        if max_source_amount_with_slippage > available_xlm:
            raise ValueError(f"Insufficient XLM: need {max_source_amount_with_slippage:.7f}, available {available_xlm:.7f}")

        # Build and submit transaction with empty path
        operations = [
            PathPaymentStrictReceive(
                send_asset=native_asset,
                send_max=max_source_amount_str,
                destination=public_key,
                dest_asset=self.asset,
                dest_amount=dest_amount_str,
                path=[]  # Let Stellar DEX find the best path
            )
        ]
        response = self.build_and_submit_transaction(account, operations, memo=f"Buy {self.asset_code}")
        logger.info(f"Buy successful: {response['hash']}")

    def perform_sell(self):
        native_asset = Asset.native()
        public_key = self.public_key
        account = self.load_account(public_key)

        # Check balance
        balance = float(next((b["balance"] for b in account["balances"] if b.get("asset_code") == self.asset_code and b.get("asset_issuer") == self.asset_issuer), "0"))
        send_amount = min(self.sell_asset_amount, balance)
        send_amount = Decimal(str(send_amount)).quantize(Decimal('0.0000001'))
        send_amount_str = format(send_amount, 'f')
        if float(send_amount) <= 0:
            raise ValueError(f"No {self.asset_code} available to sell. Balance: {balance} {self.asset_code}")

        # Find paths (simplified from trade_services.py)
        paths_response = self.server.strict_send_paths(
            source_asset=self.asset,
            source_amount=send_amount_str,
            destination=[native_asset]
        ).limit(10).call()
        paths = paths_response.get("_embedded", {}).get("records", [])
        if not paths:
            raise ValueError(f"No paths found to sell {send_amount} {self.asset_code}. Check liquidity for {self.asset_code}/XLM on StellarExpert.")

        # Log available paths
        for path in paths:
            logger.info(f"Path found: {send_amount} {self.asset_code} for {path['destination_amount']} XLM (hops: {len(path['path'])})")

        # Select path with highest destination amount
        selected_path = max(paths, key=lambda p: float(p["destination_amount"]))
        max_dest_amount = Decimal(selected_path["destination_amount"])
        slippage = Decimal('0.05')  # 5% slippage
        min_dest_amount = (max_dest_amount * (1 - slippage)).quantize(Decimal('0.0000001'))
        min_dest_amount_str = format(min_dest_amount, 'f')

        # Build and submit transaction with empty path
        operations = [
            PathPaymentStrictSend(
                send_asset=self.asset,
                send_amount=send_amount_str,
                destination=public_key,
                dest_asset=native_asset,
                dest_min=min_dest_amount_str,
                path=[]  # Let Stellar DEX find the best path
            )
        ]
        response = self.build_and_submit_transaction(account, operations, memo=f"Sell {self.asset_code}")
        logger.info(f"Sell successful: {response['hash']}")

    def build_and_submit_transaction(self, account, operations, memo=None):
        sequence = int(account["sequence"])
        base_fee = max(self.get_recommended_fee(), 200 * len(operations))

        tx_builder = TransactionBuilder(
            source_account=Account(self.public_key, sequence),
            network_passphrase=self.network_passphrase,
            base_fee=base_fee
        ).add_time_bounds(0, int(time.time()) + 900)
        
        for op in operations:
            tx_builder.append_operation(op)
        if memo:
            tx_builder.add_text_memo(memo)

        tx = tx_builder.build()
        tx.sign(self.keypair)
        
        response = self.server.submit_transaction(tx)
        if not response.get("successful"):
            raise Exception(f"Transaction submission failed: {response.get('result_xdr', 'Unknown error')}")

        return response

    def get_recommended_fee(self):
        try:
            ledger = self.server.ledgers().order(desc=True).limit(1).call()
            latest_ledger = ledger["_embedded"]["records"][0]["sequence"]
            transactions = self.server.transactions().for_ledger(latest_ledger).call()
            fees = [int(tx["max_fee"]) for tx in transactions["_embedded"]["records"]]
            if not fees:
                return 10000
            fees.sort()
            mid = len(fees) // 2
            return (fees[mid] + fees[mid - 1]) // 2 if len(fees) % 2 == 0 else fees[mid]
        except Exception:
            return 10000

    def load_account(self, public_key):
        try:
            return self.server.accounts().account_id(public_key).call()
        except Exception as e:
            raise ValueError(f"Unable to load account {public_key}: {str(e)}")

    def has_trustline(self, account, asset):
        balances = account.get("balances", [])
        for balance in balances:
            if asset.is_native() and balance["asset_type"] == "native":
                return True
            elif balance.get("asset_code") == asset.code and balance.get("asset_issuer") == asset.issuer:
                return True
        return False

    def calculate_available_xlm(self, account):
        xlm_balance = float(next((b["balance"] for b in account["balances"] if b["asset_type"] == "native"), "0"))
        selling_liabilities = float(next((b["selling_liabilities"] for b in account["balances"] if b["asset_type"] == "native"), "0"))
        subentry_count = account["subentry_count"]
        num_sponsoring = account.get("num_sponsoring", 0)
        num_sponsored = account.get("num_sponsored", 0)
        minimum_reserve = 2 + (subentry_count + num_sponsoring - num_sponsored) * 0.5
        return max(xlm_balance - selling_liabilities - minimum_reserve, 0)

    def log_balances(self):
        account = self.load_account(self.public_key)
        xlm_balance = next((b["balance"] for b in account["balances"] if b["asset_type"] == "native"), "0")
        asset_balance = next((b["balance"] for b in account["balances"] if b.get("asset_code") == self.asset_code and b.get("asset_issuer") == self.asset_issuer), "0")
        logger.info(f"Current balances: {xlm_balance} XLM, {asset_balance} {self.asset_code}")

if __name__ == "__main__":
    bot = TradeBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
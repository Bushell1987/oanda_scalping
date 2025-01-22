import tkinter as tk
from tkinter import messagebox
import yaml
import requests
import logging

# Load YAML configuration
def load_config(file_path="config.yaml"):
    """Load configuration from a YAML file."""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

# Set button colors based on environment
def set_button_colors(environment, buttons):
    """Set the background color of buttons based on the environment."""
    color = config["colors"].get(environment, "gray")  # Default to gray if environment is unknown
    for button in buttons:
        button.config(bg=color)

# Fetch account balance
# Functions
def get_account_balance(api_url, account_id, headers):
    """Fetch the current account balance from OANDA."""
    try:
        url = f"{api_url}/accounts/{account_id}/summary"
        response = requests.get(url, headers=headers)
        response_data = response.json()
        logging.debug(f"Account Summary Response: {response_data}")
        return float(response_data["account"]["balance"])
    except Exception as e:
        logging.error(f"Failed to fetch account balance: {e}")
        messagebox.showerror("Error", f"Failed to fetch account balance: {e}")
        return 0


def get_price(instrument,api_url, account_id, headers):
    """Fetch the current bid and ask prices of the instrument."""
    try:
        url = f"{api_url}/accounts/{account_id}/pricing"
        response = requests.get(url, headers=headers, params={"instruments": instrument})
        response_data = response.json()
        print("pricing=",response_data)
        logging.debug(f"Pricing API Response: {response_data}")

        # Check if 'prices' key exists
        if "prices" not in response_data:
            raise ValueError("Missing 'prices' key in API response. Check instrument or API setup.")

        # Extract bid and ask prices
        bid_price = float(response_data["prices"][0]["bids"][0]["price"])
        ask_price = float(response_data["prices"][0]["asks"][0]["price"])
        return bid_price, ask_price
    except Exception as e:
        logging.error(f"Failed to fetch prices: {e}")
        messagebox.showerror("Error", f"Failed to fetch prices: {e}")
        return 0, 0


def calculate_units(account_balance, risk_percentage, sl_pips, pip_value):
    """Calculate the number of units to trade based on risk percentage."""
    risk_amount = account_balance * (risk_percentage / 100)
    units = risk_amount / (pip_value * sl_pips)
    return int(units)


def calculate_order_prices(entry_price, sl_pips, tp_pips, direction):
    """Calculate the stop-loss and take-profit prices."""
    pip_size = 0.0001  # For most instruments, use 0.01 for JPY pairs
    if direction == "buy":
        sl_price = entry_price - (sl_pips * pip_size)
        tp_price = entry_price + (tp_pips * pip_size)
    else:  # sell
        sl_price = entry_price + (sl_pips * pip_size)
        tp_price = entry_price - (tp_pips * pip_size)
    return round(sl_price, 5), round(tp_price, 5)


def place_order(direction, instrument, risk_percentage, api_url, account_id, headers, SL_PIPS, TP_PIPS):
    """Place a trade with risk management."""
    try:
        # Get instrument from the input field
        instrument = instrument.strip().upper()
        if not instrument:
            messagebox.showerror("Error", "Instrument cannot be empty.")
            return

        # Get the custom risk percentage from the input box
        
        try:
            risk_percentage = float(risk_percentage)
            if risk_percentage <= 0:
                messagebox.showerror("Error", "Risk percentage must be greater than 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid risk percentage. Enter a valid number.")
            return

        # Get account balance
        account_balance = get_account_balance(api_url, account_id, headers)
        if account_balance <= 0:
            return

        # Calculate pip value (simplified for major pairs)
        pip_value = 0.0001  # For EUR/USD; use 0.01 for JPY pairs

        # Calculate units based on risk
        units = calculate_units(account_balance, risk_percentage, SL_PIPS, pip_value)
        if units <= 0:
            messagebox.showerror("Error", "Calculated units are zero or negative.")
            return
        print(instrument, units)
        # Get current prices
        bid_price, ask_price = get_price(instrument,api_url, account_id, headers)
        print("bid_price=",bid_price,", ask_price=",  ask_price)
        entry_price = ask_price if direction == "buy" else bid_price

        # Calculate SL and TP prices
        sl_price, tp_price = calculate_order_prices(entry_price, SL_PIPS, TP_PIPS, direction)
        print("sl_price=",sl_price,", tp_price=",  tp_price)
        # Prepare order data
        data = {
            "order": {
                "instrument": instrument,
                "units": units if direction == "buy" else -units,
                "type": "MARKET",
                "positionFill": "DEFAULT",
                "takeProfitOnFill": {"price": str(tp_price)},
                "stopLossOnFill": {"price": str(sl_price)},
            }
        }

        # Send the order
        url = f"{api_url}/accounts/{account_id}/orders"
        response = requests.post(url, headers=headers, json=data)
        logging.debug(f"Order Response: {response.json()}")

        if response.status_code == 201:
            messagebox.showinfo("Success", f"Order placed successfully: {response.json()}")
        else:
            messagebox.showerror("Error", f"Failed to place order: {response.json()}")
    except Exception as e:
        logging.error(f"Error placing order: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")


# GUI creation
def create_gui(config):
    """Create the main GUI application."""
    root = tk.Tk()
    root.title("OANDA Scalping Tool")
    root.geometry("400x400")
    
    SL_PIPS = config["trade_settings"].get("sl_pips", "")
    TP_PIPS = config["trade_settings"].get("tp_pips", "")
    # Display environment status
    environment_text = f"Trading in {'Live' if config['environment'] == 'live' else 'Test'} Mode"
    tk.Label(root, text=environment_text, font=("Helvetica", 12), fg="green" if config['environment'] == 'live' else "orange").pack(pady=5)

    tk.Label(root, text="OANDA Scalping Tool", font=("Helvetica", 16)).pack(pady=10)

    tk.Label(root, text="Instrument (e.g., EUR_USD):", font=("Helvetica", 12)).pack(pady=5)
    instrument_entry = tk.Entry(root, font=("Helvetica", 12), width=15)
    instrument_entry.insert(0, config["trade_settings"].get("default_instrument", ""))
    instrument_entry.pack(pady=5)

    tk.Label(root, text="Risk Percentage (%):", font=("Helvetica", 12)).pack(pady=5)
    risk_entry = tk.Entry(root, font=("Helvetica", 12), width=10)
    risk_entry.insert(0, config["trade_settings"].get("risk_per_trade_percent", "0.5"))
    risk_entry.pack(pady=5)

    # Buttons
    def on_buy():
        """Handle Buy button click."""
        update_status("Placing Buy Order...")
        place_order("buy", instrument_entry.get(), float(risk_entry.get()), api_url, account_id, headers, SL_PIPS, TP_PIPS)
        update_status("Idle")


    def on_sell():
        """Handle Sell button click."""
        update_status("Placing Sell Order...")
        place_order("sell", instrument_entry.get(), float(risk_entry.get()), api_url, account_id, headers, SL_PIPS, TP_PIPS)
        update_status("Idle")


    def update_status(message):
        """Update the status label."""
        status_label.config(text=f"Status: {message}")

    buy_button = tk.Button(root, text="Buy", command=on_buy, width=10, font=("Helvetica", 14))
    sell_button = tk.Button(root, text="Sell", command=on_sell, width=10, font=("Helvetica", 14))

    buy_button.pack(pady=5)
    sell_button.pack(pady=5)

    # Status Label
    status_label = tk.Label(root, text="Status: Idle", font=("Helvetica", 12), fg="blue")
    status_label.pack(pady=10)

    # Set button colors based on environment
    set_button_colors(config["environment"], [buy_button, sell_button])

    root.mainloop()

if __name__ == "__main__":
    config = load_config("config.yaml")
    api_url = config["oanda"][config["environment"]]["api_url"]
    account_id = config["oanda"][config["environment"]]["account_id"]
    api_key = config["oanda"][config["environment"]]["api_key"]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    create_gui(config)

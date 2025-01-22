# oanda_scalping

## Introduction
This tool provides a GUI-based scalping tool for OANDA trading. You can place buy and sell orders with defined risk parameters, stop-loss, and take-profit levels.

## Features
- GUI interface for trading.
- Configurable stop-loss (SL) and take-profit (TP) settings.
- Risk percentage management.
- Environment-specific settings for Live and Test modes.

## Setup Instructions

### Prerequisites
1. Install Python 3.7 or higher.
2. Install required Python libraries:
   ```bash
   pip install tkinter pyyaml requests
   ```

### Configuration
1. Open the `config.yaml` file and configure the settings:
   - **Environment**: Set to `test` or `live` depending on your preference.
   - **API Details**: Add your OANDA API key and account ID for the respective environment.
   - **Trade Settings**:
     - `sl_pips`: Stop-loss pips (default: 3).
     - `tp_pips`: Take-profit pips (default: 36).
     - `default_instrument`: Default trading instrument (e.g., `EUR_USD`).
     - `risk_per_trade_percent`: Risk percentage per trade (default: 0.25).

### Running the Tool
1. Run the script:
   ```bash
   python scalping_tool.py
   ```
2. The GUI will launch, displaying the trading tool.

### Using the Tool
1. Enter the trading instrument (e.g., `EUR_USD`) in the input field.
2. Set the desired risk percentage.
3. Click the `Buy` or `Sell` button to place an order.
4. Check the status label for updates.

## Notes
- Ensure your API key and account ID are valid for the selected environment.
- For most instruments, the pip size is 0.0001 (use 0.01 for JPY pairs).

## Troubleshooting
1. **Error: Failed to fetch account balance**
   - Ensure the API key, account ID, and URL are correct in `config.yaml`.
   - Check your internet connection.

2. **Error: Invalid instrument**
   - Confirm the instrument exists and is spelled correctly.

3. **Calculated units are zero or negative**
   - Adjust the risk percentage or ensure your account balance is sufficient.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

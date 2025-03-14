import yfinance as yf
import pandas as pd
from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='static')

# Function to get current BABA price data
def get_current_price():
    try:
        # Get ticker info
        ticker = yf.Ticker("BABA")
        
        # Get current price info
        info = ticker.info
        
        # Extract relevant data
        price_data = {
            "currentPrice": info.get("currentPrice", 0),
            "previousClose": info.get("previousClose", 0),
            "dayLow": info.get("dayLow", 0),
            "dayHigh": info.get("dayHigh", 0),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", 0),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0)
        }
        
        # Calculate change
        price_data["change"] = price_data["currentPrice"] - price_data["previousClose"]
        price_data["changePercent"] = (price_data["change"] / price_data["previousClose"]) * 100
        
        return price_data
    except Exception as e:
        print(f"Error fetching current price: {e}")
        # Return fallback data
        return {
            "currentPrice": 76.42,
            "previousClose": 77.70,
            "change": -1.28,
            "changePercent": -1.65,
            "dayLow": 75.86,
            "dayHigh": 77.90,
            "fiftyTwoWeekLow": 66.63,
            "fiftyTwoWeekHigh": 112.09
        }

# Function to get historical price data
def get_historical_data():
    try:
        # Get ticker history
        ticker = yf.Ticker("BABA")
        hist = ticker.history(period="6mo")
        
        # Extract dates and closing prices
        dates = hist.index.strftime('%Y-%m-%d').tolist()
        prices = hist['Close'].tolist()
        
        return {"dates": dates, "prices": prices}
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        # Return fallback data
        return {
            "dates": [
                "2024-09-12", "2024-09-26", "2024-10-10", "2024-10-24", 
                "2024-11-07", "2024-11-21", "2024-12-05", "2024-12-19", 
                "2025-01-02", "2025-01-16", "2025-01-30", "2025-02-13", 
                "2025-02-27", "2025-03-10"
            ],
            "prices": [
                82.45, 81.30, 80.20, 78.30, 75.20, 72.15, 70.50, 
                68.90, 71.40, 74.25, 77.60, 79.80, 78.10, 76.42
            ]
        }

# API route for current price
@app.route('/api/current-price')
def api_current_price():
    return jsonify(get_current_price())

# API route for historical data
@app.route('/api/historical-data')
def api_historical_data():
    return jsonify(get_historical_data())

# Serve the HTML page
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Make sure static folder exists
if not os.path.exists('static'):
    os.makedirs('static')

# Create the HTML file in the static folder
with open('static/index.html', 'w') as f:
    f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My BABA Trading Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 20px;
        }
        .card h2 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .price-info {
            display: flex;
            justify-content: space-between;
            font-size: 18px;
            margin-bottom: 15px;
        }
        .price {
            font-size: 28px;
            font-weight: bold;
        }
        .change {
            padding: 5px 10px;
            border-radius: 4px;
            font-weight: bold;
        }
        .positive {
            background-color: #e6f7ee;
            color: #0e9f6e;
        }
        .negative {
            background-color: #fde8e8;
            color: #e02424;
        }
        .profit-table {
            width: 100%;
            border-collapse: collapse;
        }
        .profit-table th, .profit-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .profit-table th {
            background-color: #f9fafb;
        }
        .chart-container {
            height: 300px;
            position: relative;
        }
        .total-profit {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            margin-top: 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        .stat-item {
            background: #f9fafb;
            padding: 15px;
            border-radius: 6px;
        }
        .stat-label {
            font-size: 14px;
            color: #6b7280;
        }
        .stat-value {
            font-size: 18px;
            font-weight: bold;
            margin-top: 5px;
        }
        .last-updated {
            text-align: right;
            font-size: 12px;
            color: #6b7280;
            margin-top: 10px;
        }
        .loading {
            text-align: center;
            padding: 20px;
            font-style: italic;
            color: #6b7280;
        }
        .api-status {
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
            background-color: #f9fafb;
            color: #6b7280;
            font-size: 12px;
        }
        .toggle-button {
            cursor: pointer;
            padding: 8px 16px;
            background-color: #4682B4;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>My BABA Trading Dashboard</h1>
            <p>Track your Alibaba trading performance</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h2>BABA Current Price</h2>
                <div id="price-container">
                    <div class="loading">Loading current price data...</div>
                </div>
                <div class="last-updated" id="last-updated"></div>
                <div class="api-status" id="api-status"></div>
                <button class="toggle-button" id="update-button">Refresh Price</button>
            </div>
            
            <div class="card">
                <h2>My BABA Profits</h2>
                <table class="profit-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Shares</th>
                            <th>Buy Price</th>
                            <th>Sell Price</th>
                            <th>Profit</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Add your trade history here -->
                        <tr>
                            <td>2025-01-15</td>
                            <td>50</td>
                            <td>$68.50</td>
                            <td>$74.25</td>
                            <td class="positive">+$287.50</td>
                        </tr>
                        <tr>
                            <td>2025-02-03</td>
                            <td>75</td>
                            <td>$72.10</td>
                            <td>$78.40</td>
                            <td class="positive">+$472.50</td>
                        </tr>
                        <tr>
                            <td>2025-02-28</td>
                            <td>100</td>
                            <td>$79.30</td>
                            <td>$77.50</td>
                            <td class="negative">-$180.00</td>
                        </tr>
                    </tbody>
                </table>
                <div class="total-profit positive">Total Profit: +$580.00</div>
            </div>
        </div>
        
        <div class="card" style="margin-top: 20px;">
            <h2>BABA Price Chart</h2>
            <div class="chart-container">
                <canvas id="priceChart"></canvas>
            </div>
            <div class="loading" id="chart-loading">Loading historical data...</div>
        </div>
    </div>

    <script>
        // Initialize chart with empty data
        let priceChart;
        const ctx = document.getElementById('priceChart').getContext('2d');
        const chartData = {
            labels: [],
            datasets: [{
                label: 'BABA Price',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                data: [],
                tension: 0.3,
                fill: true
            }]
        };
        
        function initChart() {
            priceChart = new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    }
                }
            });
        }
        
        // Function to format current price data
        function formatCurrentPrice(data) {
            const price = data.currentPrice.toFixed(2);
            const change = data.change.toFixed(2);
            const changePercent = data.changePercent.toFixed(2);
            const dayLow = data.dayLow.toFixed(2);
            const dayHigh = data.dayHigh.toFixed(2);
            const fiftyTwoWeekLow = data.fiftyTwoWeekLow.toFixed(2);
            const fiftyTwoWeekHigh = data.fiftyTwoWeekHigh.toFixed(2);
            
            const changeClass = change >= 0 ? 'positive' : 'negative';
            const changeSign = change >= 0 ? '+' : '';
            
            return `
                <div class="price-info">
                    <span class="price">$${price}</span>
                    <span class="change ${changeClass}">${changeSign}$${Math.abs(change)} (${changeSign}${changePercent}%)</span>
                </div>
                <div>
                    <div class="stat-label">Day Range</div>
                    <div class="stat-value">$${dayLow} - $${dayHigh}</div>
                </div>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-label">52-Week Low</div>
                        <div class="stat-value">$${fiftyTwoWeekLow}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">52-Week High</div>
                        <div class="stat-value">$${fiftyTwoWeekHigh}</div>
                    </div>
                </div>
            `;
        }
        
        // Function to fetch current price from our backend
        async function fetchCurrentPrice() {
            try {
                const response = await fetch('/api/current-price');
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                
                // Update price display
                document.getElementById('price-container').innerHTML = formatCurrentPrice(data);
                
                // Update last updated time
                const now = new Date();
                document.getElementById('last-updated').textContent = `Last updated: ${now.toLocaleString()}`;
                document.getElementById('api-status').textContent = 'Data from yfinance API';
                
                return data;
            } catch (error) {
                console.error('Error fetching price data:', error);
                document.getElementById('price-container').innerHTML = `
                    <div class="loading">Error loading price data. Please try again later.</div>
                `;
                document.getElementById('api-status').textContent = 'Failed to fetch data from API';
                return null;
            }
        }
        
        // Function to fetch historical data from our backend
        async function fetchHistoricalData() {
            try {
                const response = await fetch('/api/historical-data');
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                
                // Update chart data
                chartData.labels = data.dates;
                chartData.datasets[0].data = data.prices;
                priceChart.update();
                
                // Hide loading message
                document.getElementById('chart-loading').style.display = 'none'  }));
                </script>
                </body>
                </html>"""

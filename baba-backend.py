import yfinance as yf
import time
import pandas as pd
from flask import Flask, jsonify, send_from_directory
import os
import requests
from requests.exceptions import RequestException

app = Flask(__name__, static_folder='static')

def get_current_price():

        ticker = yf.Ticker("BABA")
        info = ticker.fast_info
    
        # Extract relevant data
        price_data = {
            "lastPrice": info.get("lastPrice"),
            "previousClose": info.get("previousClose"),
            "dayLow": info.get("dayLow", 0),
            "dayHigh": info.get("dayHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh")
        }
        
        # Calculate change
        price_data["change"] = price_data["lastPrice"] - price_data["previousClose"]
        price_data["changePercent"] = (price_data["change"] / price_data["previousClose"]) * 100
        
        # Update cache
        cached_price_data = price_data
        last_price_update = current_time
        
        print(f"Successfully fetched price data: {price_data}")  # Debug log
        return price_data
            
        print("Returning fallback data")
        return {
            "lastPrice": 76.5,
            "previousClose": 77.70,
            "change": -1.28,
            "changePercent": -1.65,
            "dayLow": 75.86,
            "dayHigh": 77.90,
            "fiftyTwoWeekLow": 66.63,
            "fiftyTwoWeekHigh": 112.09
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
            <p>Tracking Alibaba trading performance</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h2>BABA Current Price</h2>
                <div id="price-container">
                    <div class="loading">Loading current price data...</div>
                </div>
                <div class="last-updated" id="last-updated"></div>
                <div class="api-status" id="api-status"></div>
            </div>
            
            <div class="card">
                <h2>My BABA Profits</h2>
                <table class="profit-table">
                    <thead>
                        <tr>
                            <th>Date Closed</th>
                            <th>Strikes</th>
                            <th>Credit Received</th>
                            <th>Profit</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Add your trade history here -->
                        <tr>
                            <td>01-28-2025</td>
                            <td>85</td>
                            <td>$108</td>
                            <td class="positive">+$69</td>
                        </tr>
                        <tr>
                            <td>02-07-2025</td>
                            <td>85/97</td>
                            <td>$969</td>
                            <td class="positive">+$492</td>
                        </tr>
                        <tr>
                            <td>02-12-2025</td>
                            <td>104</td>
                            <td>$335</td>
                            <td class="positive">+$186</td>>
                        </tr>
                    </tbody>
                </table>
                <div class="total-profit positive">Total Profit: +$1752.00</div>
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
        function formatlastPrice(data) {
            const price = data.lastPrice.toFixed(2);
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
    async function fetchlastPrice() {
        try {
            const response = await fetch('/api/current-price');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            
            // Update price display
             document.getElementById('price-container').innerHTML = formatlastPrice(data["lastPrice"]);
            
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
                if (!response.ok) throw new Error('Failed to fetch data');
                const data = await response.json();
            
            // Update chart data
                chartData.labels = data.dates;
                chartData.datasets[0].data = data.prices;
            
            // Initialize chart if it doesn't exist
                if (!priceChart) {
                    initChart();
                } else {
                    priceChart.update();
                }
            
                document.getElementById('chart-loading').style.display = 'none';
            } catch (error) {
                console.error('Error fetching historical data:', error);
                document.getElementById('chart-loading').textContent = 'Failed to load data';
            }
        }

// Add periodic updates for both current price and chart

function startUpdates() {
    // Initial fetches
    fetchlastPrice();
    fetchHistoricalData();
    
    // Set up periodic updates with longer intervals
    setInterval(fetchlastPrice, 300000);  // Update price every 5 minutes instead of every minute
    setInterval(fetchHistoricalData, 900000); // Update chart every 15 minutes instead of every 5 minutes
}

// Change the DOMContentLoaded event to use startUpdates
document.addEventListener("DOMContentLoaded", startUpdates);
                </script>
                </body>
                </html>""")
    if __name__ == "__main__":
        print("Server starting on http://localhost:10080")
        app.run(host='0.0.0.0', port=10080, debug=False)

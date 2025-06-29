# Costco Items Analysis Dashboard

A beautiful, interactive HTML dashboard for analyzing your Costco purchase data with price trends and statistics.

## Features

🛒 **Interactive Visualization**

- Beautiful ECharts-powered line charts showing price trends over time
- Multi-select item filtering with search functionality
- Responsive design that works on desktop and mobile

📊 **Comprehensive Statistics**

- Min, Max, Average, Median, and Standard Deviation for each item
- Real-time statistics updates based on your selection
- Color-coded statistics cards in the sidebar

📋 **Data Table**

- Sortable table showing underlying transaction data
- Displays transaction date, item name, description, and price
- Limited to 100 rows for optimal performance

🎨 **Modern UI**

- Glass-morphism design with gradient backgrounds
- Smooth animations and hover effects
- Professional color scheme

## How to Use

1. **Open the Dashboard**

   ```bash
   # Serve the files using Python's built-in server
   python -m http.server 8000

   # Or use any other local server
   # Then open: http://localhost:8000/costco-dashboard.html
   ```

2. **Select Items**

   - Use the multi-select dropdown in the sidebar
   - Search for specific items using the search box
   - Use "Select All" or "Clear All" buttons for bulk operations

3. **Analyze Data**

   - View price trends in the main chart
   - Check statistics in the sidebar for selected items
   - Browse underlying data in the table below the chart

4. **Chart Interactions**
   - Zoom in/out using mouse wheel or zoom controls
   - Hover over data points for detailed tooltips
   - Save chart as image using the toolbar

## Default Behavior

- By default, shows average price trends for all items
- Y-axis represents unit price in dollars
- X-axis shows transaction dates
- Statistics show aggregated data for all selected items

## Data Format

The dashboard expects a CSV file named `costco-items.csv` with the following columns:

- `transaction_date`: Date of purchase (YYYY-MM-DD)
- `transaction_barcode`: Receipt barcode
- `item_number`: Item number
- `description`: Item description
- `description2`: Additional description
- `combined_description`: Full item name
- `item_unit_price`: Price in dollars

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Works best with internet connection for CDN resources

## Customization

You can customize the dashboard by:

- Modifying colors in the CSS variables
- Adjusting chart options in the `setupChart()` function
- Changing the number of displayed table rows
- Adding new statistical calculations

Enjoy analyzing your Costco shopping patterns! 🛒📈

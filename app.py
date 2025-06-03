from flask import Flask, render_template_string, request
import pandas as pd

app = Flask(__name__)

# Function to fetch and sort data from an Excel file, and filter by status if provided
def get_hotel_data(hotel_name, filter_status=None):
    file_name = f"{hotel_name.lower()}.xlsx"  # Assumes file names are in lowercase
    try:
        # Read the Excel file for the selected hotel
        df = pd.read_excel(file_name)

        # Check if required columns are present, then sort by Name and Status
        if 'Name' in df.columns and 'Status' in df.columns:
            if filter_status:
                df = df[df['Status'].str.lower() == filter_status.lower()]  # Filter by status if provided
            sorted_df = df[['Name', 'Status']].sort_values(by=['Name', 'Status'])
            return sorted_df.to_dict(orient='records')  # Convert to list of dictionaries for Flask template
        else:
            return [{'error': 'Required columns (Name, Status) not found in file'}]
    except FileNotFoundError:
        return [{'error': f'File "{file_name}" not found.'}]

def get_system_data(system_name):
    file_name = f"{system_name.lower()}.xlsx"  # Assumes file names are in lowercase
    try:
        # Read the Excel file for the selected system
        df = pd.read_excel(file_name)

        # Check if required columns are present
        if 'Name' in df.columns and 'Status' in df.columns:
            sorted_df = df[['Name', 'Status']].sort_values(by=['Name', 'Status'])
            return sorted_df.to_dict(orient='records')  # Convert to list of dictionaries for Flask template
        else:
            return [{'error': 'Required columns (Name, Status) not found in file'}]
    except FileNotFoundError:
        return [{'error': f'File "{file_name}" not found.'}]

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_site = request.form.get('site')
    selected_system = request.form.get('system')
    filter_status = request.form.get('status')
    parsed_data = []
    system_data = []

    if selected_site:
        # Fetch data from the Excel file for the selected site and filter by status if applicable
        parsed_data = get_hotel_data(selected_site, filter_status)

    if selected_system:
        # Fetch data from the Excel file for the selected system without filtering by status
        system_data = get_system_data(selected_system)

    # Enhanced HTML template with the requested color and font changes
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ICT OPS Proactive Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Century+Gothic&display=swap" rel="stylesheet">
        <style>
            body { 
                font-family: 'Century Gothic', sans-serif; 
                background: #fafafa; 
                color: #00263e; 
                padding: 20px; 
                margin: 0; 
                background-image: url('{{ url_for('static', filename='logo.png') }}'); /* Logo as background */
                background-size: cover; /* Adjust to cover entire area */
                background-position: center; /* Center the logo */
                background-repeat: no-repeat; /* Prevent repetition */
            }
            h1 { 
                color: #00263e; 
                text-align: center; 
                margin-top: 20px; 
                font-size: 2.5em; 
            }
            form { 
                display: flex; 
                justify-content: center; 
                margin-bottom: 20px; 
            }
            select, button { 
                padding: 10px; 
                font-size: 16px; 
                border-radius: 5px; 
                border: 1px solid #ccc; 
                margin-right: 10px; 
            }
            select { 
                background-color: #ffffff; 
            }
            button { 
                background-color: #b4a064; 
                color: #ffffff; 
                cursor: pointer; 
                transition: background-color 0.3s; 
            }
            button:hover { 
                background-color: #a18a57; 
            }
            .container { 
                max-width: 900px; 
                margin: auto; 
                padding: 20px; 
                background-color: rgba(255, 255, 255, 0.9); /* White background with transparency */
                border-radius: 12px; 
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); 
            }
            .data-grid { 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 15px; 
                padding: 20px 0; 
            }
            .header { 
                font-weight: bold; 
                text-align: center; 
                color: #333; 
                border-bottom: 2px solid #FFC107; 
                padding-bottom: 8px; 
            }
            .grid-item { 
                padding: 10px; 
                font-size: 1.1em; 
                border-radius: 8px; 
                text-align: center; 
            }
            .error { 
                color: red; 
                text-align: center; 
            }
            /* Status-specific color coding */
            .status-online { 
                background-color: #e3f2e9; 
                color: #155724; 
                border: 1px solid #c3e6cb; 
            }
            .status-dormant { 
                background-color: #ffeeba; 
                color: #856404; 
                border: 1px solid #ffeeba; 
            }
            .status-offline { 
                background-color: #f8d7da; 
                color: #721c24; 
                border: 1px solid #f5c6cb; 
            }
            .footer { 
                text-align: center; 
                color: #666; 
                font-size: 0.9em; 
                margin-top: 20px; 
            }
        </style>
    </head>
    <body>
        <h1>ICT OPS Proactive Dashboard</h1>
        <form method="POST">
            <select name="site" required>
                <option value="">-- Select a Hotel --</option>
                <option value="Paradis" {% if selected_site == 'Paradis' %}selected{% endif %}>Paradis Beachcomber</option>
                <option value="Mauricia" {% if selected_site == 'Mauricia' %}selected{% endif %}>Mauricia Beachcomber</option>
                <option value="Royal Palm" {% if selected_site == 'Royal Palm' %}selected{% endif %}>Royal Palm Beachcomber</option>
            </select>
            <select name="system">
                <option value="">-- Select a System --</option>
                <option value="Meraki" {% if selected_system == 'Meraki' %}selected{% endif %}>Meraki</option>
                <option value="Lycia" {% if selected_system == 'Lycia' %}selected{% endif %}>Lycia</option>
                <option value="CUCM" {% if selected_system == 'CUCM' %}selected{% endif %}>CUCM</option>
            </select>
            <select name="status">
                <option value="">-- All Statuses --</option>
                <option value="Dormant" {% if filter_status == 'Dormant' %}selected{% endif %}>Dormant</option>
                <option value="Offline" {% if filter_status == 'Offline' %}selected{% endif %}>Offline</option>
                <option value="Alerting" {% if filter_status == 'Alerting' %}selected{% endif %}>Alerting</option>
            </select>
            <button type="submit">Load Data</button>
        </form>

        <div class="container">
            {% if selected_site %}
                <div class="data-grid">
                    <div class="header">Name</div>
                    <div class="header">Status</div>
                    {% for device in parsed_data %}
                        <div class="grid-item">{{ device['Name'] }}</div>
                        <div class="grid-item 
                            {% if device['Status'] == 'Online' %}status-online{% elif device['Status'] == 'Dormant' %}status-dormant{% elif device['Status'] == 'Offline' %}status-offline{% endif %}
                        ">
                            {{ device['Status'] }}
                        </div>
                    {% endfor %}
                </div>
            {% elif selected_system == 'Meraki' %}
                <div class="data-grid">
                    <div class="header">Name</div>
                    <div class="header">Status</div>
                    {% for device in system_data %}
                        <div class="grid-item">{{ device['Name'] }}</div>
                        <div class="grid-item 
                            {% if device['Status'] == 'Online' %}status-online{% elif device['Status'] == 'Dormant' %}status-dormant{% elif device['Status'] == 'Offline' %}status-offline{% endif %}
                        ">
                            {{ device['Status'] }}
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
            {% if parsed_data and parsed_data[0].get('error') %}
                <p class="error">{{ parsed_data[0]['error'] }}</p>
            {% endif %}
        </div>

        <div class="footer">
            &copy; ICT OPS Proactive Dashboard by Mika
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_template, parsed_data=parsed_data, selected_site=selected_site,
                                  filter_status=filter_status, system_data=system_data, selected_system=selected_system)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)

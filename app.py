from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Function to fetch and sort hotel data
def get_hotel_data(hotel_name, filter_status=None):
    file_name = f"{hotel_name.lower()}.xlsx"
    try:
        df = pd.read_excel(file_name)
        if 'Name' in df.columns and 'Status' in df.columns:
            if filter_status:
                df = df[df['Status'].str.lower() == filter_status.lower()]
            sorted_df = df[['Name', 'Status']].sort_values(by=['Name', 'Status'])
            return sorted_df.to_dict(orient='records')
        else:
            return [{'error': 'Required columns (Name, Status) not found in file'}]
    except FileNotFoundError:
        return [{'error': f'File "{file_name}" not found.'}]

# Function to fetch system data
def get_system_data(system_name):
    file_name = f"{system_name.lower()}.xlsx"
    try:
        df = pd.read_excel(file_name)
        if 'Name' in df.columns and 'Status' in df.columns:
            sorted_df = df[['Name', 'Status']].sort_values(by=['Name', 'Status'])
            return sorted_df.to_dict(orient='records')
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
        parsed_data = get_hotel_data(selected_site, filter_status)
    if selected_system:
        system_data = get_system_data(selected_system)

    html_template = '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ICT OPS Proactive Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Century+Gothic&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Century Gothic', sans-serif;
                background: #fafafa;
                color: #00263e;
                padding: 20px;
                margin: 0;
                background-image: url('{{ url_for('static', filename='logo.png') }}');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }
            h1 { text-align: center; font-size: 2.5em; }
            form { display: flex; justify-content: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
            select, button {
                padding: 10px; font-size: 16px; border-radius: 5px; border: 1px solid #ccc;
            }
            button {
                background-color: #b4a064; color: white; cursor: pointer;
            }
            .container {
                max-width: 900px; margin: auto; background-color: rgba(255,255,255,0.9);
                padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            .data-grid {
                display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 20px 0;
            }
            .header { font-weight: bold; text-align: center; border-bottom: 2px solid #FFC107; }
            .grid-item {
                padding: 10px; text-align: center; border-radius: 8px;
            }
            .status-online {
                background-color: #e3f2e9; color: #155724; border: 1px solid #c3e6cb;
            }
            .status-dormant {
                background-color: #ffeeba; color: #856404; border: 1px solid #ffeeba;
            }
            .status-offline {
                background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;
            }
            .error { color: red; text-align: center; }
            .footer { text-align: center; font-size: 0.9em; margin-top: 20px; color: #666; }
        </style>
    </head>
    <body>
        <h1>ICT OPS Proactive Dashboard</h1>
        <form method="POST">
            <select name="site">
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
            {% if parsed_data %}
                <div class="data-grid">
                    <div class="header">Name</div>
                    <div class="header">Status</div>
                    {% for device in parsed_data %}
                        <div class="grid-item">{{ device['Name'] }}</div>
                        <div class="grid-item 
                            {% if device['Status'] == 'Online' %}status-online{% elif device['Status'] == 'Dormant' %}status-dormant{% elif device['Status'] == 'Offline' %}status-offline{% endif %}">
                            {{ device['Status'] }}
                        </div>
                    {% endfor %}
                </div>
            {% elif parsed_data and parsed_data[0].get('error') %}
                <p class="error">{{ parsed_data[0]['error'] }}</p>
            {% endif %}

            {% if selected_system and selected_system == 'Meraki' %}
                <div class="data-grid">
                    <div class="header">Name</div>
                    <div class="header">Status</div>
                    {% for device in system_data %}
                        <div class="grid-item">{{ device['Name'] }}</div>
                        <div class="grid-item 
                            {% if device['Status'] == 'Online' %}status-online{% elif device['Status'] == 'Dormant' %}status-dormant{% elif device['Status'] == 'Offline' %}status-offline{% endif %}">
                            {{ device['Status'] }}
                        </div>
                    {% endfor %}
                </div>
            {% endif %}
        </div>

        <div class="footer">
            &copy; ICT OPS Proactive Dashboard by Mika
        </div>
    </body>
    </html>'''

    return render_template_string(html_template, parsed_data=parsed_data, selected_site=selected_site,
                                  filter_status=filter_status, system_data=system_data, selected_system=selected_system)

# Optional route to receive Meraki alert webhook (JSON payload)
@app.route('/meraki/webhook', methods=['POST'])
def meraki_webhook():
    data = request.get_json()
    print("Meraki Alert Received:", data)  # Log to terminal or Render logs
    return jsonify({"status": "received"}), 200

# Run app (Render uses the PORT env variable)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

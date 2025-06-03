from flask import Flask, render_template_string, request
import meraki

app = Flask(__name__)

# Replace with your actual Meraki API key
MERAKI_API_KEY = 'YOUR_MERAKI_API_KEY'
DASHBOARD = meraki.DashboardAPI(MERAKI_API_KEY, suppress_logging=True)

ORG_ID = None  # optional: hardcode if known for speed

# Get Meraki Devices
def get_meraki_devices():
    try:
        global ORG_ID
        if not ORG_ID:
            orgs = DASHBOARD.organizations.getOrganizations()
            ORG_ID = orgs[0]['id']

        networks = DASHBOARD.organizations.getOrganizationNetworks(ORG_ID)
        all_devices = []

        for net in networks:
            net_id = net['id']
            devices = DASHBOARD.networks.getNetworkDevices(net_id)
            for device in devices:
                all_devices.append({
                    'Name': device.get('name', device['model']),
                    'Status': device.get('status', 'Unknown')
                })

        sorted_devices = sorted(all_devices, key=lambda x: (x['Name'], x['Status']))
        return sorted_devices
    except Exception as e:
        return [{'error': f'Meraki API error: {str(e)}'}]

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_system = request.form.get('system')
    filter_status = request.form.get('status')
    system_data = []

    if selected_system == 'Meraki':
        system_data = get_meraki_devices()
        if filter_status:
            system_data = [d for d in system_data if d['Status'].lower() == filter_status.lower()]

    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ICT OPS Proactive Dashboard</title>
        <link href="https://fonts.googleapis.com/css2?family=Century+Gothic&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Century Gothic', sans-serif;
                background: #fafafa;
                padding: 20px;
                margin: 0;
            }
            h1 { text-align: center; color: #00263e; }
            form {
                display: flex; justify-content: center; gap: 10px; margin-bottom: 20px;
            }
            select, button {
                padding: 10px; font-size: 16px;
                border-radius: 5px; border: 1px solid #ccc;
            }
            button {
                background-color: #b4a064; color: white; cursor: pointer;
            }
            .container {
                max-width: 1000px; margin: auto;
                background-color: white;
                padding: 20px; border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            }
            .data-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }
            .header {
                font-weight: bold;
                border-bottom: 2px solid #FFC107;
                text-align: center;
            }
            .grid-item {
                text-align: center;
                padding: 10px;
                border-radius: 6px;
            }
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
            .status-alerting {
                background-color: #fff3cd;
                color: #856404;
                border: 1px solid #ffeeba;
            }
            .footer {
                text-align: center;
                color: #666;
                font-size: 0.9em;
                margin-top: 20px;
            }
            .error {
                color: red;
                text-align: center;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h1>ICT OPS Proactive Dashboard</h1>
        <form method="POST">
            <select name="system">
                <option value="">-- Select a System --</option>
                <option value="Meraki" {% if selected_system == 'Meraki' %}selected{% endif %}>Meraki</option>
            </select>
            <select name="status">
                <option value="">-- All Statuses --</option>
                <option value="Online" {% if filter_status == 'Online' %}selected{% endif %}>Online</option>
                <option value="Dormant" {% if filter_status == 'Dormant' %}selected{% endif %}>Dormant</option>
                <option value="Offline" {% if filter_status == 'Offline' %}selected{% endif %}>Offline</option>
                <option value="Alerting" {% if filter_status == 'Alerting' %}selected{% endif %}>Alerting</option>
            </select>
            <button type="submit">Load Data</button>
        </form>

        <div class="container">
            {% if system_data and system_data[0].get('error') %}
                <p class="error">{{ system_data[0]['error'] }}</p>
            {% endif %}

            {% if selected_system and not system_data[0].get('error') %}
                <div class="data-grid">
                    <div class="header">Name</div><div class="header">Status</div>
                    {% for device in system_data %}
                        <div class="grid-item">{{ device['Name'] }}</div>
                        <div class="grid-item status-{{ device['Status'] | lower }}">{{ device['Status'] }}</div>
                    {% endfor %}
                </div>
            {% endif %}
        </div>

        <div class="footer">
            &copy; ICT OPS Proactive Dashboard by Mika
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_template, system_data=system_data,
                                  selected_system=selected_system, filter_status=filter_status)

if __name__ == '__main__':
    app.run(debug=True)

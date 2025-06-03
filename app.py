from flask import Flask, render_template, request
import meraki

app = Flask(__name__)

MERAKI_API_KEY = 'YOUR_MERAKI_API_KEY'
DASHBOARD = meraki.DashboardAPI(MERAKI_API_KEY, suppress_logging=True)
ORG_ID = None


def get_lycia_devices():
    return [
        {'Name': 'Lycia Gateway 1', 'Status': 'online'},
        {'Name': 'Lycia Gateway 2', 'Status': 'offline'}
    ]

def get_cucm_devices():
    return [
        {'Name': 'CUCM Cluster 1', 'Status': 'online'},
        {'Name': 'CUCM Cluster 2', 'Status': 'offline'}
    ]

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
        return [{'Name': 'Error', 'Status': f'Meraki API error: {str(e)}'}]

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_system = request.form.get('system', 'Meraki')
    filter_status = request.form.get('status', '')
    system_data = []

    if selected_system == 'Meraki':
        system_data = get_meraki_devices()
    elif selected_system == 'Lycia':
        system_data = get_lycia_devices()
    elif selected_system == 'CUCM':
        system_data = get_cucm_devices()

    if filter_status:
        system_data = [d for d in system_data if d['Status'].lower() == filter_status.lower()]

    return render_template('index.html',
                           system_data=system_data,
                           selected_system=selected_system,
                           filter_status=filter_status)

if __name__ == '__main__':
    app.run(debug=True)

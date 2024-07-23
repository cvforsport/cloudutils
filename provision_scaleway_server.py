import requests
import argparse
import time

# Remplacez par vos propres valeurs
API_TOKEN = '0c48a1d6-84fa-4dbe-9e39-021f17283823'
ORGANIZATION_ID = '15194b27-ccae-428a-88ae-5c6edacc6ba3'
PROJECT_ID = '15194b27-ccae-428a-88ae-5c6edacc6ba3'
ZONE = 'fr-par-2'  # Exemple: 'fr-par-1', 'nl-ams-1'
IMAGE = 'ubuntu_focal'  # Exemple: 'ubuntu_focal'
COMMERCIAL_TYPE = 'GP1-XS'  # Exemple pour GPU
INSTANCE_NAME = 'yolo-training-instance'  # Nom de l'instance

headers = {
    'X-Auth-Token': API_TOKEN,
    'Content-Type': 'application/json',
}

def list_images(zone):
    response = requests.get(f'https://api.scaleway.com/instance/v1/zones/{zone}/images', headers=headers)
    if response.status_code == 200:
        images = response.json()['images']
        if images:
            print("Available images:")
            for image in images:
                print(f"- ID: {image['id']}, Name: {image['name']}, Arch: {image['arch']}, Creation date: {image['creation_date']}")
        else:
            print("No images available.")
    else:
        print(f"Failed to list images: {response.json()}")

def attach_ip(instance_id, project_id):
    data = {
        "project": project_id,
        "server": instance_id
    }
    response = requests.post(f'https://api.scaleway.com/instance/v1/zones/{ZONE}/ips', headers=headers, json=data)
    if response.status_code == 201:
        ip_info = response.json()['ip']
        ip_address = ip_info['address']
        print(f"IP {ip_info['id']} attached to instance {instance_id}")
        return ip_address
    else:
        print(f"Failed to attach IP: {response.json()}")
        return None

def start_instance(instance_id):
    data = {
        "action": "poweron"
    }
    response = requests.post(f'https://api.scaleway.com/instance/v1/zones/{ZONE}/servers/{instance_id}/action', headers=headers, json=data)
    if response.status_code == 202:
        print(f"Instance {instance_id} start action initiated.")
        
        # Wait for the instance to start
        start_time = time.time()
        while time.time() - start_time < 20:
            time.sleep(2)  # Wait for 2 seconds before checking the status again
            status_response = requests.get(f'https://api.scaleway.com/instance/v1/zones/{ZONE}/servers/{instance_id}', headers=headers)
            if status_response.status_code == 200:
                status = status_response.json()['server']['state']
                if status in ["running"]:
                    print(f"Instance {instance_id} is now running.")
                    return True
            else:
                print(f"Failed to get instance status: {status_response.json()}")
                return False
        print(f"Timeout: Instance {instance_id} did not start within 20 seconds.")
    else:
        print(f"Failed to start instance: {response.json()}")
    return False

def create_instance(instance_name):
    data = {
        "organization": ORGANIZATION_ID,
        "name": instance_name,
        "commercial_type": COMMERCIAL_TYPE,
        "image": IMAGE,
        "tags": ["test-instance"],
    }
    response = requests.post(f'https://api.scaleway.com/instance/v1/zones/{ZONE}/servers', headers=headers, json=data)
    if response.status_code == 201:
        instance_id = response.json()['server']['id']
        print(f"Instance created with ID: {instance_id}")

        # Attach IP to instance
        ip_address = attach_ip(instance_id, PROJECT_ID)
        if ip_address:
            print(f"Connect to your instance using: ssh root@{ip_address}")
            # Start the instance
            if start_instance(instance_id):
                print(f"Instance {instance_id} started successfully.")

        return instance_id
    else:
        print(f"Failed to create instance: {response.json()}")
        list_instances()
        return None

def delete_instance(instance_id):
    response = requests.delete(f'https://api.scaleway.com/instance/v1/zones/{ZONE}/servers/{instance_id}', headers=headers)
    if response.status_code == 204:
        print(f"Instance {instance_id} deleted successfully.")
    else:
        print(f"Failed to delete instance: {response.json()}")
        list_instances()

def list_instances():
    response = requests.get(f'https://api.scaleway.com/instance/v1/zones/{ZONE}/servers', headers=headers)
    if response.status_code == 200:
        instances = response.json()['servers']
        if instances:
            print("Available instances:")
            for instance in instances:
                print(f"- ID: {instance['id']}, Name: {instance['name']}, Status: {instance['state']}")
        else:
            print("No instances available.")
    else:
        print(f"Failed to list instances: {response.json()}")

def main():
    parser = argparse.ArgumentParser(description='Create, delete or list images for a Scaleway instance.')
    parser.add_argument('--delete', type=str, help='ID of the instance to delete')
    parser.add_argument('--list', action='store_true', help='List available images')
    parser.add_argument('--attach-ip', type=str, help='ID of the Flexible IP to attach')
    parser.add_argument('--server-id', type=str, help='ID of the server to attach the Flexible IP to')
    args = parser.parse_args()

    if args.list:
        list_images(ZONE)
    elif args.delete:
        delete_instance(args.delete)
    elif args.attach_ip and args.server_id:
        attach_ip(args.server_id, args.attach_ip)
    else:
        instance_id = create_instance(INSTANCE_NAME)

if __name__ == "__main__":
    main()
import time

import googleapiclient.discovery
from oauth2client.client import GoogleCredentials


def create_multi_instances(compute, project, zone, instance_type, instance_name, instance_count):
        
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(
        project='debian-cloud', family='debian-11').execute()
    source_disk_image = image_response['selfLink']

    config = {
        'count': instance_count,
        'name_pattern': instance_name+"###",
        'instance_properties': {
            'machineType': instance_type,
              "labels": {
                "key": "value",
                },
    
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': source_disk_image,
                    },
                    "labels": {
                        "key": "value",
                    }
                }
            ],
    
            # Specify a network interface with NAT to access the public
            # internet.
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ]
            }]
        }
    }

    return compute.instances().bulkInsert(
        project=project,
        zone=zone,
        body=config).execute()


def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)


def list_instances(compute, project, zone, instance_name):
    instances_result = compute.instances().list(project=project, zone=zone, filter="name = %s*" %instance_name).execute()
    return instances_result['items'] if 'items' in instances_result else None



if __name__ == '__main__':

    credentials = GoogleCredentials.get_application_default()
    compute = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)

    project_id = "becky-poc"
    zone = "us-central1-f"
    instance_type = "n1-standard-1"
    instance_name = "demo-instances-"
    instance_count = 2

    print('start creating instances.')
    # operation = create_multi_instances(compute, project_id, zone, instance_type, instance_name, instance_count)
    # result = wait_for_operation(compute, project_id, zone, operation['name'])
    print('instances created.')

    instances = list_instances(compute, project_id, zone, instance_name)
    print('instances are below:')
    for instance in instances:
        print (instance["name"])
        # print (instance)


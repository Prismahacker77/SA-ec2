import boto3

def get_public_subnets(ec2, vpc_id):
    public_subnets = set()
    route_tables = ec2.describe_route_tables(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
    )['RouteTables']

    for rt in route_tables:
        for route in rt['Routes']:
            if route.get('GatewayId', '').startswith('igw-'):  # Check if route has an Internet Gateway
                for assoc in rt['Associations']:
                    if assoc.get('SubnetId'):
                        public_subnets.add(assoc['SubnetId'])

    return public_subnets

def scan_ec2_instances():
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    for region in regions:
        print(f"Scanning region: {region}")
        ec2 = boto3.client('ec2', region_name=region)
        instances = ec2.describe_instances()['Reservations']

        for reservation in instances:
            for instance in reservation['Instances']:
                vpc_id = instance.get('VpcId')
                subnet_id = instance.get('SubnetId')
                
                if vpc_id and subnet_id:
                    public_subnets = get_public_subnets(ec2, vpc_id)
                    if subnet_id in public_subnets:
                        instance_id = instance['InstanceId']
                        instance_type = instance['InstanceType']
                        print(f"Region: {region}")
                        print(f"VPC ID: {vpc_id}")
                        print(f"Subnet ID: {subnet_id} (Public Subnet)")
                        print(f"Instance ID: {instance_id}")
                        print(f"Instance Type: {instance_type}")
                        print("-" * 60)

if __name__ == "__main__":
    scan_ec2_instances()
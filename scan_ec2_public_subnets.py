import boto3

def get_public_subnets(ec2, vpc_id):
    public_subnets = set()
    route_tables = ec2.describe_route_tables(
        Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
    )['RouteTables']

    for rt in route_tables:
        for route in rt['Routes']:
            # Check if the route destination is 0.0.0.0/0 and the target is an Internet Gateway
            if route.get('DestinationCidrBlock') == '0.0.0.0/0' and route.get('GatewayId', '').startswith('igw-'):
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
                instance_id = instance['InstanceId']
                vpc_id = instance.get('VpcId')
                subnet_id = instance.get('SubnetId')
                public_ip = instance.get('PublicIpAddress')
                
                if vpc_id and subnet_id:
                    public_subnets = get_public_subnets(ec2, vpc_id)
                    if subnet_id in public_subnets and public_ip:
                        print(f"Region: {region}")
                        print(f"VPC ID: {vpc_id}")
                        print(f"Subnet ID: {subnet_id} (Public Subnet)")
                        print(f"Instance ID: {instance_id}")
                        print(f"Public IP: {public_ip}")
                        print("-" * 60)

if __name__ == "__main__":
    scan_ec2_instances()
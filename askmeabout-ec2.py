import boto3

def get_regions():
    ec2_client = boto3.client('ec2')
    return [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

def get_public_subnets(ec2, vpc_id):
    public_subnets = set()
    route_tables = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']

    for rt in route_tables:
        for route in rt['Routes']:
            if route.get('DestinationCidrBlock') == '0.0.0.0/0' and route.get('GatewayId', '').startswith('igw-'):
                for assoc in rt['Associations']:
                    if assoc.get('SubnetId'):
                        public_subnets.add(assoc['SubnetId'])

    return public_subnets

def get_instances(ec2, region):
    return ec2.describe_instances()['Reservations']

def scan_ec2_instances():
    regions = get_regions()

    for region in regions:
        print(f"Scanning region: {region}")
        ec2 = boto3.client('ec2', region_name=region)
        instances = get_instances(ec2, region)

        for reservation in instances:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                vpc_id = instance.get('VpcId')
                subnet_id = instance.get('SubnetId')
                public_ip = instance.get('PublicIpAddress')

                print(f"Instance ID: {instance_id}, VPC ID: {vpc_id}, Subnet ID: {subnet_id}, Public IP: {public_ip}")
                
                if vpc_id and subnet_id:
                    public_subnets = get_public_subnets(ec2, vpc_id)
                    if subnet_id in public_subnets and public_ip:
                        print(f"  Internet Accessible: Yes")
                        print(f"  Instance ID: {instance_id}")
                        print(f"  Public IP: {public_ip}")
                        print(f"  VPC ID: {vpc_id}")
                        print(f"  Subnet ID: {subnet_id} (Public Subnet)")
                        print("-" * 60)

if __name__ == "__main__":
    scan_ec2_instances()
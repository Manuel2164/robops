#!/usr/bin/env python3
import boto3, time, argparse, sys, json

iot = boto3.client('iot', region_name='us-east-1')
iotdata = boto3.client('iot-data', region_name='us-east-1')

def deploy_canary(version, fleet):
    robots = get_fleet_robots(fleet)
    canary_robot = robots[0]

    print(f"[CANARY] Deploying v{version[:8]} to {canary_robot}...")
    trigger_deployment(canary_robot, version, fault_mode="false")

    print("[CANARY] Waiting 30s for sensor data...")
    time.sleep(30)

    if health_check(canary_robot):
        print("[CANARY] Health check passed, rolling out to full fleet")
        for robot in robots[1:]:
            trigger_deployment(robot, version, fault_mode="false")
        print("[DEPLOY] Full fleet updated successfully")
    else:
        print("[CANARY] Health check FAILED, triggering rollback")
        rollback(canary_robot)
        sys.exit(1)

def health_check(robot_name):
    try:
        response = iotdata.get_thing_shadow(thingName=robot_name)
        shadow = json.loads(response['payload'].read())
        temp = shadow['state']['reported'].get('temperature', 0)
        print(f"[HEALTH] {robot_name} temperature: {temp}")
        return temp < 100.0
    except Exception as e:
        print(f"[HEALTH] Error reading shadow: {e}")
        return False

def rollback(robot_name):
    print(f"[ROLLBACK] Reverting {robot_name} to previous stable version")
    trigger_deployment(robot_name, "stable", fault_mode="false")

def get_fleet_robots(fleet):
    response = iot.list_things_in_thing_group(thingGroupName=fleet)
    return response['things']

def trigger_deployment(robot, version, fault_mode):
    iotdata.update_thing_shadow(
        thingName=robot,
        payload=json.dumps({
            "state": {"desired": {
                "version": version,
                "fault_mode": fault_mode
            }}
        })
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', required=True)
    parser.add_argument('--fleet', required=True)
    args = parser.parse_args()
    deploy_canary(args.version, args.fleet)

from flask import Flask, request, jsonify, send_file, render_template
import os
import csv
import random
from datetime import datetime, timedelta
from collections import deque

app = Flask(__name__)

# Initialize trucks with initial random battery levels between 40% and 80%
def initialize_trucks(num_trucks, max_battery_capacity, start_batteries=None):
    if start_batteries:
        return {f'truck{i+1}': {'battery': start_batteries[f'truck{i+1}'], 'status': 'Running'} for i in range(num_trucks)}
    else:
        return {f'truck{i+1}': {'battery': random.uniform(0.4, 0.8) * max_battery_capacity, 'status': 'Running'} for i in range(num_trucks)}

# Helper function to determine charging power demand based on battery percentage
def get_charging_power_demand(battery, max_battery_capacity, charging_power_demands):
    battery_percentage = battery / max_battery_capacity
    if battery_percentage <= 0.85:
        return charging_power_demands['low']
    elif battery_percentage <= 0.95:
        return charging_power_demands['medium']
    else:
        return charging_power_demands['high']

# Function to simulate one day and return the truck statuses and battery levels
def simulate_day(trucks, max_battery_capacity, average_consumption_per_hour, critical_level, ok_level, charging_power_demands, max_charger_power, num_guns, num_chargers, schedule):
    start_batteries = {truck: params['battery'] for truck, params in trucks.items()}
    result = []
    queue = deque()
    status_counters = {truck: {'Running': 0, 'Charging': 0, 'Waiting': 0, 'Idle': 0} for truck in trucks.keys()}
    load_profile = [{'hour': f'{hour:02}', 'peak_power': 0, 'total_energy': 0} for hour in range(24)]
    
    for hour in range(24):
        for minute in range(60):
            current_time = f'{hour:02}:{minute:02}'
            schedule_status = 'Break'
            for event in schedule:
                event_name, event_start, event_end = event
                if event_start <= current_time < event_end:
                    schedule_status = event_name
                    break
            
            charging_trucks = [[] for _ in range(num_chargers)]
            power_demands = [[] for _ in range(num_chargers)]
            row = {'minute': current_time, 'schedule': schedule_status}

            for truck, params in trucks.items():
                battery_start = params['battery']
                status = params['status']
                charging_power_demand = 0
                assigned_gun = None
                assigned_charger = None

                if schedule_status == 'Work':
                    if battery_start <= critical_level or status == 'Charging':
                        if sum(len(c) for c in charging_trucks) < (num_guns * num_chargers) or status == 'Charging':
                            status = 'Charging'
                            charging_power_demand = get_charging_power_demand(battery_start, max_battery_capacity, charging_power_demands) / 60  # kW to kWh per minute
                            if params['battery'] >= ok_level:
                                status = 'Running'
                                charging_power_demand = 0  # Reset charging power demand when switching to running
                            if status == 'Charging':
                                # Find the charger with the most available power
                                best_charger = None
                                max_available_power = 0
                                for charger_index in range(num_chargers):
                                    available_power = max_charger_power - sum([demand for demand in power_demands[charger_index]])
                                    if available_power > max_available_power:
                                        max_available_power = available_power
                                        best_charger = charger_index

                                if best_charger is not None:
                                    assigned_charger = best_charger + 1
                                    gun_index = len(charging_trucks[best_charger]) + 1
                                    assigned_gun = f'C{assigned_charger}-G{gun_index}'
                                    charging_trucks[best_charger].append((truck, params, charging_power_demand))
                        else:
                            status = 'Waiting'
                            if truck not in queue:
                                queue.append(truck)
                    else:
                        status = 'Running'
                        power_consumption = average_consumption_per_hour / 60  # kWh per minute
                        params['battery'] -= power_consumption
                        if params['battery'] < 0:
                            params['battery'] = 0

                elif schedule_status == 'Break':
                    if battery_start < max_battery_capacity:
                        if sum(len(c) for c in charging_trucks) < (num_guns * num_chargers) or status == 'Charging':
                            status = 'Charging'
                            charging_power_demand = get_charging_power_demand(battery_start, max_battery_capacity, charging_power_demands) / 60  # kW to kWh per minute
                            if status == 'Charging':
                                # Find the charger with the most available power
                                best_charger = None
                                max_available_power = 0
                                for charger_index in range(num_chargers):
                                    available_power = max_charger_power - sum([demand for demand in power_demands[charger_index]])
                                    if available_power > max_available_power:
                                        max_available_power = available_power
                                        best_charger = charger_index

                                if best_charger is not None:
                                    assigned_charger = best_charger + 1
                                    gun_index = len(charging_trucks[best_charger]) + 1
                                    assigned_gun = f'C{assigned_charger}-G{gun_index}'
                                    charging_trucks[best_charger].append((truck, params, charging_power_demand))
                        else:
                            status = 'Waiting'
                            if truck not in queue:
                                queue.append(truck)
                    else:
                        status = 'Idle'

                params['status'] = status
                status_counters[truck][status] += 1

                if status == 'Charging' and assigned_charger is not None:
                    power_demands[assigned_charger - 1].append(charging_power_demand)

                row.update({
                    f'{truck}_status': status,
                    f'{truck}_battery_start': round(battery_start, 2),
                    f'{truck}_battery_end': round(params['battery'], 2),
                    f'{truck}_charging_power_demand': round(charging_power_demand, 2),
                    f'{truck}_state_of_charge': f"{round((params['battery'] / max_battery_capacity) * 100)}%",  # State of charge in percentage
                    f'{truck}_assigned_gun': assigned_gun
                })

            total_power_given = 0

            # Distribute power for each charger
            for charger_index in range(num_chargers):
                charger_power_demand = sum(power_demands[charger_index])
                if charger_power_demand > (max_charger_power / 60):  # Convert to kWh per minute
                    # Share power proportionally within this charger
                    available_power_per_minute = max_charger_power / 60  # Convert to kWh per minute
                    for truck, params, charging_power_demand in charging_trucks[charger_index]:
                        proportion = charging_power_demand / charger_power_demand
                        power_given = proportion * available_power_per_minute
                        params['battery'] += power_given
                        if params['battery'] > max_battery_capacity:
                            params['battery'] = max_battery_capacity
                        row.update({
                            f'{truck}_battery_end': round(params['battery'], 2),
                            f'{truck}_power_given': round(power_given, 2),
                            f'{truck}_state_of_charge': f"{round((params['battery'] / max_battery_capacity) * 100)}%"  # State of charge in percentage
                        })
                        total_power_given += power_given
                else:
                    # All trucks get their demanded power within this charger
                    for truck, params, charging_power_demand in charging_trucks[charger_index]:
                        power_given = charging_power_demand  # Since total power demand is within the charger's capacity
                        params['battery'] += power_given
                        if params['battery'] > max_battery_capacity:
                            params['battery'] = max_battery_capacity
                        row.update({
                            f'{truck}_battery_end': round(params['battery'], 2),
                            f'{truck}_power_given': round(power_given, 2),
                            f'{truck}_state_of_charge': f"{round((params['battery'] / max_battery_capacity) * 100)}%"  # State of charge in percentage
                        })
                        total_power_given += power_given

            # Process the queue
            while sum(len(c) for c in charging_trucks) < (num_guns * num_chargers) and queue:
                next_truck = queue.popleft()
                params = trucks[next_truck]
                charging_power_demand = get_charging_power_demand(params['battery'], max_battery_capacity, charging_power_demands) / 60  # kW to kWh per minute
                if params['battery'] < max_battery_capacity:
                    params['status'] = 'Charging'
                    best_charger = None
                    max_available_power = 0
                    for charger_index in range(num_chargers):
                        available_power = max_charger_power - sum([demand for demand in power_demands[charger_index]])
                        if available_power > max_available_power:
                            max_available_power = available_power
                            best_charger = charger_index

                    if best_charger is not None:
                        assigned_charger = best_charger + 1
                        gun_index = len(charging_trucks[best_charger]) + 1
                        assigned_gun = f'C{assigned_charger}-G{gun_index}'
                        charging_trucks[best_charger].append((next_truck, params, charging_power_demand))
                        power_demands[best_charger].append(charging_power_demand)
                        row[f'{next_truck}_assigned_gun'] = assigned_gun

            row['total_power_given'] = round(total_power_given, 2)
            result.append(row)

            # Update load profile for the hour
            if total_power_given > load_profile[hour]['peak_power']:
                load_profile[hour]['peak_power'] = total_power_given
            load_profile[hour]['total_energy'] += total_power_given
    
    end_batteries = {truck: params['battery'] for truck, params in trucks.items()}
    return start_batteries, end_batteries, result, status_counters, load_profile

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.json
    num_trucks = int(data['num_trucks'])
    max_battery_capacity = float(data['max_battery_capacity'])
    average_consumption_per_hour = float(data['average_consumption_per_hour'])
    num_chargers = int(data['num_chargers'])
    num_guns = int(data['num_guns'])

    # Define charging power demands based on battery percentage
    charging_power_demands = {
        'low': 600,  # kW when battery <= 85% of max capacity
        'medium': 450,  # kW when 85% < battery <= 95% of max capacity
        'high': 150  # kW when battery > 95% of max capacity
    }

    critical_level = 0.1 * max_battery_capacity  # 10% of max capacity
    ok_level = 0.5 * max_battery_capacity  # 50% of max capacity

    max_charger_power = 600  # kW

    # Define work schedule
    schedule = [
        ('Break', '00:00', '00:15'),
        ('Work', '00:15', '03:20'),
        ('Break', '03:20', '04:30'),
        ('Work', '04:30', '07:40'),
        ('Break', '07:40', '08:15'),
        ('Work', '08:15', '11:30'),
        ('Break', '11:30', '12:20'),
        ('Work', '12:20', '15:40'),
        ('Break', '15:40', '16:15'),
        ('Work', '16:15', '19:30'),
        ('Break', '19:30', '20:30'),
        ('Work', '20:30', '23:30'),
        ('Break', '23:30', '00:00')
    ]

    num_days_to_simulate = 100
    best_day = None
    smallest_difference = float('inf')
    best_result = None
    best_status_counters = None
    best_load_profile = None

    # Initialize trucks for the first day
    trucks = initialize_trucks(num_trucks, max_battery_capacity)
    start_batteries = {truck: params['battery'] for truck, params in trucks.items()}

    for day in range(num_days_to_simulate):
        trucks = initialize_trucks(num_trucks, max_battery_capacity, start_batteries)
        start_batteries, end_batteries, result, status_counters, load_profile = simulate_day(
            trucks, max_battery_capacity, average_consumption_per_hour, critical_level, ok_level, charging_power_demands, max_charger_power, num_guns, num_chargers, schedule)
        total_difference = sum(abs(end_batteries[truck] - start_batteries[truck]) for truck in trucks.keys())

        if total_difference < smallest_difference:
            smallest_difference = total_difference
            best_day = day
            best_result = result
            best_status_counters = status_counters
            best_load_profile = load_profile

        # Use end batteries as start batteries for the next day
        start_batteries = end_batteries

    # Write the results of the best day to a CSV file
    output_path = 'truck_charging_simulation.csv'
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['minute', 'schedule', 'total_power_given']
        for truck in initialize_trucks(num_trucks, max_battery_capacity).keys():
            fieldnames += [
                f'{truck}_status', f'{truck}_battery_start', f'{truck}_battery_end',
                f'{truck}_charging_power_demand', f'{truck}_power_given', f'{truck}_state_of_charge', f'{truck}_assigned_gun'
            ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in best_result:
            writer.writerow(row)
        
        # Write total times at the bottom in hours
        writer.writerow({})
        writer.writerow({'minute': 'Total Times'})
        for status in ['Running', 'Charging', 'Waiting', 'Idle']:
            row = {'minute': status}
            for truck, counters in best_status_counters.items():
                row[f'{truck}_status'] = round(counters[status] / 60, 2)  # Convert minutes to hours
            writer.writerow(row)

    # Write the load profile to a separate CSV file
    load_profile_path = 'truck_charging_load_profile.csv'
    total_energy = sum(hour_profile['total_energy'] for hour_profile in best_load_profile)

    with open(load_profile_path, 'w', newline='') as csvfile:
        fieldnames = ['hour', 'peak_power', 'total_energy']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for hour_profile in best_load_profile:
            writer.writerow({
                'hour': hour_profile['hour'],
                'peak_power': round(hour_profile['peak_power'] * 60, 2),  # kW
                'total_energy': round(hour_profile['total_energy'], 2)  # kWh
            })
        
        # Write total energy at the bottom
        writer.writerow({})
        writer.writerow({'hour': 'Total Energy', 'peak_power': '', 'total_energy': round(total_energy, 2)})

    return jsonify({'success': True, 'csv_url': f'/download/{output_path}', 'load_profile_url': f'/download/{load_profile_path}', 'total_times': best_status_counters, 'load_profile': best_load_profile})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Truck Charging Simulation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }
        .container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 800px;
            text-align: center;
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
        }
        h2 {
            color: #333;
            font-size: 20px;
            margin-top: 30px;
            margin-bottom: 10px;
        }
        label {
            display: block;
            margin-top: 10px;
            color: #555;
        }
        input[type="number"] {
            width: calc(100% - 22px);
            padding: 8px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            margin-top: 20px;
            padding: 10px 15px;
            border: none;
            background-color: #28a745;
            color: #fff;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #218838;
        }
        p {
            margin-top: 15px;
            color: #333;
        }
        a {
            margin-top: 15px;
            display: block;
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        table {
            margin: 0 auto;
            margin-top: 20px;
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            padding: 10px;
            text-align: center;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        .waiting-cell {
            color: red;
        }
        canvas {
            margin-top: 20px;
            width: 100%;
            height: 400px;
        }
        .scroll-top-padding {
            padding-top: 60px; /* Add extra padding to ensure input table is fully visible */
        }
    </style>
</head>
<body>
    <div class="container scroll-top-padding">
        <h1>Truck Charging Simulation</h1>
        <form id="simulationForm">
            <label for="num_trucks">Number of Trucks:</label>
            <input type="number" id="num_trucks" name="num_trucks" value="5"><br>

            <label for="max_battery_capacity">Max Battery Capacity (kWh):</label>
            <input type="number" id="max_battery_capacity" name="max_battery_capacity" value="700"><br>

            <label for="average_consumption_per_hour">Average Consumption per Hour (kWh):</label>
            <input type="number" id="average_consumption_per_hour" name="average_consumption_per_hour" value="99"><br>

            <label for="num_chargers">Number of Chargers:</label>
            <input type="number" id="num_chargers" name="num_chargers" value="2"><br>

            <label for="num_guns">Number of Guns per Charger:</label>
            <input type="number" id="num_guns" name="num_guns" value="3"><br>

            <button type="submit">Run Simulation</button>
        </form>
        <p id="status"></p>
        <a id="downloadLink" style="display:none;" download>Download Simulation CSV</a>
        <a id="loadProfileLink" style="display:none;" download>Download Load Profile CSV</a>
    </div>

    <div class="container">
        <h2 id="activityHoursHeader" style="display:none;">Truck Activity Hours</h2>
        <table id="totalTimesTable" style="display:none;">
            <thead>
                <tr id="totalTimesHeader"></tr>
            </thead>
            <tbody id="totalTimesBody"></tbody>
        </table>
    </div>

    <div class="container">
        <h2 id="loadProfileHeader" style="display:none;">Load Profile</h2>
        <canvas id="loadProfileChart" style="display:none;"></canvas>
        <p id="totalDailyEnergy" style="display:none;"></p>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        document.getElementById('simulationForm').addEventListener('submit', async function(event) {
            event.preventDefault();

            document.getElementById('status').innerText = 'Running simulation...';
            document.getElementById('downloadLink').style.display = 'none';
            document.getElementById('loadProfileLink').style.display = 'none';
            document.getElementById('activityHoursHeader').style.display = 'none';
            document.getElementById('totalTimesTable').style.display = 'none';
            document.getElementById('loadProfileHeader').style.display = 'none';
            document.getElementById('loadProfileChart').style.display = 'none';
            document.getElementById('totalDailyEnergy').style.display = 'none';

            const formData = new FormData(event.target);
            const params = Object.fromEntries(formData.entries());

            const response = await fetch('/run_simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });

            const result = await response.json();
            if (result.success) {
                document.getElementById('status').innerText = 'Simulation completed successfully!';
                const downloadLink = document.getElementById('downloadLink');
                downloadLink.href = result.csv_url;
                downloadLink.style.display = 'block';
                downloadLink.innerText = 'Download Simulation CSV';

                const loadProfileLink = document.getElementById('loadProfileLink');
                loadProfileLink.href = result.load_profile_url;
                loadProfileLink.style.display = 'block';
                loadProfileLink.innerText = 'Download Load Profile CSV';

                // Display total times as a table
                const totalTimesHeader = document.getElementById('totalTimesHeader');
                const totalTimesBody = document.getElementById('totalTimesBody');
                totalTimesHeader.innerHTML = '<th>Status</th>';
                totalTimesBody.innerHTML = '';
                const statuses = ['Running', 'Charging', 'Waiting', 'Idle'];

                const trucks = Object.keys(result.total_times);
                for (const truck of trucks) {
                    totalTimesHeader.innerHTML += `<th>${truck}</th>`;
                }

                for (const status of statuses) {
                    const row = document.createElement('tr');
                    row.innerHTML = `<td>${status}</td>`;
                    for (const truck of trucks) {
                        const timeValue = (result.total_times[truck][status] / 60).toFixed(2);
                        const cellClass = status === 'Waiting' && parseFloat(timeValue) > 0 ? 'waiting-cell' : '';
                        row.innerHTML += `<td class="${cellClass}">${timeValue}</td>`;
                    }
                    totalTimesBody.appendChild(row);
                }
                document.getElementById('activityHoursHeader').style.display = 'block';
                document.getElementById('totalTimesTable').style.display = 'table';

                // Display load profile as a bar chart
                const loadProfileChart = document.getElementById('loadProfileChart').getContext('2d');
                const labels = result.load_profile.map(hour => hour.hour);
                const data = result.load_profile.map(hour => hour.total_energy);
                if (window.loadProfileChartInstance) {
                    window.loadProfileChartInstance.destroy();
                }
                window.loadProfileChartInstance = new Chart(loadProfileChart, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Total Energy (kWh)',
                            data: data,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: 'Time of Day'
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: 'Energy (kWh)'
                                }
                            }
                        }
                    }
                });
                document.getElementById('loadProfileHeader').style.display = 'block';
                document.getElementById('loadProfileChart').style.display = 'block';

                // Display total daily energy consumption
                const totalDailyEnergy = data.reduce((acc, value) => acc + value, 0).toFixed(2);
                document.getElementById('totalDailyEnergy').innerText = `Total Daily Energy Consumption: ${totalDailyEnergy} kWh`;
                document.getElementById('totalDailyEnergy').style.display = 'block';

                // Scroll to the top of the page
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } else {
                document.getElementById('status').innerText = 'Simulation failed. Please try again.';
            }
        });
    </script>
</body>
</html>

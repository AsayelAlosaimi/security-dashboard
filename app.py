# Security Dashboard - Network Threat Monitoring Tool
# Simulates real-time security events and visualizes them on an interactive dashboard

from flask import Flask, render_template
import pandas as pd
import random
from datetime import datetime, timedelta
import plotly.express as px
import folium

app = Flask(__name__)

def generate_fake_logs():
    """
    Generates 50 simulated security log entries.
    Each entry includes a timestamp, source IP, event type, and severity level.
    """
    events = []

    event_types = ["Failed Login", "Port Scan", "Suspicious Traffic", "Brute Force", "Normal"]

    ip_addresses = [
        "192.168.1.10",
        "10.0.0.5",
        "172.16.0.3",
        "192.168.1.55",
        "10.10.10.1"
    ]

    # Map each event type to a severity level
    severity_map = {
        "Normal": "Low",
        "Failed Login": "Medium",
        "Port Scan": "Medium",
        "Brute Force": "High",
        "Suspicious Traffic": "High"
    }

    for _ in range(50):
        event = random.choice(event_types)
        events.append({
            "time": (datetime.now() - timedelta(minutes=random.randint(1, 120))).strftime("%H:%M:%S"),
            "ip": random.choice(ip_addresses),
            "event": event,
            "severity": severity_map[event]
        })

    return events


@app.route("/")
def index():
    """
    Main route that renders the security dashboard.
    Processes log data and passes charts, stats, and map to the template.
    """
    logs = generate_fake_logs()
    df = pd.DataFrame(logs)

    # Count events by severity level
    high_count = len(df[df["severity"] == "High"])
    medium_count = len(df[df["severity"] == "Medium"])
    low_count = len(df[df["severity"] == "Low"])

    # Prepare event count data in a consistent order
    event_counts = df["event"].value_counts().reindex(
        ["Brute Force", "Suspicious Traffic", "Failed Login", "Port Scan", "Normal"],
        fill_value=0
    ).reset_index()
    event_counts.columns = ["event", "count"]

    # Assign colors based on threat severity
    color_map = {
        "Brute Force": "#db1005",
        "Suspicious Traffic": "#f1ac0b",
        "Failed Login": "#262627",
        "Port Scan": "#ee358b",
        "Normal": "#d6d6e2"
    }

    # Build bar chart for event types
    event_fig = px.bar(
        event_counts,
        x="event",
        y="count",
        color="event",
        text="count",
        color_discrete_map=color_map
    )
    event_fig.update_layout(
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font_color="#c9d1d9",
        margin=dict(l=20, r=20, t=20, b=20),
        width=550,
        height=350,
        showlegend=False
    )
    event_fig.update_yaxes(rangemode="tozero")
    event_chart = event_fig.to_html(full_html=False)

    # Build pie chart for top source IPs
    ip_fig = px.pie(
        df["ip"].value_counts().reset_index(),
        names="ip",
        values="count"
    )
    ip_fig.update_layout(
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font_color="#c9d1d9",
        margin=dict(l=20, r=20, t=20, b=20),
        width=550,
        height=350
    )
    ip_chart = ip_fig.to_html(full_html=False)

    # Map each IP to a real-world geographic location
    ip_locations = {
        "192.168.1.10": [24.7136, 46.6753, "Riyadh"],
        "10.0.0.5": [40.7128, -74.0060, "New York"],
        "172.16.0.3": [51.5074, -0.1278, "London"],
        "192.168.1.55": [35.6762, 139.6503, "Tokyo"],
        "10.10.10.1": [48.8566, 2.3522, "Paris"]
    }

    # Build interactive threat map using Folium
    threat_map = folium.Map(location=[20, 0], zoom_start=2,
                            tiles="CartoDB dark_matter")

    for ip, data in ip_locations.items():
        count = len(df[df["ip"] == ip])
        folium.CircleMarker(
            location=[data[0], data[1]],
            radius=count * 2,
            color="#f85149",
            fill=True,
            fill_color="#f85149",
            fill_opacity=0.7,
            popup=f"{ip} — {data[2]} — {count} events"
        ).add_to(threat_map)

    map_html = threat_map._repr_html_()

    return render_template("index.html",
                           logs=logs,
                           high_count=high_count,
                           medium_count=medium_count,
                           low_count=low_count,
                           total=len(logs),
                           event_chart=event_chart,
                           ip_chart=ip_chart,
                           map_html=map_html)


if __name__ == "__main__":
    app.run(debug=True)
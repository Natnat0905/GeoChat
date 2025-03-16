import time
import matplotlib.pyplot as plt
from locust import HttpUser, task, between, events

class RailwayLoadTest(HttpUser):
    wait_time = between(1, 2)  
    host = "https://web-openaiapikey.up.railway.app"  # API Base URL

    @task
    def test_api(self):
        payload = {"message": "897 times 567"}  # Example JSON data
        headers = {"Content-Type": "application/json"}  # Set correct headers
        
        response = self.client.post("/chat", json=payload, headers=headers)
        print(f"Response: {response.status_code} - {response.text}")  # Debug output

# Collecting Metrics
response_times = []
request_timestamps = []
start_time = time.time()

@events.request.add_listener
def on_request_success(request_type, name, response_time, response_length, **kwargs):
    response_times.append(response_time)
    request_timestamps.append(time.time() - start_time)

@events.quitting.add_listener
def visualize_results(environment, **kwargs):
    """Visualize results with Matplotlib when Locust finishes."""
    if not response_times:
        print("No data to visualize.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(request_timestamps, response_times, marker="o", linestyle="-", color="b", alpha=0.6, label="Response Time (ms)")

    plt.xlabel("Time (seconds)")
    plt.ylabel("Response Time (ms)")
    plt.title("API Load Test - Response Times Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()

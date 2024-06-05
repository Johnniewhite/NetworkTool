import speedtest
import subprocess
import concurrent.futures
import time

def get_network_name():
    """
    Get the name of the current network.

    Returns:
        str: The network name or an error message.
    """
    try:
        result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True, timeout=2)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def measure_speed():
    """
    Measure the download and upload speed, and latency.

    Returns:
        tuple: Download speed (Mbps), upload speed (Mbps), and ping (ms).
    """
    s = speedtest.Speedtest()
    s.get_best_server()
    download_speed = s.download() / 1_000_000  # Convert to Mbps
    upload_speed = s.upload() / 1_000_000  # Convert to Mbps
    ping = s.results.ping  # Ping in ms
    return download_speed, upload_speed, ping

def measure_jitter():
    """
    Measure the jitter using multiple ping tests.

    Returns:
        float: The jitter value (ms).
    """
    latencies = []
    for _ in range(5):  # Reduced to 5 for faster execution
        try:
            result = subprocess.run(["ping", "-c", "1", "8.8.8.8"], capture_output=True, text=True, timeout=2)
            output = result.stdout
            time_line = [line for line in output.splitlines() if "time=" in line][0]
            latency = float(time_line.split("time=")[1].split(" ms")[0])
            latencies.append(latency)
        except Exception:
            pass
    if len(latencies) < 2:
        return 0
    return max(latencies) - min(latencies)

def measure_packet_loss():
    """
    Measure the packet loss percentage.

    Returns:
        float: Packet loss percentage.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "10", "8.8.8.8"],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout
        lines = output.splitlines()
        packet_loss_line = [line for line in lines if "packet loss" in line][0]
        packet_loss = float(packet_loss_line.split("%")[0].split()[-1])
        return packet_loss
    except Exception as e:
        return f"Error: {e}"

def run_network_tests():
    """
    Run all network tests concurrently and gather results.

    Returns:
        dict: Results of network tests.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_network_name = executor.submit(get_network_name)
        future_speed = executor.submit(measure_speed)
        future_jitter = executor.submit(measure_jitter)
        future_packet_loss = executor.submit(measure_packet_loss)
        
        network_name = future_network_name.result()
        download_speed, upload_speed, ping = future_speed.result()
        jitter = future_jitter.result()
        packet_loss = future_packet_loss.result()

    return {
        'network_name': network_name,
        'download_speed': download_speed,
        'upload_speed': upload_speed,
        'latency': ping,
        'jitter': jitter,
        'packet_loss': packet_loss
    }

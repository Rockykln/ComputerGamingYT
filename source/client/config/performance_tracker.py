import psutil
import time
from collections import deque
from datetime import datetime, timedelta
import threading

class PerformanceTracker:
	def __init__(self, history_hours=2):
		self.history_hours = history_hours
		self.metrics = {
			'cpu': deque(maxlen=720),
			'memory': deque(maxlen=720),
			'disk': deque(maxlen=720),
			'network': deque(maxlen=720)
		}
		self.running = False
		self.lock = threading.Lock()

	def start(self):
		self.running = True
		self.collection_thread = threading.Thread(target=self._collect_metrics)
		self.collection_thread.daemon = True
		self.collection_thread.start()

	def stop(self):
		self.running = False

	def _collect_metrics(self):
		while self.running:
			with self.lock:
				timestamp = datetime.now()
				self.metrics['cpu'].append((timestamp, psutil.cpu_percent(interval=1)))
				self.metrics['memory'].append((timestamp, psutil.virtual_memory().percent))
				self.metrics['disk'].append((timestamp, psutil.disk_usage('/').percent))
				net_io = psutil.net_io_counters()
				self.metrics['network'].append((timestamp, (net_io.bytes_sent, net_io.bytes_recv)))
			time.sleep(10) 

	def get_metrics(self, hours=None):
		if hours is None:
			hours = self.history_hours

		cutoff_time = datetime.now() - timedelta(hours=hours)
		with self.lock:
			return {
				'cpu': [(t, v) for t, v in self.metrics['cpu'] if t > cutoff_time],
				'memory': [(t, v) for t, v in self.metrics['memory'] if t > cutoff_time],
				'disk': [(t, v) for t, v in self.metrics['disk'] if t > cutoff_time],
				'network': [(t, v) for t, v in self.metrics['network'] if t > cutoff_time]
			}

performance_tracker = PerformanceTracker()
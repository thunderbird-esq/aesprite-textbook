#!/usr/bin/env python3
"""
production_monitoring.py - Real-time monitoring and alerting for the production pipeline
"""

import time
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import psutil
import logging
from collections import deque, defaultdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import numpy as np
from queue import Queue, Empty
import schedule
import plotly.graph_objs as go
import plotly.offline as pyo

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types of metrics to monitor"""
    GENERATION_TIME = "generation_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    CACHE_HIT_RATE = "cache_hit_rate"
    ERROR_RATE = "error_rate"
    QUEUE_SIZE = "queue_size"
    THROUGHPUT = "throughput"
    API_LATENCY = "api_latency"

@dataclass
class Alert:
    """Alert data structure"""
    timestamp: datetime
    severity: AlertSeverity
    metric_type: MetricType
    message: str
    value: float
    threshold: float
    context: Dict = field(default_factory=dict)
    acknowledged: bool = False
    
@dataclass
class Metric:
    """Metric data point"""
    timestamp: datetime
    metric_type: MetricType
    value: float
    tags: Dict = field(default_factory=dict)
    
class MetricsCollector:
    """Collect and store metrics"""
    
    def __init__(self, db_path: str = "metrics.db", retention_days: int = 30):
        self.db_path = db_path
        self.retention_days = retention_days
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        
        # In-memory buffers for recent metrics
        self.recent_metrics = defaultdict(lambda: deque(maxlen=1000))
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                tags TEXT,
                INDEX idx_timestamp (timestamp),
                INDEX idx_metric_type (metric_type)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                severity TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                message TEXT NOT NULL,
                value REAL NOT NULL,
                threshold REAL NOT NULL,
                context TEXT,
                acknowledged BOOLEAN DEFAULT 0,
                INDEX idx_alert_timestamp (timestamp),
                INDEX idx_alert_severity (severity)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_metric(self, metric_type: MetricType, value: float, 
                     tags: Optional[Dict] = None):
        """Record a metric data point"""
        
        metric = Metric(
            timestamp=datetime.now(),
            metric_type=metric_type,
            value=value,
            tags=tags or {}
        )
        
        with self.lock:
            # Add to in-memory buffer
            self.recent_metrics[metric_type].append(metric)
            
            # Store in database
            self._store_metric(metric)
    
    def _store_metric(self, metric: Metric):
        """Store metric in database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO metrics (timestamp, metric_type, value, tags)
            VALUES (?, ?, ?, ?)
        """, (
            metric.timestamp,
            metric.metric_type.value,
            metric.value,
            json.dumps(metric.tags)
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_metrics(self, metric_type: MetricType, 
                          minutes: int = 60) -> List[Metric]:
        """Get recent metrics from memory or database"""
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self.lock:
            # First check in-memory buffer
            recent = [m for m in self.recent_metrics[metric_type] 
                     if m.timestamp >= cutoff_time]
            
            if not recent or len(recent) < 10:
                # Fetch from database if needed
                recent = self._fetch_metrics_from_db(metric_type, cutoff_time)
        
        return recent
    
    def _fetch_metrics_from_db(self, metric_type: MetricType, 
                               since: datetime) -> List[Metric]:
        """Fetch metrics from database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, value, tags 
            FROM metrics 
            WHERE metric_type = ? AND timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT 1000
        """, (metric_type.value, since))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append(Metric(
                timestamp=datetime.fromisoformat(row[0]),
                metric_type=metric_type,
                value=row[1],
                tags=json.loads(row[2]) if row[2] else {}
            ))
        
        conn.close()
        return metrics
    
    def cleanup_old_data(self):
        """Remove old data beyond retention period"""
        
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff,))
        cursor.execute("DELETE FROM alerts WHERE timestamp < ?", (cutoff,))
        
        deleted_metrics = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Cleaned up {deleted_metrics} old metric records")

class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.logger = logging.getLogger(__name__)
        
        # Alert thresholds
        self.thresholds = {
            MetricType.MEMORY_USAGE: 0.85,  # 85% memory usage
            MetricType.CPU_USAGE: 0.90,     # 90% CPU usage
            MetricType.ERROR_RATE: 0.05,    # 5% error rate
            MetricType.CACHE_HIT_RATE: 0.50, # Below 50% cache hits
            MetricType.QUEUE_SIZE: 1000,    # Queue backup
            MetricType.API_LATENCY: 5.0,    # 5 second latency
            MetricType.GENERATION_TIME: 60.0, # 60 second generation
            MetricType.THROUGHPUT: 0.1       # Below 0.1 items/sec
        }
        
        # Alert cooldown to prevent spam
        self.last_alert_time = {}
        self.alert_cooldown = timedelta(minutes=15)
        
        # Alert callbacks
        self.alert_handlers = []
        
    def check_threshold(self, metric_type: MetricType, value: float) -> Optional[Alert]:
        """Check if metric exceeds threshold"""
        
        threshold = self.thresholds.get(metric_type)
        if threshold is None:
            return None
        
        # Different comparison for different metrics
        if metric_type in [MetricType.CACHE_HIT_RATE, MetricType.THROUGHPUT]:
            # These should be above threshold
            if value < threshold:
                severity = self._calculate_severity(value, threshold, below=True)
                return Alert(
                    timestamp=datetime.now(),
                    severity=severity,
                    metric_type=metric_type,
                    message=f"{metric_type.value} below threshold",
                    value=value,
                    threshold=threshold
                )
        else:
            # These should be below threshold
            if value > threshold:
                severity = self._calculate_severity(value, threshold, below=False)
                return Alert(
                    timestamp=datetime.now(),
                    severity=severity,
                    metric_type=metric_type,
                    message=f"{metric_type.value} exceeded threshold",
                    value=value,
                    threshold=threshold
                )
        
        return None
    
    def _calculate_severity(self, value: float, threshold: float, 
                           below: bool = False) -> AlertSeverity:
        """Calculate alert severity based on how far from threshold"""
        
        if below:
            ratio = value / threshold
            if ratio < 0.5:
                return AlertSeverity.CRITICAL
            elif ratio < 0.75:
                return AlertSeverity.ERROR
            else:
                return AlertSeverity.WARNING
        else:
            ratio = value / threshold
            if ratio > 2.0:
                return AlertSeverity.CRITICAL
            elif ratio > 1.5:
                return AlertSeverity.ERROR
            else:
                return AlertSeverity.WARNING
    
    def process_alert(self, alert: Alert):
        """Process and send alert if needed"""
        
        # Check cooldown
        last_time = self.last_alert_time.get(alert.metric_type)
        if last_time and datetime.now() - last_time < self.alert_cooldown:
            return  # Skip due to cooldown
        
        # Store alert
        self._store_alert(alert)
        
        # Update cooldown
        self.last_alert_time[alert.metric_type] = datetime.now()
        
        # Notify handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")
    
    def _store_alert(self, alert: Alert):
        """Store alert in database"""
        
        conn = sqlite3.connect(self.collector.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts 
            (timestamp, severity, metric_type, message, value, threshold, context, acknowledged)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.timestamp,
            alert.severity.value,
            alert.metric_type.value,
            alert.message,
            alert.value,
            alert.threshold,
            json.dumps(alert.context),
            alert.acknowledged
        ))
        
        conn.commit()
        conn.close()
    
    def add_handler(self, handler):
        """Add alert handler callback"""
        self.alert_handlers.append(handler)

class SystemMonitor:
    """Monitor system resources"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval: int = 10):
        """Start monitoring system resources"""
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"System monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("System monitoring stopped")
    
    def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        
        while self.monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.collector.record_metric(
                    MetricType.CPU_USAGE,
                    cpu_percent / 100.0
                )
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.collector.record_metric(
                    MetricType.MEMORY_USAGE,
                    memory.percent / 100.0,
                    tags={'available_mb': memory.available / 1024 / 1024}
                )
                
                # Disk usage
                disk = psutil.disk_usage('/')
                if disk.percent > 90:
                    self.logger.warning(f"Disk usage high: {disk.percent}%")
                
                # Process-specific metrics
                process = psutil.Process()
                self.collector.record_metric(
                    MetricType.MEMORY_USAGE,
                    process.memory_percent() / 100.0,
                    tags={'process': 'workbook_generator'}
                )
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
            
            time.sleep(interval)

class PipelineMonitor:
    """Monitor the generation pipeline"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.logger = logging.getLogger(__name__)
        
        # Track generation statistics
        self.generation_times = deque(maxlen=100)
        self.error_counts = deque(maxlen=100)
        self.cache_hits = 0
        self.cache_misses = 0
        self.queue_sizes = deque(maxlen=100)
        
    def record_generation(self, element_id: str, duration: float, 
                         success: bool = True):
        """Record generation metrics"""
        
        self.generation_times.append(duration)
        
        self.collector.record_metric(
            MetricType.GENERATION_TIME,
            duration,
            tags={'element_id': element_id, 'success': success}
        )
        
        if not success:
            self.error_counts.append(1)
        else:
            self.error_counts.append(0)
        
        # Calculate error rate
        if len(self.error_counts) > 10:
            error_rate = sum(self.error_counts) / len(self.error_counts)
            self.collector.record_metric(MetricType.ERROR_RATE, error_rate)
    
    def record_cache_access(self, hit: bool):
        """Record cache access"""
        
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        total = self.cache_hits + self.cache_misses
        if total > 0 and total % 10 == 0:  # Record every 10 accesses
            hit_rate = self.cache_hits / total
            self.collector.record_metric(MetricType.CACHE_HIT_RATE, hit_rate)
    
    def record_queue_size(self, size: int):
        """Record queue size"""
        
        self.queue_sizes.append(size)
        self.collector.record_metric(MetricType.QUEUE_SIZE, size)
    
    def record_throughput(self, items_processed: int, duration: float):
        """Record processing throughput"""
        
        if duration > 0:
            throughput = items_processed / duration
            self.collector.record_metric(MetricType.THROUGHPUT, throughput)
    
    def record_api_latency(self, api_name: str, latency: float):
        """Record API latency"""
        
        self.collector.record_metric(
            MetricType.API_LATENCY,
            latency,
            tags={'api': api_name}
        )

class NotificationService:
    """Send notifications for alerts"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def send_email(self, alert: Alert):
        """Send email notification"""
        
        if not self.config.get('email_enabled', False):
            return
        
        smtp_config = self.config['smtp']
        recipients = self.config['recipients']
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_config['from_address']
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.metric_type.value}"
        
        body = f"""
Alert Details:
--------------
Time: {alert.timestamp}
Severity: {alert.severity.value}
Metric: {alert.metric_type.value}
Message: {alert.message}
Value: {alert.value:.2f}
Threshold: {alert.threshold:.2f}
Context: {json.dumps(alert.context, indent=2)}
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        try:
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                if smtp_config.get('use_tls'):
                    server.starttls()
                if smtp_config.get('username'):
                    server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
                
            self.logger.info(f"Alert email sent to {recipients}")
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
    
    def send_webhook(self, alert: Alert):
        """Send webhook notification"""
        
        if not self.config.get('webhook_enabled', False):
            return
        
        webhook_url = self.config['webhook_url']
        
        payload = {
            'timestamp': alert.timestamp.isoformat(),
            'severity': alert.severity.value,
            'metric_type': alert.metric_type.value,
            'message': alert.message,
            'value': alert.value,
            'threshold': alert.threshold,
            'context': alert.context
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            self.logger.info(f"Alert webhook sent to {webhook_url}")
        except Exception as e:
            self.logger.error(f"Failed to send webhook: {e}")
    
    def send_log(self, alert: Alert):
        """Log alert to file"""
        
        log_message = (
            f"ALERT [{alert.severity.value.upper()}] "
            f"{alert.metric_type.value}: {alert.message} "
            f"(value={alert.value:.2f}, threshold={alert.threshold:.2f})"
        )
        
        if alert.severity == AlertSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif alert.severity == AlertSeverity.ERROR:
            self.logger.error(log_message)
        elif alert.severity == AlertSeverity.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

class DashboardGenerator:
    """Generate monitoring dashboards"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.logger = logging.getLogger(__name__)
        
    def generate_dashboard(self, output_path: str = "dashboard.html"):
        """Generate HTML dashboard with charts"""
        
        # Create subplots
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'CPU Usage', 'Memory Usage',
                'Generation Time', 'Cache Hit Rate',
                'Error Rate', 'Throughput'
            )
        )
        
        # CPU Usage
        cpu_metrics = self.collector.get_recent_metrics(MetricType.CPU_USAGE, 60)
        if cpu_metrics:
            times = [m.timestamp for m in cpu_metrics]
            values = [m.value * 100 for m in cpu_metrics]
            fig.add_trace(
                go.Scatter(x=times, y=values, name='CPU %'),
                row=1, col=1
            )
        
        # Memory Usage
        mem_metrics = self.collector.get_recent_metrics(MetricType.MEMORY_USAGE, 60)
        if mem_metrics:
            times = [m.timestamp for m in mem_metrics]
            values = [m.value * 100 for m in mem_metrics]
            fig.add_trace(
                go.Scatter(x=times, y=values, name='Memory %'),
                row=1, col=2
            )
        
        # Generation Time
        gen_metrics = self.collector.get_recent_metrics(MetricType.GENERATION_TIME, 60)
        if gen_metrics:
            times = [m.timestamp for m in gen_metrics]
            values = [m.value for m in gen_metrics]
            fig.add_trace(
                go.Scatter(x=times, y=values, name='Gen Time (s)'),
                row=2, col=1
            )
        
        # Cache Hit Rate
        cache_metrics = self.collector.get_recent_metrics(MetricType.CACHE_HIT_RATE, 60)
        if cache_metrics:
            times = [m.timestamp for m in cache_metrics]
            values = [m.value * 100 for m in cache_metrics]
            fig.add_trace(
                go.Scatter(x=times, y=values, name='Cache Hit %'),
                row=2, col=2
            )
        
        # Error Rate
        error_metrics = self.collector.get_recent_metrics(MetricType.ERROR_RATE, 60)
        if error_metrics:
            times = [m.timestamp for m in error_metrics]
            values = [m.value * 100 for m in error_metrics]
            fig.add_trace(
                go.Scatter(x=times, y=values, name='Error %'),
                row=3, col=1
            )
        
        # Throughput
        throughput_metrics = self.collector.get_recent_metrics(MetricType.THROUGHPUT, 60)
        if throughput_metrics:
            times = [m.timestamp for m in throughput_metrics]
            values = [m.value for m in throughput_metrics]
            fig.add_trace(
                go.Scatter(x=times, y=values, name='Items/sec'),
                row=3, col=2
            )
        
        # Update layout
        fig.update_layout(
            title='Klutz Workbook Generation Monitor',
            showlegend=False,
            height=800
        )
        
        # Save to HTML
        pyo.plot(fig, filename=output_path, auto_open=False)
        self.logger.info(f"Dashboard generated: {output_path}")
        
        return output_path

class MonitoringOrchestrator:
    """Orchestrate all monitoring components"""
    
    def __init__(self, config_path: str = "monitoring_config.json"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize components
        self.collector = MetricsCollector(
            db_path=self.config.get('db_path', 'metrics.db'),
            retention_days=self.config.get('retention_days', 30)
        )
        
        self.alert_manager = AlertManager(self.collector)
        self.system_monitor = SystemMonitor(self.collector)
        self.pipeline_monitor = PipelineMonitor(self.collector)
        self.dashboard_generator = DashboardGenerator(self.collector)
        
        # Set up notifications
        self.notification_service = NotificationService(
            self.config.get('notifications', {})
        )
        
        # Register alert handlers
        self.alert_manager.add_handler(self.notification_service.send_log)
        if self.config.get('notifications', {}).get('email_enabled'):
            self.alert_manager.add_handler(self.notification_service.send_email)
        if self.config.get('notifications', {}).get('webhook_enabled'):
            self.alert_manager.add_handler(self.notification_service.send_webhook)
        
        # Schedule periodic tasks
        self._schedule_tasks()
        
        self.logger = logging.getLogger(__name__)
        
    def _schedule_tasks(self):
        """Schedule periodic maintenance tasks"""
        
        # Generate dashboard every 5 minutes
        schedule.every(5).minutes.do(self.dashboard_generator.generate_dashboard)
        
        # Clean up old data daily
        schedule.every().day.at("02:00").do(self.collector.cleanup_old_data)
        
        # Check for alerts every minute
        schedule.every().minute.do(self._check_alerts)
    
    def _check_alerts(self):
        """Check metrics for alert conditions"""
        
        # Check each metric type
        for metric_type in MetricType:
            recent = self.collector.get_recent_metrics(metric_type, minutes=5)
            if recent:
                # Use average of recent values
                avg_value = np.mean([m.value for m in recent])
                
                alert = self.alert_manager.check_threshold(metric_type, avg_value)
                if alert:
                    self.alert_manager.process_alert(alert)
    
    def start(self):
        """Start monitoring"""
        
        self.logger.info("Starting monitoring orchestrator...")
        
        # Start system monitoring
        self.system_monitor.start_monitoring(
            interval=self.config.get('system_monitor_interval', 10)
        )
        
        # Start scheduled tasks
        self.schedule_thread = threading.Thread(target=self._run_schedule, daemon=True)
        self.schedule_thread.start()
        
        self.logger.info("Monitoring orchestrator started")
    
    def _run_schedule(self):
        """Run scheduled tasks"""
        
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """Stop monitoring"""
        
        self.logger.info("Stopping monitoring orchestrator...")
        
        # Stop system monitoring
        self.system_monitor.stop_monitoring()
        
        # Note: Schedule thread will stop when program exits (daemon=True)
        
        self.logger.info("Monitoring orchestrator stopped")
    
    def get_status(self) -> Dict:
        """Get current monitoring status"""
        
        # Get recent alerts
        conn = sqlite3.connect(self.collector.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT severity, COUNT(*) 
            FROM alerts 
            WHERE timestamp > datetime('now', '-1 hour')
            GROUP BY severity
        """)
        
        alert_counts = dict(cursor.fetchall())
        
        conn.close()
        
        # Get current metrics
        current_metrics = {}
        for metric_type in MetricType:
            recent = self.collector.get_recent_metrics(metric_type, minutes=5)
            if recent:
                current_metrics[metric_type.value] = {
                    'current': recent[0].value,
                    'average': np.mean([m.value for m in recent])
                }
        
        return {
            'status': 'running',
            'alerts': alert_counts,
            'metrics': current_metrics,
            'cache_stats': {
                'hits': self.pipeline_monitor.cache_hits,
                'misses': self.pipeline_monitor.cache_misses,
                'hit_rate': self.pipeline_monitor.cache_hits / 
                          max(self.pipeline_monitor.cache_hits + 
                              self.pipeline_monitor.cache_misses, 1)
            }
        }


# Usage example
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create configuration
    config = {
        'db_path': 'metrics.db',
        'retention_days': 30,
        'system_monitor_interval': 10,
        'notifications': {
            'email_enabled': False,
            'webhook_enabled': False,
            'smtp': {
                'host': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'from_address': 'monitor@example.com',
                'username': 'user',
                'password': 'pass'
            },
            'recipients': ['admin@example.com'],
            'webhook_url': 'https://hooks.slack.com/services/XXX'
        }
    }
    
    # Save configuration
    with open('monitoring_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Start monitoring
    orchestrator = MonitoringOrchestrator('monitoring_config.json')
    orchestrator.start()
    
    # Simulate some activity
    import random
    
    for i in range(10):
        # Record generation
        duration = random.uniform(1, 10)
        success = random.random() > 0.1
        orchestrator.pipeline_monitor.record_generation(
            f"element_{i}",
            duration,
            success
        )
        
        # Record cache access
        hit = random.random() > 0.3
        orchestrator.pipeline_monitor.record_cache_access(hit)
        
        # Record throughput
        orchestrator.pipeline_monitor.record_throughput(
            random.randint(5, 20),
            10.0
        )
        
        time.sleep(2)
    
    # Generate dashboard
    orchestrator.dashboard_generator.generate_dashboard()
    
    # Get status
    status = orchestrator.get_status()
    print("\nMonitoring Status:")
    print(json.dumps(status, indent=2, default=str))
    
    # Keep running for a bit
    time.sleep(30)
    
    # Stop monitoring
    orchestrator.stop()

from typing import Dict, Any, Optional
import time
from datetime import datetime
import psutil
import requests
from src.utils.logger import get_logger
from src.config.settings import settings

logger = get_logger(__name__)

class SystemMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.error_counts = {
            'api': 0,
            'database': 0,
            'email': 0,
            'github': 0,
            'other': 0
        }
        self.last_check = datetime.utcnow()

    def get_system_metrics(self) -> Dict[str, Any]:
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'cpu_percent': process.cpu_percent(),
                'memory_used': memory_info.rss / 1024 / 1024,  # MB
                'uptime': time.time() - self.start_time,
                'error_counts': self.error_counts,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            return {}

    def record_error(self, error_type: str, error_message: str) -> None:
        try:
            if error_type in self.error_counts:
                self.error_counts[error_type] += 1
            else:
                self.error_counts['other'] += 1
                
            logger.error(f"{error_type.upper()} Error: {error_message}")
        except Exception as e:
            logger.error(f"Error recording error: {str(e)}")

    def check_system_health(self) -> Dict[str, Any]:
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': settings.APP_VERSION,
                'metrics': self.get_system_metrics()
            }
            
            if self.error_counts['api'] > 100 or self.error_counts['database'] > 50:
                health_status['status'] = 'degraded'
                
            if self.error_counts['email'] > 200 or self.error_counts['github'] > 100:
                health_status['status'] = 'critical'
                
            return health_status
        except Exception as e:
            logger.error(f"Error checking system health: {str(e)}")
            return {
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }

class ErrorHandler:
    def __init__(self):
        self.monitor = SystemMonitor()

    def handle_error(
        self,
        error: Exception,
        error_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            error_info = {
                'type': error_type,
                'message': str(error),
                'timestamp': datetime.utcnow().isoformat(),
                'context': context or {}
            }
            
            self.monitor.record_error(error_type, str(error))
            
            if error_type == 'api':
                return self._handle_api_error(error_info)
            elif error_type == 'database':
                return self._handle_database_error(error_info)
            elif error_type == 'email':
                return self._handle_email_error(error_info)
            elif error_type == 'github':
                return self._handle_github_error(error_info)
            else:
                return self._handle_generic_error(error_info)
                
        except Exception as e:
            logger.error(f"Error in error handler: {str(e)}")
            return {
                'status': 'error',
                'message': 'Error handling failed',
                'original_error': str(error)
            }

    def _handle_api_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'status': 'error',
            'type': 'api',
            'message': 'API request failed',
            'details': error_info
        }

    def _handle_database_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'status': 'error',
            'type': 'database',
            'message': 'Database operation failed',
            'details': error_info
        }

    def _handle_email_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'status': 'error',
            'type': 'email',
            'message': 'Email operation failed',
            'details': error_info
        }

    def _handle_github_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'status': 'error',
            'type': 'github',
            'message': 'GitHub operation failed',
            'details': error_info
        }

    def _handle_generic_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'status': 'error',
            'type': 'generic',
            'message': 'An unexpected error occurred',
            'details': error_info
        }

class AlertManager:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_used': 1024,  # MB
            'error_rate': 0.1  # 10% error rate
        }

    def check_alerts(self) -> List[Dict[str, Any]]:
        try:
            alerts = []
            metrics = self.monitor.get_system_metrics()
            
            if metrics.get('cpu_percent', 0) > self.alert_thresholds['cpu_percent']:
                alerts.append({
                    'type': 'high_cpu',
                    'message': f"CPU usage is high: {metrics['cpu_percent']}%",
                    'severity': 'warning'
                })
                
            if metrics.get('memory_used', 0) > self.alert_thresholds['memory_used']:
                alerts.append({
                    'type': 'high_memory',
                    'message': f"Memory usage is high: {metrics['memory_used']}MB",
                    'severity': 'warning'
                })
                
            total_errors = sum(self.monitor.error_counts.values())
            if total_errors > 0:
                error_rate = total_errors / (time.time() - self.monitor.start_time)
                if error_rate > self.alert_thresholds['error_rate']:
                    alerts.append({
                        'type': 'high_error_rate',
                        'message': f"Error rate is high: {error_rate:.2%}",
                        'severity': 'critical'
                    })
                    
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            return [] 
"""
Simulation Coordinator Service

High-level orchestration of simulation runs.
Coordinates between circuit model, analyzers, and result management.
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class AnalysisType(Enum):
    """Supported analysis types"""
    DC = "dc"
    AC = "ac"
    TRANSIENT = "transient"
    PARAMETRIC = "parametric"
    MONTE_CARLO = "monte_carlo"


class SimulationRequest:
    """Encapsulates a simulation request"""

    def __init__(self, analysis_type: AnalysisType, **kwargs):
        self.analysis_type = analysis_type
        self.parameters = kwargs
        self.id = None
        self.status = 'pending'
        self.results = None


class SimulationCoordinator:
    """
    High-level simulation orchestration.
    
    Responsibilities:
    - Queue simulation requests
    - Coordinate analyzer selection
    - Manage result caching
    - Track simulation history
    """

    def __init__(self):
        self.request_queue = []
        self.result_cache = {}
        self.simulation_history = []

    def submit_request(self, analysis_type: AnalysisType,
                      **parameters) -> str:
        """
        Submit simulation request.
        
        Args:
            analysis_type: Type of analysis to perform
            **parameters: Analysis parameters
            
        Returns:
            Request ID
        """
        import uuid
        request_id = str(uuid.uuid4())
        
        request = SimulationRequest(analysis_type, **parameters)
        request.id = request_id
        
        self.request_queue.append(request)
        return request_id

    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of pending request"""
        for request in self.request_queue:
            if request.id == request_id:
                return {
                    'id': request_id,
                    'status': request.status,
                    'analysis_type': request.analysis_type.value,
                    'parameters': request.parameters
                }
        return None

    def get_cached_result(self, request_id: str) -> Optional[Dict]:
        """Get cached simulation result"""
        return self.result_cache.get(request_id)

    def cache_result(self, request_id: str, result: Dict) -> None:
        """Cache simulation result"""
        self.result_cache[request_id] = result
        self.simulation_history.append({
            'id': request_id,
            'result': result
        })

    def get_simulation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent simulation history"""
        return self.simulation_history[-limit:]

    def clear_cache(self) -> None:
        """Clear result cache"""
        self.result_cache.clear()

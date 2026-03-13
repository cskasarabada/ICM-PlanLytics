# comp_plan/models/schemas.py - Enhanced Pydantic Models
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TemplateName(str, Enum):
    MASTER = "master"
    AUTOMATION_FRAMEWORK = "automation_framework"
    VENDOR_CHECKLIST = "vendor_checklist"
    SIDE_BY_SIDE = "side_by_side"
    SIDE_BY_SIDE_VENDOR_COMPARE = "side_by_side_vendor_compare"
    RISK_ASSESSMENT = "risk_assessment"
    ORACLE_MAPPING = "oracle_mapping"
    QUICK_ANALYSIS = "quick_analysis"


class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AIProvider(str, Enum):
    AUTO = "auto"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    OLLAMA = "ollama"


# Analysis Request Schemas
class AnalysisRequest(BaseModel):
    template: TemplateName
    ai_provider: AIProvider = AIProvider.AUTO
    priority: Priority = Priority.NORMAL
    approach: str = "comprehensive"
    custom_instructions: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: AnalysisStatus
    message: str
    excel_url: Optional[str] = None
    pdf_url: Optional[str] = None
    json_url: Optional[str] = None
    html_url: Optional[str] = None
    file_name: Optional[str] = None
    template: Optional[TemplateName] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None


class AnalysisResult(BaseModel):
    analysis_id: str
    file_name: str
    template: TemplateName
    status: AnalysisStatus
    document_analysis: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    oracle_mapping: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    exports: Optional[Dict[str, str]] = None
    created_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None


# Agent configuration
class AgentConfig(BaseModel):
    agent_type: str
    enabled: bool = True
    model_preference: Optional[str] = None
    timeout_seconds: int = 120


class WorkflowConfig(BaseModel):
    name: str
    description: str
    agents: List[AgentConfig]
    parallel_execution: bool = False
    failure_strategy: str = "continue"


# Export
class ExportRequest(BaseModel):
    analysis_id: str
    format: str  # excel, pdf, json, csv
    include_raw_data: bool = False


class ExportResponse(BaseModel):
    export_id: str
    download_url: str
    file_size: int


# Comparison
class ComparisonRequest(BaseModel):
    analysis_ids: List[str]
    comparison_type: str  # side_by_side, delta, benchmark
    include_recommendations: bool = True


class ComparisonResponse(BaseModel):
    comparison_id: str
    analyses_compared: List[str]
    results: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]


# API Response
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None


class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: datetime
    ai_providers_status: Dict[str, str] = {}

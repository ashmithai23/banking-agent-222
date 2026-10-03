# Request & Response Pydantic Schemas

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., description="Customer financial inquiry or instruction")
    customer_id: Optional[str] = Field("CUST-DEFAULT", description="Unique customer identifier")
    stream: bool = Field(False, description="Whether to request SSE token streaming")

class ToolExecutionResult(BaseModel):
    tool_name: str
    input_parameters: dict
    output_result: dict
    execution_time_ms: float

class AnalysisResponse(BaseModel):
    response: str
    active_agent: str
    tools_invoked: List[ToolExecutionResult] = []
    citations: List[str] = []
    regulatory_flags: List[str] = []
```

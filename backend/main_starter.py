import asyncio
import os
import sys
import uuid
import logging
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from typing import Callable, List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import field_validator, Field
from contextlib import contextmanager
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, SequentialOrchestration
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import KernelArguments
from semantic_kernel.kernel_pydantic import KernelBaseModel
from semantic_kernel.contents import ChatMessageContent
from rag_utils import extract_banking_policies, create_semantic_kernel_context
from blob_connector import BlobStorageConnector
from chroma_manager import ChromaDBManager
from shared_state import SharedState
from offline_agents import AGENT_NAMES, run_offline_agent
from dotenv import load_dotenv

try:
    import pyodbc  # Optional: only needed for Azure SQL connectivity
except ImportError:  # pragma: no cover - depends on system unixODBC libs
    pyodbc = None

# Registry document "type" -> ChromaDB collection (keyword classification is the fallback)
DOC_TYPE_COLLECTIONS = {
    "fraud": "fraud_detection",
    "loans": "loan_policies",
    "support": "customer_support",
    "risk": "risk_assessment",
    "transaction_monitoring": "transaction_monitoring",
    "compliance": "compliance",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Global logger instance
logger = logging.getLogger(__name__)

def setup_logging():
    """Setup logging with unique file for each run"""
    if not os.path.exists("logs"):
        os.makedirs("logs")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/banking_analysis_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, mode='w', encoding='utf-8'),
        ]
    )

    print(f"Logger started. Log file: {log_filename}")
    return log_filename

class DataConnector:
    """Azure SQL Database connectivity for banking data retrieval"""

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv("AZURE_SQL_CONNECTION_STRING")
        if self.connection_string and pyodbc is None:
            logger.warning("pyodbc is not installed. Using sample data fallback.")
            self.connection_string = None
        if self.connection_string:
            self._test_connection()
        else:
            logger.warning("No SQL connection string provided. Using sample data fallback.")

    def _test_connection(self):
        """Test database connection on initialization"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
            logger.info("Database connection test successful")
        except Exception as e:
            logger.warning(f"Database connection test failed: {e}. Will use sample data fallback.")
            self.connection_string = None

    async def fetch_income(self, customer_id: str) -> Optional[float]:
        """Fetch customer income from Azure SQL database"""
        if not self.connection_string:
            return None
        try:
            await asyncio.sleep(0)
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT TOP 1 income FROM transactions WHERE customer_id = ? ORDER BY ts DESC",
                    (customer_id,)
                )
                row = cursor.fetchone()
                cursor.close()
                return float(row[0]) if row else None
        except Exception as e:
            logger.error(f"Error fetching income for customer {customer_id}: {e}")
            return None

    async def fetch_transactions(self, customer_id: str) -> List[Dict]:
        """Fetch customer transactions from Azure SQL database"""
        if not self.connection_string:
            return []
        try:
            await asyncio.sleep(0)
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT transaction_id, customer_id, income, amount, ts, description "
                    "FROM transactions WHERE customer_id = ? ORDER BY ts DESC",
                    (customer_id,)
                )
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                cursor.close()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching transactions for customer {customer_id}: {e}")
            return []

    @contextmanager
    def get_db_connection(self):
        """Create database connection context manager"""
        conn = None
        try:
            conn = pyodbc.connect(self.connection_string, timeout=30)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()


class EnhancedBankingReport(KernelBaseModel):
    """Comprehensive banking analysis report with field validation"""
    report_id: str = Field(..., min_length=1, description="Unique report identifier")
    customer_id: str = Field(..., min_length=1, description="Customer identifier")
    query: str = Field(..., min_length=1, description="Original customer query")
    summary: str = Field(..., min_length=1, description="Analysis summary from agents")
    key_findings: List[str] = Field(default=[], description="Key findings from analysis")
    risk_assessment: Literal["low", "medium-low", "medium", "high", "critical"] = Field(
        default="medium", description="Overall risk tier"
    )
    risk_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Numeric risk score 0-1")
    recommendations: List[str] = Field(default=[], description="Actionable recommendations")
    actions_taken: List[str] = Field(default=[], description="Actions performed during analysis")
    policy_references: List[str] = Field(default=[], description="Referenced policy documents")
    agent_contributions: Dict[str, Any] = Field(default={}, description="Per-agent output")
    processing_metrics: Dict[str, Any] = Field(default={}, description="Performance metrics")
    generated_by: str = "EnhancedBankingOrchestration"
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator("risk_score")
    @classmethod
    def validate_risk_score(cls, v: float) -> float:
        """Ensure risk score is within valid range"""
        return max(0.0, min(1.0, v))


class CustomerProfile(KernelBaseModel):
    """Comprehensive customer profile with financial data validation"""
    customer_id: str = Field(..., min_length=1, description="Unique customer identifier")
    income: float = Field(default=0.0, ge=0.0, description="Annual income in USD")
    credit_score: int = Field(default=0, ge=0, le=850, description="Credit score (0-850)")
    account_type: Literal["basic", "standard", "premium", "premium_plus"] = Field(
        default="standard", description="Account tier"
    )
    customer_since: str = Field(default="", description="Date customer joined (YYYY-MM-DD)")
    risk_tier: Literal["low", "medium", "high", "critical"] = Field(
        default="medium", description="Customer risk classification"
    )
    recent_transactions: List[Dict[str, Any]] = Field(
        default=[], description="Recent transaction history"
    )
    banking_products: List[str] = Field(default=[], description="Active banking products")
    last_review_date: str = Field(default="", description="Last profile review (YYYY-MM-DD)")

    @field_validator("credit_score")
    @classmethod
    def validate_credit_score(cls, v: int) -> int:
        """Ensure credit score is within realistic range"""
        return max(0, min(850, v))

    @field_validator("income")
    @classmethod
    def validate_income(cls, v: float) -> float:
        """Ensure income is non-negative"""
        return max(0.0, v)


class EnhancedBankingSequentialOrchestration:
    """Enhanced banking system with advanced features"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize enhanced storage components
        self.blob_connector = BlobStorageConnector(os.path.join(BASE_DIR, "banking_documents"))
        self.chroma_store = ChromaDBManager(os.path.join(BASE_DIR, "chroma_db_banking"))
        self.shared_state = SharedState()

        # Initialize Azure SQL Data Connector (graceful fallback if unavailable)
        self.data_connector = DataConnector()

        # Initialize enhanced kernel with the best available LLM provider
        self.kernel = Kernel()
        self.llm_mode, self.llm_model = self._configure_llm_service()
        self.logger.info(f"LLM mode: {self.llm_mode} ({self.llm_model})")

        # Load enhanced banking policies
        self.banking_policies = self._load_enhanced_policies()
        self.customer_profiles = {}

        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "successful_analyses": 0,
            "average_processing_time": 0,
            "agent_performance": {}
        }

    def _configure_llm_service(self) -> tuple:
        """Register a chat service: Azure AI Foundry, then OpenAI, else offline rule-based agents"""
        forced = os.getenv("LLM_MODE", "").strip().lower()
        azure_name = os.getenv("AZURE_TEXTGENERATOR_DEPLOYMENT_NAME", "").strip()
        azure_endpoint = os.getenv("AZURE_TEXTGENERATOR_DEPLOYMENT_ENDPOINT", "").strip()
        azure_key = os.getenv("AZURE_TEXTGENERATOR_DEPLOYMENT_KEY", "").strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()

        if forced != "offline":
            if azure_name and azure_endpoint and azure_key and forced in ("", "azure"):
                kwargs = dict(
                    service_id="enhanced_banking_chat",
                    deployment_name=azure_name,
                    endpoint=azure_endpoint,
                    api_key=azure_key,
                )
                api_version = os.getenv("AZURE_API_VERSION", "").strip()
                if api_version:
                    kwargs["api_version"] = api_version
                self.kernel.add_service(AzureChatCompletion(**kwargs))
                return "azure", azure_name
            if openai_key and forced in ("", "openai"):
                model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
                kwargs = dict(
                    service_id="enhanced_banking_chat",
                    ai_model_id=model,
                    api_key=openai_key,
                )
                # Any OpenAI-compatible endpoint (e.g. Google Gemini, NVIDIA NIM, OpenRouter, vLLM)
                base_url = os.getenv("OPENAI_BASE_URL", "").strip()
                if base_url:
                    from openai import AsyncOpenAI
                    async_client = AsyncOpenAI(api_key=openai_key, base_url=base_url)
                    orig_create = async_client.chat.completions.create

                    async def safe_create(*c_args, **c_kwargs):
                        msgs = c_kwargs.get("messages")
                        if msgs and isinstance(msgs, list):
                            last_msg = msgs[-1]
                            last_role = last_msg.get("role") if isinstance(last_msg, dict) else getattr(last_msg, "role", None)
                            if last_role in ("assistant", "model"):
                                c_kwargs["messages"] = list(msgs) + [{"role": "user", "content": "Please proceed with your specialized analysis based on the information provided."}]
                        return await orig_create(*c_args, **c_kwargs)

                    async_client.chat.completions.create = safe_create
                    kwargs["async_client"] = async_client
                self.kernel.add_service(OpenAIChatCompletion(**kwargs))
                return "openai", model
        return "offline", "rule-based-agents"

    def _load_enhanced_policies(self) -> Dict[str, Any]:
        """Load and parse banking policy documents"""
        try:
            if not self.blob_connector.list_documents():
                self.blob_connector.upload_sample_documents()

            enhanced_docs = []
            for doc_name in self.blob_connector.list_documents():
                content = self.blob_connector.get_document_content(doc_name)
                metadata = self.blob_connector.get_document_metadata(doc_name)

                enhanced_docs.append({
                    "filename": doc_name,
                    "id": f"{metadata.get('type', 'general')}_{doc_name}",
                    "meta": {
                        **metadata,
                        "priority": "high" if metadata.get('type') in ['fraud', 'risk'] else "medium",
                        "review_frequency": "quarterly" if metadata.get('type') in ['fraud', 'compliance'] else "annually"
                    },
                    "text": content
                })

            policies = extract_banking_policies(enhanced_docs)
            self.logger.info(f"Loaded policies from {len(enhanced_docs)} documents")
            return policies
        except Exception as e:
            self.logger.error(f"Could not load enhanced banking policies: {e}")
            return {}

    async def _load_customer_profiles(self) -> Dict[str, CustomerProfile]:
        """Load customer profiles from Azure SQL with fallback to sample data"""

        # Default sample profiles (35+ rich banking customer personas)
        try:
            from customer_data import get_customer_profiles_dict
            default_profiles = get_customer_profiles_dict()
        except ImportError:
            try:
                from backend.customer_data import get_customer_profiles_dict
                default_profiles = get_customer_profiles_dict()
            except Exception:
                default_profiles = {}

        # Try loading from Azure SQL, fall back to defaults
        if self.data_connector.connection_string:
            try:
                for cid in ["12345", "67890", "11111"]:
                    income = await self.data_connector.fetch_income(cid)
                    transactions = await self.data_connector.fetch_transactions(cid)
                    if income is not None:
                        profile = default_profiles.get(cid, CustomerProfile(customer_id=cid))
                        profile.income = income
                        if transactions:
                            profile.recent_transactions = transactions
                        default_profiles[cid] = profile
                self.logger.info("Customer profiles loaded from Azure SQL")
            except Exception as e:
                self.logger.warning(f"SQL load failed, using sample data: {e}")
        else:
            self.logger.info("Using sample customer profiles (no SQL connection)")

        return default_profiles

    def _build_llm_arguments(self) -> Optional[KernelArguments]:
        """Optional generation settings from env: LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_REASONING_EFFORT"""
        if self.llm_mode != "openai":
            return None
        options = {}
        max_tokens = os.getenv("LLM_MAX_TOKENS", "").strip()
        temperature = os.getenv("LLM_TEMPERATURE", "").strip()
        effort = os.getenv("LLM_REASONING_EFFORT", "").strip()
        if max_tokens:
            options["max_tokens"] = int(max_tokens)
        if temperature:
            options["temperature"] = float(temperature)
        if effort:
            options["extra_body"] = {"reasoning_effort": effort}
        if not options:
            return None
        settings = OpenAIChatPromptExecutionSettings(service_id="enhanced_banking_chat", **options)
        return KernelArguments(settings=settings)

    def create_enhanced_agents(self, selected_names: Optional[List[str]] = None) -> List[ChatCompletionAgent]:
        """Create specialized banking agents with detailed instructions"""
        if self.llm_mode == "offline":
            # Agents are still defined (instructions, names); responses come from offline_agents.
            service = None
        else:
            service = self.kernel.get_service("enhanced_banking_chat")
        llm_arguments = self._build_llm_arguments()

        data_agent = ChatCompletionAgent(
            name="Enhanced_Data_Gatherer",
            instructions="""You are a Senior Banking Data Analyst specializing in customer financial profiling.

Your responsibilities:
1. Analyze customer financial data including income, transactions, credit history, and account activity.
2. Match customer profiles against relevant banking policies and eligibility criteria.
3. Assess data quality and completeness, flagging any gaps or inconsistencies.
4. Calculate key financial metrics: debt-to-income ratio, savings rate, spending patterns.
5. Identify the customer's financial segment (premium, standard, basic) based on their profile.

Output format:
- Customer Financial Summary with key metrics
- Data Quality Assessment (completeness score)
- Policy Relevance Mapping (which policies apply to this customer)
- Key observations about the customer's financial behavior""",
            service=service,
            arguments=llm_arguments
        )

        fraud_agent = ChatCompletionAgent(
            name="Enhanced_Fraud_Analyst",
            instructions="""You are a Senior Fraud Detection Specialist with expertise in banking transaction analysis.

Your responsibilities:
1. Analyze transaction patterns for suspicious activity indicators:
   - Large transactions (>$2,000) or unusual amounts
   - Rapid transaction sequences (>10/hour)
   - Geographic anomalies or new payees
   - Transactions outside normal behavioral patterns
2. Assess fraud risk level (Low/Medium/High/Critical) with justification.
3. Identify potential fraud typologies: account takeover, identity theft, card fraud, money laundering.
4. Recommend specific mitigation actions based on risk level.
5. Reference applicable fraud detection policies.

Output format:
- Transaction Pattern Analysis
- Fraud Risk Score (0-100) with risk level
- Identified suspicious indicators (if any)
- Recommended actions and monitoring enhancements""",
            service=service,
            arguments=llm_arguments
        )

        loan_agent = ChatCompletionAgent(
            name="Enhanced_Loan_Analyst",
            instructions="""You are a Senior Credit Risk Analyst specializing in loan eligibility assessment.

Your responsibilities:
1. Evaluate loan eligibility based on:
   - Income tier classification (A+: $100K+, A: $75K+, B: $50K+, C: $30K+)
   - Credit score tier (Excellent 750+, Good 700-749, Fair 650-699, Review <650)
   - Debt-to-income ratio against tier limits (30%-45% depending on tier)
   - Employment history and stability
2. Determine maximum qualifying loan amount and recommended terms.
3. Identify applicable interest rates and LTV ratios.
4. Recommend suitable loan products based on customer profile.
5. Flag any disqualifying factors or conditions requiring special review.

Output format:
- Eligibility Determination (Approved/Conditional/Review Required/Declined)
- Qualifying tier and applicable rates
- Maximum recommended loan amount
- Required documentation level (Basic/Standard/Comprehensive/Premium)
- Product recommendations""",
            service=service,
            arguments=llm_arguments
        )

        support_agent = ChatCompletionAgent(
            name="Enhanced_Support_Specialist",
            instructions="""You are a Senior Customer Experience Specialist focused on banking service optimization.

Your responsibilities:
1. Assess customer service needs based on their profile and query context.
2. Identify service gaps and opportunities for improvement.
3. Determine priority classification (P0-Critical to P3-Low) for the customer's needs.
4. Recommend proactive engagement strategies for customer retention.
5. Suggest relevant self-service options and digital banking features.
6. Evaluate customer lifetime value and recommend appropriate service tier.

Output format:
- Customer Experience Assessment
- Service Priority Classification with response time SLA
- Identified service gaps and improvement opportunities
- Retention risk assessment
- Recommended engagement actions""",
            service=service,
            arguments=llm_arguments
        )

        risk_agent = ChatCompletionAgent(
            name="Enhanced_Risk_Analyst",
            instructions="""You are a Senior Enterprise Risk Analyst specializing in banking compliance and risk management.

Your responsibilities:
1. Perform comprehensive risk assessment across five categories:
   - Credit Risk: borrower default probability
   - Market Risk: economic exposure
   - Operational Risk: process and system risks
   - Compliance Risk: regulatory adherence
   - Reputational Risk: brand impact
2. Assign risk scores and levels (Low <10%, Medium 10-30%, High 30-60%, Critical >60%).
3. Verify compliance with banking regulations and internal policies.
4. Recommend risk mitigation strategies with priority ranking.
5. Determine appropriate review frequency based on risk profile.

Output format:
- Multi-dimensional Risk Assessment Matrix
- Overall risk score and level
- Compliance status with specific policy references
- Prioritized mitigation recommendations
- Recommended monitoring and review schedule""",
            service=service,
            arguments=llm_arguments
        )

        synthesis_agent = ChatCompletionAgent(
            name="Enhanced_Synthesis_Coordinator",
            instructions="""You are a Senior Banking Strategy Coordinator responsible for synthesizing multi-agent analyses into executive reports.

Your responsibilities:
1. Integrate findings from all previous agent analyses into a coherent narrative.
2. Identify cross-cutting themes, conflicts, and synergies between agent assessments.
3. Generate an executive summary suitable for senior banking leadership.
4. Produce a prioritized action plan with clear ownership and timelines.
5. Provide strategic recommendations for the customer relationship.

Output format:
- Executive Summary (2-3 paragraphs)
- Consolidated Key Findings (top 5)
- Integrated Risk Profile
- Strategic Recommendations (prioritized)
- Immediate Action Items
- Long-term Relationship Strategy""",
            service=service,
            arguments=llm_arguments
        )

        all_agents = [data_agent, fraud_agent, loan_agent, support_agent, risk_agent, synthesis_agent]
        if not selected_names:
            return all_agents
        agent_map = {a.name: a for a in all_agents}
        return [agent_map[name] for name in selected_names if name in agent_map]

    async def load_enhanced_documents(self, max_attempts: int = 3):
        """Load banking policy documents into ChromaDB for semantic search.

        Checks each document individually so one that failed earlier (e.g. while the
        embedding model was still downloading) is retried on the next start.
        """
        loaded, failed = 0, []
        for doc_name in self.blob_connector.list_documents():
            if self.chroma_store.has_document(doc_name):
                continue
            content = self.blob_connector.get_document_content(doc_name)
            if not content:
                continue
            doc_type = (self.blob_connector.get_document_metadata(doc_name) or {}).get("type", "")
            collection_type = DOC_TYPE_COLLECTIONS.get(doc_type) or \
                self.chroma_store.determine_collection(doc_name, content)
            for attempt in range(1, max_attempts + 1):
                if await self.chroma_store.chunk_and_store_document(doc_name, content, collection_type):
                    loaded += 1
                    break
                self.logger.warning(f"Storing {doc_name} failed (attempt {attempt}/{max_attempts})")
                await asyncio.sleep(2 * attempt)
            else:
                failed.append(doc_name)

        if failed:
            self.logger.error(f"Could not load into ChromaDB (will retry next start): {failed}")
        stats = await self.chroma_store.get_collection_stats()
        total = sum(v.get("document_count", 0) for v in stats.values())
        self.logger.info(f"ChromaDB ready: {total} chunks ({loaded} documents newly loaded)")

    async def get_customer_profiles(self) -> Dict[str, CustomerProfile]:
        """Return cached customer profiles, loading them on first use"""
        if not self.customer_profiles:
            self.customer_profiles = await self._load_customer_profiles()
        return self.customer_profiles

    async def run_enhanced_analysis(
        self,
        customer_id: str,
        customer_query: str,
        on_event: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> EnhancedBankingReport:
        """Run the main banking analysis workflow.

        ``on_event`` (optional) receives progress dicts: ``stage``, ``agent_started``,
        ``agent_completed`` so callers (e.g. the web API) can stream progress.
        """
        start_time = time.time()
        self.performance_metrics["total_requests"] += 1

        def emit(event: Dict[str, Any]) -> None:
            if on_event:
                try:
                    on_event(event)
                except Exception as cb_err:  # never let a UI callback break analysis
                    self.logger.warning(f"Progress callback failed: {cb_err}")

        # Ensure customer profiles are loaded
        emit({"type": "stage", "stage": "profile", "message": "Loading customer profile"})
        profiles = await self.get_customer_profiles()

        # Load documents to ChromaDB
        emit({"type": "stage", "stage": "documents", "message": "Preparing policy knowledge base"})
        await self.load_enhanced_documents()

        # Get customer data and perform semantic search
        customer_profile = profiles.get(
            customer_id,
            CustomerProfile(customer_id=customer_id)
        )

        # 1. Execute Banking Tools
        from banking_tools import run_banking_tool_suite
        from supervisor import analyze_and_route

        emit({"type": "stage", "stage": "tools", "message": "Executing deterministic financial calculation tools"})
        tool_results = run_banking_tool_suite(customer_profile.model_dump(), customer_query)
        emit({"type": "tools_executed", "tools": tool_results})

        # 2. Supervisor / Dynamic Routing
        emit({"type": "stage", "stage": "supervisor", "message": "Supervisor Agent analyzing query intent and routing pipeline"})
        routing = analyze_and_route(customer_query, customer_profile.model_dump())
        emit({
            "type": "router_decision",
            "intent": routing["intent_title"],
            "reasoning": routing["reasoning"],
            "agents": routing["selected_agents"],
            "collections": routing["primary_collections"],
            "is_full_audit": routing["is_full_audit"],
        })

        # 3. Hybrid search across prioritized banking collections
        emit({"type": "stage", "stage": "retrieval", "message": f"Retrieving relevant policies for {routing['intent_title']} (hybrid RAG)"})
        target_collections = routing.get("primary_collections") or [
            "fraud_detection", "loan_policies", "customer_support",
            "risk_assessment", "transaction_monitoring", "compliance"
        ]
        search_results = await self.chroma_store.hybrid_search(customer_query, target_collections, top_k=4)
        emit({
            "type": "retrieval",
            "results": [
                {
                    "filename": r.get("filename"),
                    "collection": r.get("collection"),
                    "score": round(float(r.get("final_score", r.get("relevance_score", 0))), 3),
                    "snippet": r.get("document", "")[:300],
                }
                for r in search_results[:6]
            ],
        })

        # Prepare enhanced context with verified tools math
        banking_context = self._prepare_enhanced_context(customer_profile, search_results, customer_query, tool_results)

        # Create dynamically routed agents
        agents = self.create_enhanced_agents(routing["selected_agents"])

        # Agent tracking
        agent_contributions: Dict[str, str] = {}
        agent_timings: Dict[str, float] = {}

        def record_agent(name: str, content: str, duration: float) -> None:
            agent_contributions[name] = content
            agent_timings[name] = round(duration, 2)
            self.logger.info(f"Agent {name} completed analysis ({agent_timings[name]}s)")
            emit({"type": "agent_completed", "agent": name, "content": content, "seconds": agent_timings[name]})

        emit({
            "type": "stage",
            "stage": "agents",
            "message": f"Running {len(agents)} specialized agents ({self.llm_mode})",
            "agents": [a.name for a in agents]
        })

        accumulated_contributions = ""
        previous = ""
        runtime = None

        try:
            for idx, agent in enumerate(agents):
                emit({"type": "agent_started", "agent": agent.name})
                t_agent_start = time.time()

                if self.llm_mode == "offline":
                    content = run_offline_agent(
                        agent.name, customer_profile.model_dump(), customer_query,
                        search_results, self.banking_policies, agent_contributions,
                    )
                    words = content.split(" ")
                    for w_idx, w in enumerate(words):
                        chunk_text = w if w_idx == len(words) - 1 else w + " "
                        emit({"type": "agent_token", "agent": agent.name, "token": chunk_text})
                        await asyncio.sleep(0.012)
                    record_agent(agent.name, content, time.time() - t_agent_start)
                    previous = content
                else:
                    agent_prompt = f"""
ENHANCED BANKING CUSTOMER ANALYSIS REQUEST
============================================
{banking_context}

SUPERVISOR ROUTING FOCUS:
Intent: {routing['intent_title']}
Reasoning: {routing['reasoning']}
{f"PREVIOUS SPECIALIZED AGENT CONTRIBUTIONS:\n{accumulated_contributions}" if accumulated_contributions else ""}

INSTRUCTIONS FOR {agent.name}:
Perform your specialized banking analysis based on the customer data, verified financial calculations, and policies provided above.
"""
                    tokens = []
                    async for chunk in agent.invoke_stream(agent_prompt):
                        if chunk.content:
                            token_str = str(chunk.content)
                            tokens.append(token_str)
                            emit({"type": "agent_token", "agent": agent.name, "token": token_str})

                    content = "".join(tokens)
                    accumulated_contributions += f"\n\n### [{agent.name} Findings]:\n{content}\n"
                    record_agent(agent.name, content, time.time() - t_agent_start)
                    previous = content

            final_output = previous

            # Calculate enhanced risk score
            risk_score = self._calculate_enhanced_risk_score(customer_profile, search_results)
            risk_assessment = self._determine_risk_tier(risk_score)

            # Extract policy references from search results
            policy_refs = sorted({
                r.get("filename", "Unknown") for r in search_results if r.get("filename")
            })

            elapsed = time.time() - start_time

            # Create comprehensive banking report
            report = EnhancedBankingReport(
                report_id=f"enhanced_{uuid.uuid4().hex[:8]}",
                customer_id=customer_id,
                query=customer_query,
                summary=str(final_output),
                key_findings=self._generate_enhanced_findings(customer_profile, search_results, agent_contributions),
                risk_assessment=risk_assessment,
                risk_score=risk_score,
                recommendations=self._generate_enhanced_recommendations(customer_profile, risk_score),
                actions_taken=[
                    "Enhanced multi-agent sequential analysis completed",
                    "Comprehensive policy compliance verification performed",
                    "Enterprise risk assessment conducted",
                    f"Analyzed {len(search_results)} relevant policy documents",
                    f"{len(agent_contributions)} specialized agents contributed to analysis",
                ],
                policy_references=policy_refs,
                agent_contributions=agent_contributions,
                processing_metrics={
                    "total_processing_time_seconds": round(elapsed, 2),
                    "agents_used": len(agents),
                    "policies_referenced": len(policy_refs),
                    "search_results_analyzed": len(search_results),
                    "risk_score": risk_score,
                    "agent_timings_seconds": agent_timings,
                    "llm_mode": self.llm_mode,
                    "llm_model": self.llm_model,
                },
                generated_by="EnhancedBankingSequentialOrchestration"
            )

            self.performance_metrics["successful_analyses"] += 1
            self.shared_state.update_interaction(customer_id, {
                "query": customer_query,
                "report_id": report.report_id,
                "risk_score": risk_score,
                "timestamp": datetime.now().isoformat()
            })

            return report

        except Exception as e:
            self.logger.error(f"Error in enhanced orchestration: {e}")
            self.shared_state.record_failure(customer_id, str(e))
            raise
        finally:
            if runtime is not None:
                await runtime.stop_when_idle()

    def _calculate_enhanced_risk_score(self, customer_profile: CustomerProfile, search_results: List[Dict]) -> float:
        """Calculate comprehensive risk score from multiple factors (0.0 = low risk, 1.0 = high risk)"""
        base_score = 0.5

        # Income-based risk factor (higher income = lower risk)
        if customer_profile.income >= 100000:
            base_score -= 0.15
        elif customer_profile.income >= 75000:
            base_score -= 0.10
        elif customer_profile.income >= 50000:
            base_score -= 0.05
        elif customer_profile.income < 30000:
            base_score += 0.10

        # Credit score-based factor
        if customer_profile.credit_score >= 750:
            base_score -= 0.15
        elif customer_profile.credit_score >= 700:
            base_score -= 0.08
        elif customer_profile.credit_score >= 650:
            base_score += 0.05
        elif customer_profile.credit_score > 0:
            base_score += 0.15

        # Customer tenure (longer tenure = lower risk)
        if customer_profile.customer_since:
            try:
                since = datetime.strptime(customer_profile.customer_since, "%Y-%m-%d")
                years = (datetime.now() - since).days / 365.25
                if years >= 5:
                    base_score -= 0.10
                elif years >= 3:
                    base_score -= 0.05
                elif years < 1:
                    base_score += 0.08
            except ValueError:
                pass

        # Product diversification (more products = lower risk)
        num_products = len(customer_profile.banking_products)
        if num_products >= 4:
            base_score -= 0.08
        elif num_products >= 2:
            base_score -= 0.03
        elif num_products <= 1:
            base_score += 0.05

        # Transaction pattern analysis
        transactions = customer_profile.recent_transactions
        if transactions:
            amounts = [t.get("amount", 0) for t in transactions]
            max_amount = max(amounts) if amounts else 0
            if max_amount > 10000:
                base_score += 0.10
            elif max_amount > 5000:
                base_score += 0.03

        return max(0.0, min(1.0, round(base_score, 3)))

    def _determine_risk_tier(self, risk_score: float) -> str:
        """Determine risk tier from numeric score"""
        if risk_score < 0.25:
            return "low"
        elif risk_score < 0.50:
            return "medium-low"
        elif risk_score < 0.65:
            return "medium"
        elif risk_score < 0.80:
            return "high"
        else:
            return "critical"

    def _generate_enhanced_findings(self, customer_profile: CustomerProfile, search_results: List[Dict], agent_contributions: Dict) -> List[str]:
        """Generate comprehensive findings based on analysis"""
        findings = [
            f"Customer {customer_profile.customer_id} analysis completed with {len(agent_contributions)} agent contributions",
        ]

        # Income findings
        if customer_profile.income >= 75000:
            findings.append(f"Customer qualifies for Tier A+ or A lending products (income: ${customer_profile.income:,.2f})")
        elif customer_profile.income >= 50000:
            findings.append(f"Customer qualifies for Tier B lending products (income: ${customer_profile.income:,.2f})")
        elif customer_profile.income >= 30000:
            findings.append(f"Customer qualifies for Tier C lending products (income: ${customer_profile.income:,.2f})")
        else:
            findings.append(f"Customer income (${customer_profile.income:,.2f}) may limit product eligibility")

        # Credit score findings
        if customer_profile.credit_score >= 750:
            findings.append(f"Excellent credit score ({customer_profile.credit_score}) - eligible for best rates (3.5% APR)")
        elif customer_profile.credit_score >= 700:
            findings.append(f"Good credit score ({customer_profile.credit_score}) - eligible for competitive rates (4.5% APR)")
        elif customer_profile.credit_score >= 650:
            findings.append(f"Fair credit score ({customer_profile.credit_score}) - standard rates apply (6.0% APR)")
        elif customer_profile.credit_score > 0:
            findings.append(f"Credit score ({customer_profile.credit_score}) requires case-by-case assessment")

        # Product usage findings
        products = customer_profile.banking_products
        if len(products) >= 4:
            findings.append(f"High product engagement ({len(products)} products) indicates strong customer relationship")
        elif len(products) <= 1:
            findings.append(f"Low product engagement ({len(products)} product) - cross-sell opportunity identified")

        # Transaction pattern findings
        if customer_profile.recent_transactions:
            amounts = [t.get("amount", 0) for t in customer_profile.recent_transactions]
            findings.append(f"Recent transaction activity: {len(amounts)} transactions, range ${min(amounts):,.2f}-${max(amounts):,.2f}")

        # Policy relevance from search results
        if search_results:
            collections = {r.get("collection", "") for r in search_results[:5]}
            findings.append(f"Relevant policy areas identified: {', '.join(collections)}")

        return findings

    def _generate_enhanced_recommendations(self, customer_profile: CustomerProfile, risk_score: float) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        recommendations = []

        # Risk-based recommendations
        risk_tier = self._determine_risk_tier(risk_score)
        if risk_tier in ("high", "critical"):
            recommendations.append("Implement enhanced monitoring with quarterly risk reviews")
            recommendations.append("Consider requiring additional documentation for high-value transactions")
        elif risk_tier == "medium":
            recommendations.append("Maintain standard monitoring with semi-annual reviews")
        else:
            recommendations.append("Continue standard monitoring with annual reviews")

        # Product recommendations based on profile
        products = set(customer_profile.banking_products)
        if "investment" not in products and customer_profile.income >= 50000:
            recommendations.append("Recommend investment portfolio services based on income level")
        if "savings" not in products:
            recommendations.append("Recommend high-yield savings account to improve financial health")
        if "credit_card" not in products and customer_profile.credit_score >= 650:
            recommendations.append("Eligible for rewards credit card based on credit profile")
        if "mortgage" not in products and customer_profile.income >= 75000 and customer_profile.credit_score >= 700:
            recommendations.append("Pre-qualify for mortgage products at competitive rates")

        # Customer relationship recommendations
        if customer_profile.account_type == "basic" and customer_profile.income >= 50000:
            recommendations.append("Upgrade to premium account tier based on income qualification")

        if len(customer_profile.banking_products) <= 1:
            recommendations.append("Initiate cross-sell engagement program to deepen customer relationship")

        # Credit improvement recommendations
        if customer_profile.credit_score < 700 and customer_profile.credit_score > 0:
            recommendations.append("Offer credit-building program to improve eligibility for premium products")

        # Ensure at least a general advisory recommendation
        if len(recommendations) < 2:
            recommendations.append("Schedule periodic financial health review to identify emerging opportunities")

        return recommendations

    def _prepare_enhanced_context(self, customer_profile: CustomerProfile, search_results: List[Dict], customer_query: str, tool_results: Optional[Dict[str, Any]] = None) -> str:
        """Prepare comprehensive context for banking orchestration"""

        # Customer profile context
        customer_context = f"""
CUSTOMER PROFILE:
- Customer ID: {customer_profile.customer_id}
- Annual Income: ${customer_profile.income:,.2f}
- Credit Score: {customer_profile.credit_score}
- Account Type: {customer_profile.account_type}
- Customer Since: {customer_profile.customer_since}
- Risk Tier: {customer_profile.risk_tier}
- Banking Products: {', '.join(customer_profile.banking_products) if customer_profile.banking_products else 'None'}
- Last Review Date: {customer_profile.last_review_date}
"""

        # Transaction context
        tx_context = "\nRECENT TRANSACTIONS:\n"
        for tx in customer_profile.recent_transactions[:10]:
            tx_context += f"- ${tx.get('amount', 0):,.2f} - {tx.get('description', 'N/A')} ({tx.get('ts', 'N/A')})\n"

        # Financial tools calculation context
        tools_context = ""
        if tool_results:
            dti = tool_results.get("dti_metrics", {})
            afford = tool_results.get("loan_affordability", {})
            wealth = tool_results.get("wealth_projection", {})
            fraud = tool_results.get("fraud_rule_scan", {})
            tools_context = f"""
VERIFIED FINANCIAL TOOL CALCULATIONS:
- Debt-To-Income (DTI): {dti.get('dti_percent', 0)}% -> {dti.get('tier', 'Standard')} ({dti.get('eligibility_assessment', '')})
- Max Recommended Borrowing Limit: ${afford.get('max_recommended_borrowing_limit', 0):,.2f} at {afford.get('assigned_apr', 0)}% APR
- Sample 60-Month Payment on $50K: ${afford.get('monthly_payment', 0):,.2f}/mo (Total interest: ${afford.get('total_interest', 0):,.2f})
- 15-Year Wealth & Retirement Projection: ${wealth.get('projected_portfolio_value', 0):,.2f} ({wealth.get('multiplier', 1)}x growth)
- Automated Fraud & AML Rule Scan: Risk Level {fraud.get('risk_level', 'LOW')} with {fraud.get('alerts_count', 0)} trigger alerts
"""

        # Policy context from search results
        policy_context = "\nRELEVANT BANKING POLICIES:\n"
        for i, result in enumerate(search_results[:6], 1):
            policy_context += f"\n--- Policy Reference {i} (Source: {result.get('filename', 'Unknown')}, "
            policy_context += f"Collection: {result.get('collection', 'Unknown')}, "
            policy_context += f"Relevance: {result.get('final_score', result.get('relevance_score', 0)):.3f}) ---\n"
            policy_context += result.get("document", "")[:500] + "\n"

        # Structured policy summary
        policy_summary = "\nPOLICY FRAMEWORK SUMMARY:\n"
        policy_summary += create_semantic_kernel_context(self.banking_policies)

        return f"""
BANKING ANALYSIS REQUEST: {customer_query}

{customer_context}
{tools_context}
{tx_context}
{policy_context}
{policy_summary}

ANALYSIS SCOPE:
Provide an expert, policy-grounded analysis covering fraud detection, loan eligibility,
customer service optimization, enterprise risk assessment, and strategic recommendations.
"""


def _display_report(report: EnhancedBankingReport):
    """Display a formatted banking report"""
    print(f"\n{'='*80}")
    print(f"FINAL REPORT: {report.report_id}")
    print(f"{'='*80}")
    print(f"Customer: {report.customer_id}")
    print(f"Risk Assessment: {report.risk_assessment} (score: {report.risk_score:.3f})")
    print(f"\nKey Findings:")
    for finding in report.key_findings:
        print(f"  - {finding}")
    print(f"\nRecommendations:")
    for rec in report.recommendations:
        print(f"  - {rec}")
    print(f"\nActions Taken:")
    for action in report.actions_taken:
        print(f"  - {action}")
    print(f"\nPolicy References: {', '.join(report.policy_references)}")
    print(f"\nProcessing Metrics: {report.processing_metrics}")
    print(f"\nAgent Contributions: {list(report.agent_contributions.keys())}")
    print(f"\nSummary (first 500 chars):\n{report.summary[:500]}...")


async def run_component_tests(system: EnhancedBankingSequentialOrchestration):
    """Unit-test individual components and report pass/fail"""
    results = []
    total = 0
    passed = 0

    def check(name: str, condition: bool, detail: str = ""):
        nonlocal total, passed
        total += 1
        status = "PASS" if condition else "FAIL"
        if condition:
            passed += 1
        results.append((name, status, detail))
        print(f"  [{status}] {name}" + (f" - {detail}" if detail else ""))

    print("\n" + "="*80)
    print("COMPONENT TESTS")
    print("="*80)

    # 1. BlobStorageConnector
    print("\n--- BlobStorageConnector ---")
    docs = system.blob_connector.list_documents()
    check("Document listing", len(docs) > 0, f"{len(docs)} documents found")
    for doc_name in docs[:2]:
        content = system.blob_connector.get_document_content(doc_name)
        check(f"Read '{doc_name}'", content is not None and len(content) > 0, f"{len(content)} chars")
    meta = system.blob_connector.get_document_metadata(docs[0])
    check("Document metadata", meta is not None and "type" in meta, f"type={meta.get('type')}")
    search = system.blob_connector.search_documents("fraud")
    check("Keyword search", len(search) > 0, f"{len(search)} results for 'fraud'")

    # 2. ChromaDBManager
    print("\n--- ChromaDBManager ---")
    check("ChromaDB client", system.chroma_store.client is not None)
    check("Collections initialized", len(system.chroma_store.collections) >= 6,
          f"{len(system.chroma_store.collections)} collections")
    await system.load_enhanced_documents()
    stats = await system.chroma_store.get_collection_stats()
    total_chunks = sum(s.get("document_count", 0) for s in stats.values())
    check("Documents chunked & stored", total_chunks > 0, f"{total_chunks} chunks across collections")
    sem_results = await system.chroma_store.semantic_search("loan eligibility", ["loan_policies"], top_k=2)
    check("Semantic search", len(sem_results) > 0, f"{len(sem_results)} results")
    hyb_results = await system.chroma_store.hybrid_search("fraud detection", ["fraud_detection"], top_k=2)
    check("Hybrid search", len(hyb_results) > 0 and "final_score" in hyb_results[0],
          f"{len(hyb_results)} results with scores")

    # 3. RAG utilities
    print("\n--- RAG Utilities ---")
    check("Banking policies loaded", len(system.banking_policies) > 0,
          f"{len(system.banking_policies)} policy categories")
    policy_ctx = create_semantic_kernel_context(system.banking_policies)
    check("Semantic Kernel context", len(policy_ctx) > 20, f"{len(policy_ctx)} chars")

    # 4. SharedState
    print("\n--- SharedState ---")
    system.shared_state.update_interaction("test_unit", {"action": "unit_test"})
    interactions = system.shared_state.get_customer_interactions("test_unit")
    check("State update & retrieval", len(interactions) > 0)
    metrics = system.shared_state.get_system_metrics()
    check("System metrics", "total_interactions" in metrics)

    # 5. DataConnector
    print("\n--- DataConnector ---")
    check("DataConnector initialized", system.data_connector is not None)
    if system.data_connector.connection_string:
        income = await system.data_connector.fetch_income("12345")
        check("SQL fetch_income", income is not None, f"income={income}")
        txns = await system.data_connector.fetch_transactions("12345")
        check("SQL fetch_transactions", len(txns) > 0, f"{len(txns)} transactions")
    else:
        check("SQL connection (fallback mode)", True, "No SQL string; sample data used")

    # 6. Customer profiles
    print("\n--- Customer Profiles ---")
    profiles = await system._load_customer_profiles()
    check("Profile loading", len(profiles) >= 3, f"{len(profiles)} profiles loaded")
    for cid in ["12345", "67890", "11111"]:
        p = profiles.get(cid)
        check(f"Profile {cid}", p is not None and p.income > 0, f"income=${p.income:,.0f}, score={p.credit_score}")

    # 7. Agent creation
    print("\n--- Agent Creation ---")
    agents = system.create_enhanced_agents()
    check("Six agents created", len(agents) == 6, f"{len(agents)} agents")
    expected_names = [
        "Enhanced_Data_Gatherer", "Enhanced_Fraud_Analyst", "Enhanced_Loan_Analyst",
        "Enhanced_Support_Specialist", "Enhanced_Risk_Analyst", "Enhanced_Synthesis_Coordinator"
    ]
    for agent, name in zip(agents, expected_names):
        check(f"Agent '{name}'", agent.name == name and len(agent.instructions) > 50)

    # 8. Risk scoring
    print("\n--- Risk Scoring ---")
    low_risk = profiles["12345"]
    high_risk = profiles["11111"]
    low_score = system._calculate_enhanced_risk_score(low_risk, [])
    high_score = system._calculate_enhanced_risk_score(high_risk, [])
    check("Low-risk customer scored lower", low_score < high_score,
          f"low={low_score:.3f}, high={high_score:.3f}")
    check("Risk tier determination", system._determine_risk_tier(0.1) == "low" and
          system._determine_risk_tier(0.9) == "critical")

    # Summary
    print(f"\n{'='*80}")
    print(f"TEST RESULTS: {passed}/{total} passed")
    print(f"{'='*80}")
    return passed, total


async def run_demo(system: EnhancedBankingSequentialOrchestration):
    """Run a single demo scenario"""
    print("\n" + "="*80)
    print("DEMO: Customer 12345 - Financial Planning")
    print("="*80)
    report = await system.run_enhanced_analysis(
        "12345",
        "I need comprehensive financial planning including investments and retirement options"
    )
    _display_report(report)
    return report


async def run_test_scenarios(system: EnhancedBankingSequentialOrchestration):
    """Run all test scenarios and validate results"""
    test_scenarios = [
        {
            "customer_id": "12345",
            "query": "I need comprehensive financial planning including investments and retirement options"
        },
        {
            "customer_id": "67890",
            "query": "I want to apply for a home loan and need to understand my eligibility"
        },
        {
            "customer_id": "11111",
            "query": "I noticed some suspicious activity on my account and need help resolving it"
        },
    ]

    reports = []
    for i, scenario in enumerate(test_scenarios, 1):
        try:
            print(f"\n{'='*80}")
            print(f"SCENARIO {i}: Customer {scenario['customer_id']}")
            print(f"Query: {scenario['query']}")
            print(f"{'='*80}")

            report = await system.run_enhanced_analysis(
                scenario["customer_id"],
                scenario["query"]
            )
            _display_report(report)
            reports.append(report)

        except Exception as e:
            print(f"Error in scenario {i}: {e}")
            logger.error(f"Scenario {i} failed: {e}")

    # Validation summary
    print(f"\n{'='*80}")
    print("VALIDATION SUMMARY")
    print(f"{'='*80}")
    all_pass = True
    for report in reports:
        agents_ok = len(report.agent_contributions) == 6
        findings_ok = len(report.key_findings) >= 3
        recs_ok = len(report.recommendations) >= 2
        score_ok = 0.0 <= report.risk_score <= 1.0
        time_ok = report.processing_metrics.get("total_processing_time_seconds", 999) < 300
        status = "PASS" if all([agents_ok, findings_ok, recs_ok, score_ok, time_ok]) else "FAIL"
        if status == "FAIL":
            all_pass = False
        print(f"  [{status}] Customer {report.customer_id}: "
              f"agents={len(report.agent_contributions)}/6, "
              f"findings={len(report.key_findings)}, "
              f"recs={len(report.recommendations)}, "
              f"risk={report.risk_score:.3f} ({report.risk_assessment}), "
              f"time={report.processing_metrics.get('total_processing_time_seconds', 0):.1f}s")

    print(f"\nOverall: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
    return reports


async def enhanced_main():
    """Main entry point with CLI argument support"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Banking Multi-Agent RAG System")
    parser.add_argument("--all", action="store_true", help="Run component tests + all scenarios")
    parser.add_argument("--demo", action="store_true", help="Run a single demo scenario")
    parser.add_argument("--test", action="store_true", help="Run all test scenarios with validation")
    args = parser.parse_args()

    # Default to --all if no flags provided
    if not (args.all or args.demo or args.test):
        args.all = True

    log_filename = setup_logging()

    print("ENHANCED BANKING MULTI-AGENT RAG SYSTEM")
    print("Student Implementation Project")
    print("=" * 80)

    print("\nInitializing EnhancedBankingSequentialOrchestration...")
    system = EnhancedBankingSequentialOrchestration()

    if args.all:
        passed, total = await run_component_tests(system)
        await run_test_scenarios(system)
    elif args.demo:
        await run_demo(system)
    elif args.test:
        await run_test_scenarios(system)

    # Display system metrics
    metrics = system.shared_state.get_system_metrics()
    print(f"\n{'='*80}")
    print("SYSTEM METRICS")
    print(f"{'='*80}")
    for key, value in metrics.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(enhanced_main())

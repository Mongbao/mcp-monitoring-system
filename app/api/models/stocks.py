"""
股票分析資料模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class MarketType(str, Enum):
    """市場類型"""
    TSE = "tse"  # 台灣證券交易所
    OTC = "otc"  # 櫃買中心
    EMERGING = "emerging"  # 興櫃市場
    US = "us"  # 美股
    HK = "hk"  # 港股
    OTHER = "other"  # 其他


class StockCategory(str, Enum):
    """股票類別"""
    TECHNOLOGY = "technology"  # 科技
    FINANCE = "finance"  # 金融
    TRADITIONAL = "traditional"  # 傳產
    BIOTECH = "biotech"  # 生技
    ELECTRONICS = "electronics"  # 電子
    ENERGY = "energy"  # 能源
    CONSTRUCTION = "construction"  # 營建
    FOOD = "food"  # 食品
    TEXTILE = "textile"  # 紡織
    CHEMICAL = "chemical"  # 化工
    OTHER = "other"  # 其他


class TransactionType(str, Enum):
    """交易類型"""
    BUY = "buy"  # 買入
    SELL = "sell"  # 賣出
    DIVIDEND = "dividend"  # 股息
    SPLIT = "split"  # 股票分割
    MERGE = "merge"  # 股票合併


class AnalysisType(str, Enum):
    """分析類型"""
    TECHNICAL = "technical"  # 技術分析
    FUNDAMENTAL = "fundamental"  # 基本面分析
    NEWS = "news"  # 新聞面分析
    SENTIMENT = "sentiment"  # 情緒面分析


class TrendDirection(str, Enum):
    """趨勢方向"""
    BULLISH = "bullish"  # 看漲
    BEARISH = "bearish"  # 看跌
    NEUTRAL = "neutral"  # 中性
    UNKNOWN = "unknown"  # 未知


class RiskLevel(str, Enum):
    """風險等級"""
    LOW = "low"  # 低風險
    MEDIUM = "medium"  # 中風險
    HIGH = "high"  # 高風險
    VERY_HIGH = "very_high"  # 極高風險


# === 基礎資料模型 ===

class StockBasicInfo(BaseModel):
    """股票基本資料"""
    id: str = Field(..., description="股票ID")
    symbol: str = Field(..., description="股票代碼")
    name: str = Field(..., description="股票名稱")
    market: MarketType = Field(..., description="交易市場")
    category: StockCategory = Field(..., description="產業類別")
    industry: Optional[str] = Field(None, description="細分行業")
    description: Optional[str] = Field(None, description="公司簡介")
    website: Optional[str] = Field(None, description="公司網站")
    market_cap: Optional[float] = Field(None, description="市值（億）")
    shares_outstanding: Optional[int] = Field(None, description="已發行股數")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(True, description="是否活躍追蹤")
    tags: List[str] = Field(default_factory=list, description="自定義標籤")
    notes: Optional[str] = Field(None, description="備註")

    @validator('symbol')
    def validate_symbol(cls, v):
        return v.upper().strip()


class StockPriceData(BaseModel):
    """股價資料"""
    id: str = Field(..., description="價格記錄ID")
    stock_id: str = Field(..., description="股票ID")
    date: date = Field(..., description="日期")
    open_price: float = Field(..., description="開盤價")
    high_price: float = Field(..., description="最高價")
    low_price: float = Field(..., description="最低價")
    close_price: float = Field(..., description="收盤價")
    volume: int = Field(..., description="成交量")
    turnover: Optional[float] = Field(None, description="成交金額")
    change: Optional[float] = Field(None, description="漲跌")
    change_percent: Optional[float] = Field(None, description="漲跌幅(%)")
    created_at: datetime = Field(default_factory=datetime.now)


# === 分析資料模型 ===

class TechnicalAnalysis(BaseModel):
    """技術分析記錄"""
    id: str = Field(..., description="分析ID")
    stock_id: str = Field(..., description="股票ID")
    analysis_date: date = Field(..., description="分析日期")
    timeframe: str = Field(..., description="時間週期（日線/週線/月線）")
    
    # 移動平均線
    ma5: Optional[float] = Field(None, description="5日移動平均")
    ma10: Optional[float] = Field(None, description="10日移動平均")
    ma20: Optional[float] = Field(None, description="20日移動平均")
    ma60: Optional[float] = Field(None, description="60日移動平均")
    
    # 技術指標
    rsi: Optional[float] = Field(None, description="RSI相對強弱指標")
    macd: Optional[float] = Field(None, description="MACD")
    macd_signal: Optional[float] = Field(None, description="MACD信號線")
    macd_histogram: Optional[float] = Field(None, description="MACD柱狀圖")
    kd_k: Optional[float] = Field(None, description="KD指標K值")
    kd_d: Optional[float] = Field(None, description="KD指標D值")
    
    # 布林通道
    bb_upper: Optional[float] = Field(None, description="布林通道上軌")
    bb_middle: Optional[float] = Field(None, description="布林通道中軌")
    bb_lower: Optional[float] = Field(None, description="布林通道下軌")
    
    # 支撐壓力
    support_levels: List[float] = Field(default_factory=list, description="支撐價位")
    resistance_levels: List[float] = Field(default_factory=list, description="壓力價位")
    
    # 趨勢判斷
    trend_direction: TrendDirection = Field(..., description="趨勢方向")
    trend_strength: Optional[float] = Field(None, description="趨勢強度(1-10)")
    
    # 分析師備註
    analysis_note: Optional[str] = Field(None, description="技術分析備註")
    created_at: datetime = Field(default_factory=datetime.now)


class FundamentalAnalysis(BaseModel):
    """基本面分析記錄"""
    id: str = Field(..., description="分析ID")
    stock_id: str = Field(..., description="股票ID")
    analysis_date: date = Field(..., description="分析日期")
    quarter: str = Field(..., description="財報季度(如2024Q1)")
    
    # 財務比率
    pe_ratio: Optional[float] = Field(None, description="本益比")
    pb_ratio: Optional[float] = Field(None, description="股價淨值比")
    ps_ratio: Optional[float] = Field(None, description="股價營收比")
    dividend_yield: Optional[float] = Field(None, description="殖利率(%)")
    roe: Optional[float] = Field(None, description="股東權益報酬率(%)")
    roa: Optional[float] = Field(None, description="資產報酬率(%)")
    debt_ratio: Optional[float] = Field(None, description="負債比率(%)")
    current_ratio: Optional[float] = Field(None, description="流動比率")
    quick_ratio: Optional[float] = Field(None, description="速動比率")
    
    # 營收獲利
    revenue: Optional[float] = Field(None, description="營收（千元）")
    net_income: Optional[float] = Field(None, description="淨利（千元）")
    eps: Optional[float] = Field(None, description="每股盈餘")
    
    # 成長率
    revenue_growth: Optional[float] = Field(None, description="營收成長率(%)")
    profit_growth: Optional[float] = Field(None, description="獲利成長率(%)")
    
    # 評價
    fair_value: Optional[float] = Field(None, description="合理價位")
    target_price: Optional[float] = Field(None, description="目標價")
    rating: Optional[str] = Field(None, description="投資評等")
    
    # 風險評估
    risk_level: RiskLevel = Field(..., description="風險等級")
    risk_factors: List[str] = Field(default_factory=list, description="風險因子")
    
    # 分析備註
    analysis_note: Optional[str] = Field(None, description="基本面分析備註")
    created_at: datetime = Field(default_factory=datetime.now)


# === 交易記錄模型 ===

class Transaction(BaseModel):
    """交易記錄"""
    id: str = Field(..., description="交易ID")
    stock_id: str = Field(..., description="股票ID")
    transaction_type: TransactionType = Field(..., description="交易類型")
    transaction_date: date = Field(..., description="交易日期")
    quantity: int = Field(..., description="數量")
    price: float = Field(..., description="價格")
    total_amount: float = Field(..., description="總金額")
    fees: float = Field(0, description="手續費")
    tax: float = Field(0, description="交易稅")
    net_amount: float = Field(..., description="淨額")
    broker: Optional[str] = Field(None, description="券商")
    account: Optional[str] = Field(None, description="帳戶")
    notes: Optional[str] = Field(None, description="交易備註")
    created_at: datetime = Field(default_factory=datetime.now)

    @validator('net_amount', pre=True, always=True)
    def calculate_net_amount(cls, v, values):
        """計算淨額"""
        if v is not None:
            return v
        total = values.get('total_amount', 0)
        fees = values.get('fees', 0)
        tax = values.get('tax', 0)
        return total - fees - tax


class Portfolio(BaseModel):
    """投資組合"""
    id: str = Field(..., description="組合ID")
    name: str = Field(..., description="組合名稱")
    description: Optional[str] = Field(None, description="組合描述")
    total_cost: float = Field(0, description="總成本")
    current_value: float = Field(0, description="目前價值")
    unrealized_pnl: float = Field(0, description="未實現損益")
    realized_pnl: float = Field(0, description="已實現損益")
    total_return: float = Field(0, description="總報酬率(%)")
    risk_level: RiskLevel = Field(..., description="組合風險等級")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(True, description="是否活躍")


class PortfolioHolding(BaseModel):
    """持股明細"""
    id: str = Field(..., description="持股ID")
    portfolio_id: str = Field(..., description="組合ID")
    stock_id: str = Field(..., description="股票ID")
    quantity: int = Field(..., description="持有數量")
    avg_cost: float = Field(..., description="平均成本")
    current_price: float = Field(..., description="目前價格")
    market_value: float = Field(..., description="市值")
    unrealized_pnl: float = Field(..., description="未實現損益")
    unrealized_pnl_percent: float = Field(..., description="未實現損益率(%)")
    weight: float = Field(..., description="持股權重(%)")
    last_updated: datetime = Field(default_factory=datetime.now)


# === 分析筆記模型 ===

class AnalysisNote(BaseModel):
    """分析筆記"""
    id: str = Field(..., description="筆記ID")
    stock_id: str = Field(..., description="股票ID")
    title: str = Field(..., description="筆記標題")
    content: str = Field(..., description="筆記內容")
    analysis_type: AnalysisType = Field(..., description="分析類型")
    tags: List[str] = Field(default_factory=list, description="標籤")
    attachments: List[str] = Field(default_factory=list, description="附件路徑")
    is_public: bool = Field(False, description="是否公開")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# === 請求模型 ===

class StockCreate(BaseModel):
    """創建股票資料請求"""
    symbol: str
    name: str
    market: MarketType
    category: StockCategory
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class StockUpdate(BaseModel):
    """更新股票資料請求"""
    name: Optional[str] = None
    category: Optional[StockCategory] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    market_cap: Optional[float] = None
    shares_outstanding: Optional[int] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class TransactionCreate(BaseModel):
    """創建交易記錄請求"""
    stock_id: str
    transaction_type: TransactionType
    transaction_date: date
    quantity: int
    price: float
    fees: float = 0
    tax: float = 0
    broker: Optional[str] = None
    account: Optional[str] = None
    notes: Optional[str] = None


class AnalysisNoteCreate(BaseModel):
    """創建分析筆記請求"""
    stock_id: str
    title: str
    content: str
    analysis_type: AnalysisType
    tags: List[str] = Field(default_factory=list)
    is_public: bool = False


# === 響應模型 ===

class StockSummary(BaseModel):
    """股票摘要"""
    total_stocks: int = 0
    active_stocks: int = 0
    total_market_value: float = 0
    total_cost: float = 0
    total_pnl: float = 0
    total_return_percent: float = 0
    best_performer: Optional[Dict[str, Any]] = None
    worst_performer: Optional[Dict[str, Any]] = None
    
    
class PortfolioSummary(BaseModel):
    """投資組合摘要"""
    total_portfolios: int = 0
    total_holdings: int = 0
    total_value: float = 0
    total_cost: float = 0
    total_pnl: float = 0
    avg_return: float = 0
    risk_distribution: Dict[str, int] = Field(default_factory=dict)
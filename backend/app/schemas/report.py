from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ReportRequest(BaseModel):
    year: int
    property_id: Optional[UUID] = None


class CategoryMonthlySummary(BaseModel):
    category: str
    amount: Decimal


class MonthlySummary(BaseModel):
    month: int
    rent_collected: Decimal
    total_expenses: Decimal
    income_by_category: list[CategoryMonthlySummary] = []
    expense_by_category: list[CategoryMonthlySummary] = []


class PropertyYearSummary(BaseModel):
    property_id: UUID
    property_name: str
    monthly_summaries: list[MonthlySummary]
    total_rent: Decimal
    total_expenses: Decimal
    income_categories: list[str] = []
    expense_categories: list[str] = []


class YearEndSummary(BaseModel):
    year: int
    properties: list[PropertyYearSummary]

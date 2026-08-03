from pydantic import BaseModel


class AdminDashboardStats(BaseModel):
    total_users: int
    total_products: int
    total_categories: int
    total_deals: int
    total_support_tickets: int
    open_support_tickets: int
    total_analytics_events: int
    total_notifications_sent: int


class AdminUserDTO(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    email_verified: bool
    created_at: str


class AdminUserListResponse(BaseModel):
    users: list[AdminUserDTO]
    total: int

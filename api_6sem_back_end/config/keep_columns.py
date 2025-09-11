columns_to_keep = {
    "Agents": ["AgentId", "FullName", "Email", "IsActive", "DepartmentId"],
    "AuditLogs": ["Operation", "PerformedBy", "DetailsJson"],
    "Categories": ["CategoryId", "Name"],
    "Departments": ["DepartmentId", "Name"],
    "Priorities": ["PriorityId", "Name"],
    "Products": ["ProductId", "Name"],
    "SLA_Plans": ["Name", "FirstResponseMins", "ResolutionMins"],
    "Statuses": ["StatusId", "Name"],
    "Subcategories": ["SubcategoryId", "Name"],
    "Tags": ["Name"],
    "TicketStatusHistory": ["FromStatusId", "ToStatusId"],
    "Tickets": ["Title", "Description", "CreatedAt", "ClosedAt"]
}
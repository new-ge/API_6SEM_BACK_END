columns_to_keep = {
    "Agents": ["AgentId", "FullName", "Email", "IsActive", "DepartmentId", "NivelId"],
    "AuditLogs": ["AuditId", "Operation", "PerformedBy", "DetailsJson", "PerformedAt"],
    "Categories": ["CategoryId", "Name"],
    "Departments": ["DepartmentId", "Name"],
    "Priorities": ["PriorityId", "Name"],
    "Products": ["ProductId", "Name"],
    "SLA_Plans": ["Name", "ResolutionMins", "SLAPlanId"],
    "Statuses": ["StatusId", "Name"],
    "Subcategories": ["SubcategoryId", "Name"],
    "Tags": ["TagId", "Name"],
    "TicketTags": ["TagId", "TicketId"],
    "TicketStatusHistory": ["HistoryId", "TicketId", "FromStatusId", "ToStatusId"],
    "Tickets": ["AssignedAgentId", "TicketId", "Title", "Description", "CreatedAt", "ClosedAt", "CurrentStatusId", "ProductId", "PriorityId", "CategoryId", "SLAPlanId", "SubcategoryId"],
    "AccessLevel": ["NivelId", "Acesso"]
}
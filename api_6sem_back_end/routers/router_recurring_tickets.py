from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]

@router.post("/recurring-tickets")
def recurring_tickets(filtro: Filtro):
    query_filter = build_query_filter(filtro.filtro)

    pipeline = [
    { "$match": query_filter },
      {
        "$project": {
          "recurring_count": {
            "$size": {
              "$filter": {
                "input": "$history",
                "as": "h",
                "cond": {
                    "$and": [
                        { "$in": ["$$h.from", ["Resolvido", "Fechado"]] },
                        { "$or": [
                            { "$not": { "$in": ["$$h.to", ["Resolvido", "Fechado"]] } },
                            { "$eq": ["$$h.to", None] }
                        ]}
                    ]
                }
            }
            }
          }
        }
      },
      {
        "$match": {
          "recurring_count": { "$gt": 0 }
        }
      },
      {
        "$count": "recurring_tickets"
      }
    ]

    result = list(collection.aggregate(pipeline))

    if not result:
        return {"recurring_tickets": 0}

    return {
        "recurring_tickets": result[0]["recurring_tickets"]
    }
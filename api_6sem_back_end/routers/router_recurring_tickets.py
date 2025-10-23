from fastapi import APIRouter, Depends
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro
from api_6sem_back_end.repositories.repository_login_security import verify_token

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db_data["tickets"]

@router.post("/recurring-tickets")
def recurring_tickets(payload=Depends(verify_token), filtro: Filtro = ""):

    role = payload["role"].upper()
    
    if role != "GESTOR":  
        levels_map = {
            "N1": ["N1"],
            "N2": ["N1", "N2"],
            "N3": ["N1", "N2", "N3"]
        }
        allowed_levels = levels_map.get(role, [])
        base_filter = {"access_level": {"$in": allowed_levels}}
    else:
        base_filter = {"access_level": {"$in": ["N1", "N2", "N3"]}}

    query_filter = build_query_filter(filtro, base_filter)

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
from datetime import datetime, timezone, timedelta
from api_6sem_back_end.repositories.update_repository import UpdateRepository

class UpdateService:
    @staticmethod
    def edit_user(data: dict):
        identifier = data.get("identifier")
        update = data.get("update", {})

        if not identifier:
            return {"error": "É necessário fornecer o nome ou e-mail do usuário a ser atualizado"}

        user = UpdateRepository.find_by_name_or_email(identifier)

        if not user:
            return {"error": f"Usuário com nome ou e-mail '{identifier}' não encontrado"}

        agent_id = user.get("agent_id")
        if not agent_id:
            return {"error": "Usuário encontrado não possui agent_id válido"}

        update_fields = {}
        if "name" in update:
            update_fields["name"] = update["name"]
        if "role" in update:
            update_fields["role"] = update["role"]
        if "email" in update:
            update_fields["email"] = update["email"]
            update_fields["login.username"] = update["email"]

        update_fields["modified_at"] = datetime.now(
            timezone(timedelta(hours=-3))
        ).isoformat(timespec="seconds")

        updated = UpdateRepository.update_user(agent_id, update_fields)

        if updated:
            return {"message": f"Usuário '{identifier}' atualizado com sucesso"}
        else:
            return {"error": "Nenhum dado foi alterado"}

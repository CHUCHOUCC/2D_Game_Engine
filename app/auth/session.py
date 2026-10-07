from datetime import datetime, timezone

class Session:

    def __init__(self,user_id,token_hash,expires_at):
        self.user_id = user_id
        self.token_hash = token_hash
        self.expires_at = expires_at

    def is_valid(self) -> bool:
        return datetime.now(timezone.utc) < self.expires_at

    


        
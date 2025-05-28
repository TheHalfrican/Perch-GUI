from dataclasses import dataclass

@dataclass
class Game:
    id: int
    title: str
    file_path: str
    cover_path: str | None
    last_played: str | None
    play_count: int
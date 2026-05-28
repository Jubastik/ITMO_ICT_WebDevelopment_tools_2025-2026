from sqlmodel import SQLModel, Field

class ScrapedPage(SQLModel, table=True):
    """Модель для хранения спарсенных данных."""
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field()
    title: str = Field()

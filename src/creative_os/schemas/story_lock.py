from pydantic import BaseModel, Field


class DialogueTurn(BaseModel):
    speaker: str
    direction: str | None = None
    text: str


class LineItem(BaseModel):
    position: int
    title: str
    quantity: str | None = None
    unit_price: str | None = None
    model: str | None = None
    generation: str | None = None
    variant: str | None = None
    color: str | None = None
    pack_count: int | None = None
    external_id: str | None = None


class Economics(BaseModel):
    subtotal: str | None = None
    discount: str | None = None
    discount_label: str | None = None
    tax: str | None = None
    total: str | None = None
    staged: bool | None = None
    notes: str | None = None


class SlideDocument(BaseModel):
    index: int
    beat: str | None = None
    relative_time: str | None = None
    visible_clock: str | None = None
    visible_date: str | None = None
    overlay: str | None = None
    order_state: str | None = None
    actor_knowledge: str | None = None
    actor_location: str | None = None


class ContinuityFact(BaseModel):
    slide_index: int | None = None
    field: str
    value: str


class TextureDetail(BaseModel):
    slide_index: int | None = None
    text: str
    category: str | None = None


class CommentDoorDocument(BaseModel):
    kind: str
    text: str


class StoryLockDocument(BaseModel):
    title: str
    label: str | None = None
    core_story: str | None = None
    hook: str | None = None
    floating_hook: str | None = None
    stakes: str | None = None
    trigger: str | None = None
    action: str | None = None
    expected_next_beat: str | None = None
    reveal: str | None = None
    commerce_relation: str | None = None
    story_works_without_economics: bool | None = None
    dialogue: list[DialogueTurn] = Field(default_factory=list)
    line_items: list[LineItem] = Field(default_factory=list)
    economics: Economics | None = None
    story_date: str | None = None
    story_weekday: str | None = None
    slides: list[SlideDocument] = Field(default_factory=list)
    continuity: list[ContinuityFact] = Field(default_factory=list)
    comment_doors: list[CommentDoorDocument] = Field(default_factory=list)
    viral_texture: list[TextureDetail] = Field(default_factory=list)
    stale_notes: list[str] = Field(default_factory=list)
    extra: dict[str, str] = Field(default_factory=dict)


class StoryLockCorrection(BaseModel):
    changes: dict[str, str | bool | None]
    actor: str
    reason: str

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey, Text

db = SQLAlchemy()

class Character(db.Model):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    race: Mapped[str] = mapped_column(String(32))
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)  # Cloudinary image URL

    level: Mapped[int] = mapped_column(default=1)
    background: Mapped[str] = mapped_column(Text)
    goal: Mapped[str] = mapped_column(Text)

    health_current: Mapped[int] = mapped_column(default=6)
    health_max: Mapped[int] = mapped_column(default=6)
    mana_current: Mapped[int] = mapped_column(default=3)
    mana_max: Mapped[int] = mapped_column(default=3)

    stats = relationship("Stat", back_populates="character", cascade="all, delete-orphan")
    abilities = relationship("Ability", back_populates="character", cascade="all, delete-orphan")
    spells = relationship("Spell", back_populates="character", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="character", cascade="all, delete-orphan")
    conditions = relationship("Condition", back_populates="character", cascade="all, delete-orphan")
    relationships = relationship("CharacterRelationship", back_populates="character", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="character", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="character", cascade="all, delete-orphan")


class InventoryItem(db.Model):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    item: Mapped[str]
    description: Mapped[str]
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    magical: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    character = relationship("Character", back_populates="inventory_items")


class Ability(db.Model):
    __tablename__ = "abilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    name: Mapped[str]
    description: Mapped[str]
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    uses_per_session: Mapped[int]
    used: Mapped[bool] = mapped_column(default=False)

    character = relationship("Character", back_populates="abilities")


class Spell(db.Model):
    __tablename__ = "spells"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    name: Mapped[str]
    type: Mapped[str]
    description: Mapped[str]
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    uses: Mapped[int]

    character = relationship("Character", back_populates="spells")

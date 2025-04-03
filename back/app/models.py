from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.inspection import inspect
from app import db

class Serializer:
    def to_dict(self, include_relationships=False):
        result = {}
        for column_attribute in inspect(self).mapper.column_attrs:
            column_name = column_attribute.key
            column_value = getattr(self, column_name)
            result[column_name] = column_value
        if include_relationships:
            for relationship_property in inspect(self.__class__).relationships:
                relation_name = relationship_property.key
                relation_value = getattr(self, relation_name)

                if isinstance(relation_value, list):
                    result[relation_name] = [
                        item.to_dict() for item in relation_value
                    ]
                elif relation_value is not None:
                    result[relation_name] = relation_value.to_dict()
        return result
    

class Character(db.Model, Serializer):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    race: Mapped[str] = mapped_column(String(32))
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)

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


class Stat(db.Model, Serializer):
    __tablename__ = "stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    name: Mapped[str] = mapped_column(String(16))
    value: Mapped[int] = mapped_column(Integer)

    character = relationship("Character", back_populates="stats")


class InventoryItem(db.Model, Serializer):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    item: Mapped[str]
    description: Mapped[str]
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    magical: Mapped[bool] = mapped_column(default=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    character = relationship("Character", back_populates="inventory_items")


class Ability(db.Model, Serializer):
    __tablename__ = "abilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    name: Mapped[str]
    description: Mapped[str]
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    uses_per_session: Mapped[int]
    used: Mapped[bool] = mapped_column(default=False)

    character = relationship("Character", back_populates="abilities")


class Spell(db.Model, Serializer):
    __tablename__ = "spells"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    name: Mapped[str]
    type: Mapped[str]
    description: Mapped[str]
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    uses: Mapped[int]

    character = relationship("Character", back_populates="spells")

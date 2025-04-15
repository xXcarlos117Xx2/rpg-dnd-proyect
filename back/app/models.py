from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Text, DateTime, Boolean, func
from sqlalchemy.inspection import inspect
from datetime import datetime, timezone
from app import db

class Serializer:
    def to_dict(self, include_relationships=False):
        result = {}
        sensitive_fields = {'password', 'password_hash'}

        for column_attribute in inspect(self).mapper.column_attrs:
            column_name = column_attribute.key
            if column_name in sensitive_fields:
                continue
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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
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

    user = relationship("User", back_populates="characters")
    journal_entries = relationship("JournalEntry", back_populates="character", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="character", cascade="all, delete-orphan")
    conditions = relationship("Condition", back_populates="character", cascade="all, delete-orphan")


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

class JournalEntry(db.Model, Serializer):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    character = relationship("Character", back_populates="journal_entries")

class Decision(db.Model, Serializer):
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    description: Mapped[str] = mapped_column(Text)
    impact: Mapped[str] = mapped_column(Text, nullable=True)

    character = relationship("Character", back_populates="decisions")

class Condition(db.Model, Serializer):
    __tablename__ = "conditions"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    name: Mapped[str]
    description: Mapped[str]
    temporary: Mapped[bool] = mapped_column(default=True)

    character = relationship("Character", back_populates="conditions")

class CharacterRelationship(db.Model, Serializer):
    __tablename__ = "character_relationships"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    target_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    relation_type: Mapped[str] = mapped_column(String(64))

    source = relationship("Character", foreign_keys=[source_id], backref="relationships_out")
    target = relationship("Character", foreign_keys=[target_id], backref="relationships_in")

class User(db.Model, Serializer):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    characters = relationship("Character", back_populates="user", cascade="all, delete-orphan")

class PersistentToken(db.Model):
    __tablename__ = "persistent_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    permanent: Mapped[bool] = mapped_column(Boolean, default=False)

    user = db.relationship("User", backref="persistent_tokens")

    def mark_expired_if_needed(self):
        if self.expires_at and datetime.now(timezone.utc) > self.expires_at:
            self.revoked = True

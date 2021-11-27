from __future__ import annotations
from typing import List

from decouple import config
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, backref
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import func

from custom_exceptions import ObjectIsExist
from main import session as main_session

Base = declarative_base()

class Language(Base):
    __tablename__ = "language"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


LANGUAGE_TO_LEARN = main_session.query(Language).filter(
    Language.name == config('LANGUAGE_TO_LEARN')
).first()

LANGUAGE_TO_TRANSLATION = main_session.query(Language).filter(
    Language.name == config('LANGUAGE_TO_TRANSLATION')
).first()


word_item_association_table = Table(
    "word_item_association",
    Base.metadata,
    Column("word_id", ForeignKey("word.id"), primary_key=True),
    Column("item_id", ForeignKey("item.id"), primary_key=True),
)


class Word(Base):
    __tablename__ = "word"

    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True)
    language_id = Column(Integer, ForeignKey("language.id"))

    language = relationship("Language", backref=backref("words"))

    def __repr__(self):
        return self.word

    @classmethod
    def get_word_object(
        cls,
        word: str,
        language: Language,
        session: Session
    ) -> Word:
        word_object = session.query(
            cls
        ).filter(
            cls.language == language
        ).filter(
            cls.word == word
        ).one_or_none()
        """one_or_none() rather than first() because 
        field "word" is unique and shouldn't have many results"""

        return word_object

    @classmethod
    def create_word_object(
        cls,
        word: str,
        language: Language,
        session: Session
    ) -> Word:
        if cls.get_word_object(word, language, session) is not None:
            raise ObjectIsExist

        word_object = cls(
            word=word,
            language=language
        )
        session.add(word_object)
        session.commit()

        return word_object

    # return existing word object or create new
    @classmethod
    def get_existing_word_object(
        cls,
        word: str,
        language: Language,
        session: Session
    ) -> Word:
        word_object = cls.get_word_object(word, language, session)

        if not word_object:
            word_object = cls.create_word_object(word, language, session)

        return word_object


class Item(Base):
    __tablename__ = "item"

    id = Column(Integer, primary_key=True)
    learning_word_id = Column(Integer, ForeignKey("word.id"))
    language_to_learn_id = Column(Integer, ForeignKey("language.id"))
    language_to_translation_id = Column(Integer, ForeignKey("language.id"))
    correct_answer_from = Column(Integer, default=0)
    correct_answer_to = Column(Integer, default=0)

    learning_word = relationship(
        "Word", foreign_keys=[learning_word_id],
        backref=backref("word_learning_item", uselist=False)
    )
    language_to_learn = relationship(
        "Language",
        foreign_keys=[language_to_learn_id],
        backref=backref("language_to_learn_items")
    )
    language_to_translation = relationship(
        "Language",
        foreign_keys=[language_to_translation_id],
        backref=backref("language_to_translation_items")
    )
    translate_words = relationship(
        "Word", secondary=word_item_association_table, backref="word_translations_items"
    )

    def __repr__(self):
        return "{word} - {translate}".format(
            word=self.learning_word.word,
            translate=", ".join([word.word for word in self.translate_words])
        )

    def check_translation(
        self,
        word: str,
        answer_from: bool,
        session: Session,
        language_to_learn: Language = LANGUAGE_TO_LEARN,
        language_to_translation: Language = LANGUAGE_TO_TRANSLATION
    ) -> bool:
        respond = False

        # if translate from learning language
        if answer_from:
            word_object = Word.get_word_object(word, language_to_translation, session)
            if word_object:
                if word_object in self.translate_words:
                    self.correct_answer_from += 1
                    respond = True

            elif self.correct_answer_from > 0:
                self.correct_answer_from -= 1

        # if translate to learning language
        else:
            word_object = Word.get_word_object(word, language_to_learn, session)
            if word_object:
                if word_object is self.learning_word:
                    self.correct_answer_to += 1
                    respond = True

            elif self.correct_answer_to > 0:
                self.correct_answer_to -= 1

        session.commit()
        return respond

    @classmethod
    def get_random_item(
        cls,
        session: Session,
        language_to_learn: Language = LANGUAGE_TO_LEARN,
        language_to_translation: Language = LANGUAGE_TO_TRANSLATION,
    ) -> Item:
        return session.query(cls).filter(
            cls.language_to_learn == language_to_learn
        ).filter(
            cls.language_to_translation == language_to_translation
        ).order_by(
            func.random()
        ).first()

    @classmethod
    def create_new_item(
        cls,
        learning_word: str,
        translate_words: List[str],
        session: Session,
        language_to_learn: Language = LANGUAGE_TO_LEARN,
        language_to_translation: Language = LANGUAGE_TO_TRANSLATION
    ) -> None:
        learning_word_object = Word.create_word_object(learning_word, language_to_learn, session)

        new_item = cls(
            learning_word=learning_word_object,
            language_to_learn=language_to_learn,
            language_to_translation=language_to_translation
        )

        session.add(new_item)

        for translate_word in translate_words:
            translate_word_object = Word.get_existing_word_object(translate_word, language_to_translation, session)
            new_item.translate_words.append(translate_word_object)

        session.commit()

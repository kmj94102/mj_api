from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import List

Base = declarative_base()


class VocabularyNoteTable(Base):
    __tablename__ = 'vocabulary_note'
    noteId = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100))
    language = Column(String(100))
    timestamp = Column(DateTime)


class VocabularyNote(BaseModel):
    title: str = None
    language: str = None
    timestamp: datetime = None

    def toTable(self) -> VocabularyNoteTable:
        return VocabularyNoteTable(
            title=self.title,
            language=self.language,
            timestamp=self.timestamp
        )


class WordTable(Base):
    __tablename__ = 'word'
    wordId = Column(Integer, primary_key=True, autoincrement=True)
    noteId = Column(Integer, ForeignKey('vocabulary_note.noteId'))
    word = Column(Text)
    meaning = Column(Text)
    note1 = Column(Text)
    note2 = Column(Text)

    note = relationship("VocabularyNoteTable", foreign_keys=[noteId])


class Word(BaseModel):
    noteId: int = 0
    word: str = None
    meaning: str = None
    note1: str = None
    note2: str = None

    def toTable(self) -> WordTable:
        return WordTable(
            noteId=self.noteId,
            word=self.word,
            meaning=self.meaning,
            note1=self.note1,
            note2=self.note2
        )


class WordExampleTable(Base):
    __tablename__ = 'word_example'
    wordExampleId = Column(Integer, primary_key=True, autoincrement=True)
    wordId = Column(Integer, ForeignKey('word.wordId'))
    example = Column(Text)
    meaning = Column(Text)
    hint = Column(Text)
    isCheck = Column(Boolean)

    word = relationship("WordTable", foreign_keys=[wordId])


class WordExample(BaseModel):
    wordId: int = 0
    example: str = None
    meaning: str = None
    hint: str = None
    isCheck: bool = False

    def toTable(self) -> WordExampleTable:
        return WordExampleTable(
            wordId=self.wordId,
            example=self.example,
            meaning=self.meaning,
            hint=self.hint,
            isCheck=self.isCheck,
        )


class NoteSelectParam(BaseModel):
    year: int = None
    month: int = None
    language: str = None


class IdParam(BaseModel):
    idx: int = None


class WrongAnswerTable(Base):
    __tablename__ = 'wrong_answer'
    idx = Column(Integer, primary_key=True, autoincrement=True)
    wordId = Column(Integer, ForeignKey('word.wordId'))
    noteId = Column(Integer, ForeignKey('vocabulary_note.noteId'))
    count = Column(Integer)
    timestamp = Column(DateTime)

    word = relationship("WordTable", foreign_keys=[wordId])
    note = relationship("VocabularyNoteTable", foreign_keys=[noteId])


class WrongAnswer(BaseModel):
    idx: int = 0
    wordId: int = 0
    noteId: int = 0
    count: int = 0
    timestamp: datetime = None

    def toTable(self) -> WrongAnswerTable:
        return WrongAnswerTable(
            idx=self.idx,
            wordId=self.wordId,
            count=self.count
        )


class WrongAnswerInsertParam(BaseModel):
    wordIdx: int = 0
    noteIdx: int = 0


def create_wrong_answer(param: WrongAnswerInsertParam) -> WrongAnswerTable:
    wrongAnswer = WrongAnswerTable()
    wrongAnswer.wordId = param.wordIdx
    wrongAnswer.noteId = param.noteIdx
    wrongAnswer.count = 1
    wrongAnswer.timestamp = datetime.now()

    return wrongAnswer


class WrongAnswerSelectParam(BaseModel):
    noteIdx: str = ""
    limit: int = 100
    skip: int = 0

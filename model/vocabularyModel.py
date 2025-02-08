from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import List

Base = declarative_base()


class VocabularyNoteTable(Base):
    __tablename__ = 'vocabulary_note'
    noteId = Column(Integer, primary_key=True)
    title = Column(String)
    language = Column(String)
    timestamp = Column(DateTime)


class VocabularyNote(BaseModel):
    noteId: int = 0
    title: str = None
    language: str = None
    timestamp: datetime = None


def create_vocabulary_note_table(item: VocabularyNote) -> VocabularyNoteTable:
    result = VocabularyNoteTable()
    result.noteId = item.noteId
    result.title = item.title
    result.timestamp = item.timestamp

    return result


class WordTable(Base):
    __tablename__ = 'word'
    wordId = Column(Integer, primary_key=True)
    noteId = Column(Integer, ForeignKey('vocabulary_note.noteId'))
    word = Column(String)
    meaning = Column(String)
    note1 = Column(String)
    note2 = Column(String)

    note = relationship("vocabulary_note", foreign_keys=[noteId])


class Word(BaseModel):
    wordId: int = 0
    noteId: int = 0
    word: str = None
    meaning: str = None
    note1: str = None
    note2: str = None


def create_word_table(item: Word) -> WordTable:
    result = WordTable()
    result.noteId = item.wordId
    result.noteId = item.noteId
    result.word = item.word
    result.meaning = item.meaning
    result.note1 = item.note1
    result.note2 = item.note2

    return result


class WordExampleTable(Base):
    __tablename__ = 'word_example'
    wordExampleId = Column(Integer, primary_key=True)
    wordId = Column(Integer, ForeignKey('word.wordId'))
    example = Column(String)
    meaning = Column(String)
    hint = Column(String)
    isCheck = Column(Boolean)

    word = relationship("word", foreign_keys=[wordExampleId])


class WordExample(BaseModel):
    wordExampleId: int = 0
    wordId: int = 0
    example: str = None
    meaning: str = None
    hint: str = None
    isCheck: bool = False


def create_word_example_table(item: WordExample) -> WordExampleTable:
    result = WordExampleTable()
    result.wordExampleId = item.wordExampleId
    result.wordId = item.wordId
    result.example = item.example
    result.meaning = item.meaning
    result.hint = item.hint
    result.isCheck = item.isCheck

    return result

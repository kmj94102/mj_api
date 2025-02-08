from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError

from db import session
from model.common import raise_http_exception
from model.vocabularyModel import *
from typing import List

router = APIRouter()


@router.post("/insert/note")
async def insert_vocabulary_note(item: VocabularyNote):
    print(f"\n\n\n+++++ {item}\n\n\n")
    """
    단어장 등록
    - **title**: 타이틀
    - **language**: 언어
    - **timestamp**: 날짜
    """
    data = session.query(VocabularyNoteTable).\
        filter(VocabularyNoteTable.timestamp == item.timestamp,
               VocabularyNoteTable.language == item.language).first()

    if data is None:
        vocabulary = create_vocabulary_note_table(item)
        session.add(vocabulary)
        session.commit()
        return f"{item.title} 추가 완료"
    else:
        return "이미 등록된 노트가 있습니다."


@router.post("/insert/word")
async def insert_word(item: Word):
    print(f"\n\n\n+++++ {item}\n\n\n")
    """
    단어 등록
    - **noteId**: 노트 아이디
    - **word**: 단어
    - **meaning**: 뜻
    - **note1**: 비고1
    - **note2**: 비고2
    """
    data = session.query(WordTable).filter(WordTable.word == item.word).first()

    try:
        session.rollback()
        session.begin()

        if data is None:
            word = create_word_table(item)
            session.add(word)
            session.flush()
            session.commit()

            return word.wordId
        else:
            session.rollback()
            raise_http_exception(f'${item.word}는 이미 등록되었습니다')
    except SQLAlchemyError as e:
        session.rollback()
        raise_http_exception(f"오류가 발생하였습니다. {e}")
    finally:
        session.close()


@router.post("/insert/word/example")
async def insert_word_example(_list: List[WordExample]):
    """
    단어 예시 등록
    - **wordId**: 단어 아이디
    - **example**: 예시 문장
    - **meaning**: 예시 문장 뜻
    - **hint**: 예시 문장 힌트
    - **isCheck**: 체크 여부
    """
    try:
        for item in _list:
            data = session.query(WordExampleTable)\
                .filter(WordExampleTable.example == item.example).first()
            if data is None:
                wordExample = create_word_example_table(item)
                session.add(wordExample)
            else:
                session.rollback()
                raise_http_exception('중복으로 등록된 아이템이 있습니다.')
        session.commit()
    finally:
        session.close()

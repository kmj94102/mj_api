from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError

from db import session
from model.common import raise_http_exception
from model.vocabularyModel import *
from typing import List


router = APIRouter()


@router.post("/insert/note", summary="단어장 등록")
async def insert_vocabulary_note(item: VocabularyNote):
    """
    단어장 등록
    - **title**: 타이틀
    - **language**: 언어 (us/jp)
    - **timestamp**: 날짜
    """
    data = session.query(VocabularyNoteTable).\
        filter(VocabularyNoteTable.timestamp == item.timestamp,
               VocabularyNoteTable.language == item.language).first()

    if data is None:
        vocabulary = item.toTable()
        session.add(vocabulary)
        session.commit()
        return f"{item.title} 추가 완료"
    else:
        return "이미 등록된 노트가 있습니다."


@router.post("/insert/word", summary="단어 등록")
async def insert_word(item: Word):
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
            word = item.toTable()
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


@router.post("/insert/word/example", summary="단어 예시 등록")
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
                wordExample = item.toTable()
                session.add(wordExample)
            else:
                session.rollback()
                raise_http_exception('중복으로 등록된 아이템이 있습니다.')
        session.commit()
    finally:
        session.close()


@router.post("/select/note", summary="노트 조회")
async def select_vocabulary_note(item: NoteSelectParam):
    """
    단어장 조회
    - **year**: 년도
    - **month**: 월
    - **language**: all/us/jp
    """
    start_date = datetime(item.year, item.month, 1)
    if item.month == 12:
        end_date = datetime(item.year + 1, 1, 1)
    else:
        end_date = datetime(item.year, item.month + 1, 1)

    if item.language == 'all':
        return session.query(VocabularyNoteTable). \
            filter(VocabularyNoteTable.timestamp >= start_date). \
            filter(VocabularyNoteTable.timestamp < end_date). \
            all()
    else:
        return session.query(VocabularyNoteTable). \
            filter(VocabularyNoteTable.timestamp >= start_date). \
            filter(VocabularyNoteTable.timestamp < end_date). \
            filter(VocabularyNoteTable.language == item.language).\
            all()


@router.post("/select/word", summary="단어장 상세 조회")
async def select_vocabulary_note(item: IdParam):
    """
    단어장 상세 조회
    """

    _list = session.query(WordTable).filter(WordTable.noteId == item.idx).all()
    return [
        {
            "noteId": word.noteId,
            "wordId": word.wordId,
            "word": word.word,
            "meaning": word.meaning,
            "note1": word.note1,
            "note2": word.note2,
            "examples": session.query(WordExampleTable).filter(WordExampleTable.wordId == word.wordId).all()
        }
        for word in _list
    ]


@router.post("/insert/wrongAnswer", summary="오답 등록")
async def insert_wrong_answer(_list: List[WrongAnswerInsertParam]):
    """
    단어 예시 등록
    - **wordId**: 단어 아이디
    """
    try:
        for item in _list:
            data = session.query(WrongAnswerTable)\
                .filter(WrongAnswerTable.wordId == item.wordIdx).first()
            if data is None:
                wrongAnswer = create_wrong_answer(item)
                session.add(wrongAnswer)
            else:
                data.count += 1
                data.timestamp = datetime.now()

        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise_http_exception(f"오류가 발생하였습니다. {e}")
    finally:
        session.close()


@router.post("/select/wrongAnswer", summary="오답 조회")
async def select_wrong_answer(param: WrongAnswerSelectParam):
    session.commit()

    _list = session.query(WrongAnswerTable).filter(WrongAnswerTable.noteId.like(f"%{param.noteIdx}%")) \
        .order_by(WrongAnswerTable.timestamp).offset(param.skip).limit(param.limit).all()

    count = session.query(WrongAnswerTable).filter(WrongAnswerTable.noteId.like(f"%{param.noteIdx}%")).count()

    return {
        "list": _list,
        "count": count
    }

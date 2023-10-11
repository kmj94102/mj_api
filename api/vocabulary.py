from fastapi import APIRouter, HTTPException
from db import session
from model import VocabularyTable, Vocabulary, create_vocabulary, \
    WordGroupTable, WordGroup, create_word_group, DayParam
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
from sqlalchemy import update, delete, text

router = APIRouter()


@router.post("/insert")
async def insert_vocabulary(item: Vocabulary):
    print(f"\n\n\n+++++ {item}\n\n\n")
    """
    단어 등록
    - **day**: 날짜
    - **group**: 그룹
    - **word**: 단어
    - **meaning**: 뜻
    - **hint**: 힌트
    - **additional**: 추가
    """
    data = session.query(VocabularyTable).filter(VocabularyTable.word == item.word).first()

    if data is None:
        vocabulary = create_vocabulary(item)
        session.add(vocabulary)
        session.commit()
        return f"{item.word} 추가 완료"
    else:
        return f"{item.word}는 중복된 단어입니다."


@router.post("/select")
async def select_vocabulary(item: DayParam):
    session.commit()
    wordGroupList = session.query(WordGroupTable).filter(WordGroupTable.day == item.day).all()

    result_data = {"result": []}

    for word in wordGroupList:
        wordInfo = {
            "wordGroup": {
                "modify": word.modify,
                "day": word.day,
                "name": word.name,
                "meaning": word.meaning,
                "id": word.id
            },
            "list": []
        }

        vocabularyList = session.query(VocabularyTable).filter(VocabularyTable.group == word.name,
                                                                  VocabularyTable.day == word.day).all()
        for vocabulary in vocabularyList:
            vocabularyInfo = {
                "meaning": vocabulary.meaning,
                "day": vocabulary.day,
                "group": vocabulary.group,
                "hint": vocabulary.hint,
                "id": vocabulary.id,
                "word": vocabulary.word,
                "additional": vocabulary.additional
            }

            wordInfo["list"].append(vocabularyInfo)

        result_data["result"].append(wordInfo)

    return result_data


@router.post("/group/insert")
async def insert_word_group(item: WordGroup):
    """
    단어 등록
    - **day**: 날짜
    - **name**: 이름
    - **meaning**: 뜻
    - **modify**: 변형
    """

    data = session.query(WordGroupTable).filter(WordGroupTable.name == item.name).first()

    if data is None:
        vocabulary = create_word_group(item)
        session.add(vocabulary)
        session.commit()
        return f"{item.name} 추가 완료"
    else:
        return f"{item.name}는 중복된 그룹입니다."

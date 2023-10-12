from fastapi import APIRouter, HTTPException
from db import session
from model import VocabularyTable, Vocabulary, create_vocabulary, \
    WordGroupTable, WordGroup, create_word_group, DayParam, \
    ExaminationScoringItems, ExaminationScoring
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
from sqlalchemy import update, delete, text
from sqlalchemy.sql import func

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


@router.post("/select/examination")
async def select_examination(item: DayParam):
    random_order = func.random()
    return session.query(VocabularyTable.id, VocabularyTable.word).filter(VocabularyTable.day == item.day) \
        .order_by(random_order).all()


@router.post("/select/examination/scoring")
async def select_examination_scoring(items: List[ExaminationScoring]):
    correctCount = 0
    wrongItems = []

    vocabulary_ids = [item.id for item in items]
    vocabularies = session.query(VocabularyTable).filter(VocabularyTable.id.in_(vocabulary_ids)).all()

    for item in items:
        vocabulary = next((v for v in vocabularies if v.id == item.id), None)
        if vocabulary:
            myMeaning = item.meaning.replace(" ", "")
            vocabularyMeaning = vocabulary.meaning.replace(" ", "")

            if myMeaning != "" and myMeaning in vocabularyMeaning:
                correctCount += 1
            else:
                wrongItems.append(vocabulary)

    return {
        "totalSize": len(items),
        "correctCount": correctCount,
        "wrongItems": wrongItems
    }


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

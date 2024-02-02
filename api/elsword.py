from fastapi import APIRouter
from db import session
from model.model import Elsword, ElswordItem, create_elsword, \
    Quest, QuestItem, create_quest, QuestUpdateItem, \
    QuestProgress, create_init_quest_progress, QuestProgressUpdateItem

from sqlalchemy import delete, text
from sqlalchemy.orm import load_only

router = APIRouter()


@router.post("/insert")
async def insert_elsword(item: ElswordItem):
    """
    엘소드 캐릭터 정보 등록
    - **characterGroup**: 케릭터 그룹 ex) 엘소드
    - **line**: 전직 라인 ex) 1
    - **classType**: 전직 등급, [first, second, third, master] 중 택 1
    - **name**: 전직 이름
    - **engName: 전직 영어 이름
    - **attackType**: 공격 타입, [magic, physics] 중 택 1
    - **story**: 전직 스토리
    - **bigImage**: 전체 이미지
    - **questImage**: 퀘스트 이미지 (선택)
    - **progressImage**: 퀘스트 진행 이미지 (선택)
    - **circleImage**: 원형 이미지
    """
    elsword = create_elsword(item)

    session.add(elsword)
    session.commit()
    return f"{item.name} 추가 완료"


@router.post("/insert/quest")
async def insert_elsword_quest(item: QuestItem):
    """
    엘소드 퀘스트 정보 등록
    - name: 퀘스트 이름
    - max: 퀘스트 개수
    - complete: 퀘스트를 완료한 캐릭터 이름들
    - ongoing: 퀘스트를 진행하고 있는 캐릭터 이름들
    """
    quest = create_quest(item)

    history = session.query(Quest).filter(Quest.name == item.name).first()
    if history is None:
        session.add(quest)
        session.commit()
        result = f"{item.name}를 등록하였습니다."
    else:
        result = f"{item.name}은 이미 등록된 퀘스트입니다."
    return result


@router.get("/select/quest")
async def read_elsword_quest():
    """
    엘소드 퀘스트 리스트 조회
    """
    session.commit()
    quest = session.query(Quest).all()

    return [
        {
            "progress": calculate_task_progress(item.complete),
            "id": item.id,
            "name": item.name
        }
        for item in quest
    ]


def calculate_task_progress(complete: str):
    list = complete.split(",")
    length = len(list) if list[0] != "" or list[-1] != "" else 0
    print(length)
    return (length / 56) * 100


@router.delete("/delete/quest")
async def delete_elsword_quest(id: int):
    """
    엘소드 퀘스트 삭제
    - **id**: 삭제하려고 하는 퀘스트 id
    """
    session.execute(delete(Quest).where(Quest.id == id))
    session.commit()

    return "삭제 완료"


@router.get("/select/quest/detail")
async def select_elsword_quest_detail():
    """
    엘소드 퀘스트 상세 정보 조회
    """
    session.commit()
    quest = session.query(Quest).all()
    allowed_fields = ["characterGroup", "name", "questImage"]
    elsword = session.query(Elsword).filter(Elsword.classType == "master").options(load_only(*allowed_fields)).all()

    return [
        {
            "id": item.id,
            "name": item.name,
            "max": item.max,
            "character": [
                {
                    "name": char.name,
                    "image": char.questImage,
                    "group": char.characterGroup,
                    "isComplete": char.name in item.complete,
                    "isOngoing": char.name in item.ongoing,
                    "progress": get_character_progress(item.id, char.name) if char.name in item.ongoing else 0
                }
                for char in elsword
            ]
        }
        for item in quest
    ]


def get_character_progress(quest_id: int, name: str):
    try:
        result = session.query(QuestProgress).filter(QuestProgress.quest_id == quest_id,
                                                     QuestProgress.name == name).first().progress
    except:
        result = 0

    return result


@router.post("/update/quest")
async def update_elsword_quest(item: QuestUpdateItem):
    """
    퀘스트 상태 업데이트
    - id: 퀘스트 id
    - name: 캐릭터 이름
    - type: 변경할 퀘스트 상태 [complete, ongoing, remove] 중 택 1
    """
    quest = session.query(Quest).filter(Quest.id == item.id).first()
    if item.type == "complete":
        quest.complete = add_name_to_text(quest.complete, item.name)
        quest.ongoing = remove_name_to_text(quest.ongoing, item.name)
        await delete_quest_progress(item.id, item.name)
    elif item.type == "ongoing":
        quest.ongoing = add_name_to_text(quest.ongoing, item.name)
        quest.complete = remove_name_to_text(quest.complete, item.name)
        await create_quest_progress(item.id, item.name, item.progress)
    elif item.type == "remove":
        quest.complete = remove_name_to_text(quest.complete, item.name)
        quest.ongoing = remove_name_to_text(quest.ongoing, item.name)
        await delete_quest_progress(item.id, item.name)

    session.commit()
    return "업데이트 완료"


# 텍스트에 캐릭터 추가
def add_name_to_text(text, name):
    if text:
        result = f"{text},{name}"
    else:
        result = name
    return result


# 텍스트에 캐릭터 삭제
def remove_name_to_text(text, name):
    result = text.replace(f"{name},", "").replace(f",{name}", "").replace(name, "")
    if result.endswith(","):
        result = result[:-1]
    return result


# 퀘스트 진행 추가
async def create_quest_progress(id, name, progress_value):
    progress = create_init_quest_progress(id, name, progress_value)
    session.add(progress)

    return f"{name} 추가 완료"


# 퀘스트 진행 삭제
async def delete_quest_progress(id, name):
    session.query(QuestProgress).filter(QuestProgress.quest_id == id, QuestProgress.name == name).delete(
        synchronize_session=False)
    session.commit()

    return f"{name} 삭제 완료"


@router.get("/select/counter")
async def read_elsword_quest_progress():
    """
    퀘스트 진행 조회
    """
    session.commit()

    sql = """
        SELECT quest_progress.id, quest_progress.name, quest_progress.quest_id, quest_progress.progress, quest.max, elsword.progressImage, elsword.characterGroup 
        FROM quest, quest_progress, elsword 
        WHERE quest_progress.quest_id = quest.id AND elsword.name = quest_progress.name and elsword.classType = 'master'
    """

    result = session.execute(text(sql)).fetchall()

    formatted_result = [
        {
            "id": row[0],
            "name": row[1],
            "quest_id": row[2],
            "progress": row[3],
            "max": row[4],
            "image": row[5],
            "characterGroup": row[6],
        }
        for row in result
    ]

    return formatted_result


@router.post("/update/counter")
async def update_elsword_quest_progress(item: QuestProgressUpdateItem):
    """
    퀘스트 상태 업데이트
    - **id**: 퀘스트 진행 id
    - **max**: 퀘스트 개수
    """
    progressItem = session.query(QuestProgress).filter(QuestProgress.id == item.id).first()
    progressItem.progress += 1
    session.commit()

    if progressItem.progress >= item.max:
        await update_elsword_quest(QuestUpdateItem(id=progressItem.quest_id, name=progressItem.name, type="complete"))
        return 0

    return progressItem.progress

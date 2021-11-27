import pytest
from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session

from models import Base, Language, Word, Item

LANGUAGE_TO_LEARN = config('LANGUAGE_TO_LEARN')
LANGUAGE_TO_TRANSLATION = config('LANGUAGE_TO_TRANSLATION')

def create_test_data(db_session: Session):
    # add test languages
    language_to_learn = Language(name=LANGUAGE_TO_LEARN)
    language_to_translation = Language(name=LANGUAGE_TO_TRANSLATION)

    db_session.add_all(
        [
            language_to_learn,
            language_to_translation
        ]
    )

    db_session.commit()

    # add test words
    learning_word = Word(word="something", language=language_to_learn)
    translate_word = Word(word="щось", language=language_to_translation)
    db_session.add_all(
        [
            learning_word,
            translate_word
        ]
    )

    db_session.commit()

    # add test items
    test_item = Item(
        learning_word=learning_word,
        language_to_learn=language_to_learn,
        language_to_translation=language_to_translation
    )

    db_session.add(test_item)

    test_item.translate_words.append(translate_word)
    db_session.commit()


@pytest.fixture(scope="session")
def db_session():
    engine = create_engine(config('TEST_DB_LINK'))
    # create all tables from models
    Base.metadata.create_all(engine)
    # create session
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    try:
        create_test_data(session)

        yield session

    finally:
        session.close()
        # remove all tables
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def language_to_learn(db_session: Session):
    return db_session.query(Language).filter(Language.name == LANGUAGE_TO_LEARN).first()


@pytest.fixture()
def language_to_translation(db_session: Session):
    return db_session.query(Language).filter(Language.name == LANGUAGE_TO_TRANSLATION).first()


def test_get_word_object(
    db_session: Session,
    language_to_learn: Language
):
    assert Word.get_word_object("something", language_to_learn, db_session) is not None


def test_fail_get_word_object(
    db_session: Session,
    language_to_learn: Language
):
    assert Word.get_word_object("xxx", language_to_learn, db_session) is None


def test_get_existing_word_object(
    db_session: Session,
    language_to_learn: Language
):
    # test when word exist
    assert Word.get_existing_word_object(
        "something",
        language_to_learn,
        db_session
    ) is not None

    # test when word not exist
    assert Word.get_existing_word_object(
        "nothing",
        language_to_learn,
        db_session
    ) is not None


def test_get_random_item(
    db_session: Session,
    language_to_learn: Language,
    language_to_translation: Language
):
    assert Item.get_random_item(
        db_session,
        language_to_learn,
        language_to_translation
    ) is not None


def test_create_item(
    db_session: Session,
    language_to_learn: Language,
    language_to_translation: Language
):
    Item.create_new_item(
        learning_word="anything",
        translate_words=["що завгодно", "будь-що"],
        session=db_session,
        language_to_learn=language_to_learn,
        language_to_translation=language_to_translation
    )


"""function for get number of correct answers
depending on the argument answer_from"""
def get_number_of_correct_answers(item: Item, answer_from: bool):
    if answer_from:
        return item.correct_answer_from
    else:
        return item.correct_answer_to


"""function for test all scenarios check_translation
depending on the argument answer_from"""
def scenarios_checking_translation(
    item: Item,
    correct_answer: str,
    wrong_answer: str,
    answer_from: bool,
    db_session: Session,
    language_to_learn: Language,
    language_to_translation: Language
):
    old_correct_answer = get_number_of_correct_answers(item, answer_from)

    """test correct answer
    must be 0"""
    item.check_translation(
        correct_answer,
        answer_from,
        db_session,
        language_to_learn,
        language_to_translation
    )
    assert get_number_of_correct_answers(item, answer_from) - old_correct_answer == 1, \
        "Correct answer did not count, or wrong counted"

    """test wrong answer
    must be same as old_correct_answer"""
    item.check_translation(
        wrong_answer,
        answer_from,
        db_session,
        language_to_learn,
        language_to_translation
    )
    assert get_number_of_correct_answers(item, answer_from) == old_correct_answer, \
        "Wrong answer did not count, or wrong counted"

    """test wrong answer when correct answers = 0
    must be 0"""
    if answer_from:
        item.correct_answer_from = 0
    else:
        item.correct_answer_to = 0
    item.check_translation(
        wrong_answer,
        answer_from,
        db_session,
        language_to_learn,
        language_to_translation
    )
    assert get_number_of_correct_answers(item, answer_from) == 0, \
        "Number must not be less than 0"


def test_checking_translation(
    db_session: Session,
    language_to_learn: Language,
    language_to_translation: Language
):
    item = Word.get_word_object("something", language_to_learn, db_session).word_learning_item

    scenarios_checking_translation(
        item,
        "щось",
        "wrong",
        True,
        db_session,
        language_to_learn,
        language_to_translation
    )

    scenarios_checking_translation(
        item,
        "something",
        "wrong",
        False,
        db_session,
        language_to_learn,
        language_to_translation
    )

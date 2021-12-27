import pytest
from decouple import config

from db_helpers import add_word, check_translation, get_random_word, update_number_of_correct_answers



def create_test_data():
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
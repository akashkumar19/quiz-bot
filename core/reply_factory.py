
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if current_question_id is None:
        return True, None  # No question to record if the ID is None (initial state)

    try:
        correct_answer = PYTHON_QUESTION_LIST[current_question_id]['answer']
        user_answers = session.get('user_answers', [])

        while len(user_answers) <= current_question_id:
            user_answers.append(None)

        user_answers[current_question_id] = answer
        session['user_answers'] = user_answers
        session.save()

        if answer != correct_answer:
            return False, "Incorrect answer. Please try again."
        return True, None
    except IndexError:
        return False, "Invalid question ID."

def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    next_question_id = current_question_id + 1 if current_question_id is not None else 0

    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]['question_text']
        return next_question, next_question_id

    return None, None
    

def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''

    user_answers = session.get('user_answers', [])
    score = 0
    total_questions = len(PYTHON_QUESTION_LIST)

    for i, user_answer in enumerate(user_answers):
        if i < total_questions and user_answer == PYTHON_QUESTION_LIST[i]['answer']:
            score += 1

    result_message = f"You have completed the quiz. Your score is {score} out of {total_questions}."
    return result_message

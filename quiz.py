from typing import List


class Quiz:
    type: str = 'quiz'

    def __init__(self, quiz_id, question, options, correct_option_id, owner_id) -> None:
        self.quiz_id: str = quiz_id # Quiz ID
        self.question: str = question # question text
        self.options: List[str] = [*options] # Unpacked options list
        self.correct_option_id: int = correct_option_id # correct answer index
        self.owner_id: int = owner_id # quiz owner
        self.winners: List[int] = [] # list of winners
        self.chat_id: int = 0 # Chat in which quiz published
        self.message_id: int = 0 # quiz message for close

class Question:
    def __init__(self,question_chegg_id,url, day_id,question_text,answer,server_id,question_html,page_html):
        self.url = url
        self.day_id=day_id
        self.question_text=question_text
        self.server_id=server_id
        self.answer=answer
        self.question_html=question_html
        self.page_html=page_html
        self.is_processed = 0
        self.question_chegg_id=question_chegg_id


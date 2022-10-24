import sys
import pymysql
from repository.Model.Question import Question
from pymysql.converters import escape_string

#
#
# server_id=sys.argv[2]
server_id = 2000


class QuestionRepository:
    def add_record(self, mysql_db_manager, question):
        query = "INSERT INTO question (question_chegg_id,url, day_id,question_text,server_id,question_html,page_html) " \
                "VALUES (%s, %s,%s,%s,%s,%s,%s) "

        mysql_db_manager.execute_many_query(query, question)

    def add_question_general(self, mysql_db_manager, new_question, question):
        query = "INSERT INTO question (question_chegg_id, url, day_id,question_text,server_id) " \
                "VALUES (%s, %s,%s,%s,%s) ON DUPLICATE KEY UPDATE" \
                " day_id='" + str(question.day_id) + "' "
        " , question_text='" + str(question.question_text) + "' "
        " , is_processed='" + str(1) + "' "
        mysql_db_manager.execute_many_query(query, new_question)

    def add_question_crawled(self, mysql_db_manager, new_question, question):
        query = "INSERT INTO question (question_chegg_id, url,answer_html,server_id,question_html,page_html,state) " \
                "VALUES (%s, %s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE" \
                " day_id='" + str(question.day_id) + "' " \
                                                     ",is_processed='" + str(1) + "' "
        " , question_text='" + str(question.question_text) + "' "
        mysql_db_manager.execute_many_query(query, new_question)

    def get_first_not_crawled(self, mysql_db_manager):
        query = "SELECT * FROM question where is_processed=0 " \
                "and server_id='" + str(server_id) + "' "

        result = mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return None
        return Question(result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])

    def get_first_not_crawled_k_questions(self, mysql_db_manager, k):
        query = "SELECT * FROM question where is_processed=0 " \
                "and server_id='" + str(server_id) + "' " + " limit " + str(k)

        result = mysql_db_manager.excute_query_fetchall(query)
        if not result:
            return None
        questions = []
        for row in result:
            questions.append(Question(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return questions

    def get_first_not_answer_checked_k_questions(self, mysql_db_manager, k):
        query = "SELECT id,question_chegg_id,url,day_id,question_text,answer_html,server_id,question_html,page_html FROM question where answer_checking_processed=0 " \
                "and server_id='" + str(server_id) + "' " + " limit " + str(k)

        result = mysql_db_manager.excute_query_fetchall(query)
        if not result:
            return None
        questions = []
        for row in result:
            questions.append(Question(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return questions

    def get_first_not_answer_retrived_k_questions(self, mysql_db_manager, k):
        query = "SELECT id,question_chegg_id,url,day_id,question_text,answer_html,server_id,question_html,page_html FROM question where answer_checking_processed=1 and has_answer=1 and answer_retrieved=0 " \
                "and server_id='" + str(server_id) + "' " + " limit " + str(k)

        result = mysql_db_manager.excute_query_fetchall(query)
        if not result:
            return None
        questions = []
        for row in result:
            questions.append(Question(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return questions

    def get_question_by_id(self, mysql_db_manager, question_chegg_id):

        query = "SELECT * FROM question where question_chegg_id ='" + str(question_chegg_id) + "' "
        result = mysql_db_manager.excute_query_fetchone(query)
        if result == None:
            return None
        else:
            return Question(result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8])

    def set_answer_checked_with_no_expert_answer(self, mysql_db_manager, new_question):
        query = "UPDATE question SET answer_checking_processed = '1',has_answer='0' WHERE url='" + escape_string(
            str(new_question.url)) + "' " \
                                     "and server_id='" + str(server_id) + "' "
        mysql_db_manager.excute_query(query)

    def set_answer_checked_with_expert_answer(self, mysql_db_manager, new_question):
        query = "UPDATE question SET answer_checking_processed = '1',has_answer='1' WHERE url='" + escape_string(
            str(new_question.url)) + "' " \
                                     "and server_id='" + str(server_id) + "' "
        mysql_db_manager.excute_query(query)

    def set_processed(self, mysql_db_manager, new_question):
        query = "UPDATE question SET is_processed = '1' WHERE url='" + escape_string(str(new_question.url)) + "' " \
                                                                                                              "and server_id='" + str(
            server_id) + "' "
        mysql_db_manager.excute_query(query)

    def set_broken(self, mysql_db_manager, question, reason):
        query = "UPDATE question SET is_processed = '2' ,state = '" + str(reason) + "' WHERE url='" + escape_string(
            str(question.url)) + "' " \
                                 " and server_id='" + str(server_id) + "' "
        mysql_db_manager.excute_query(query)

    def set_answer(self, mysql_db_manager, question, answer, reason):
        query = "UPDATE question SET answer_html = '" + escape_string(str(answer)) + "' " \
                                                                                     ",answer_retrieved='" + str(
            1) + "' " \
                 ",state='" + str(reason) + "' " \
                                            " WHERE question_chegg_id ='" + str(question.question_chegg_id) + "' "
        mysql_db_manager.excute_query(query)

    def set_page_html(self, mysql_db_manager, question, html):
        query = "UPDATE question SET page_html = '" + escape_string(str(html)) + "' WHERE url='" + escape_string(
            str(question.url)) + "' " \
                                 " and server_id='" + str(server_id) + "' "
        mysql_db_manager.excute_query(query)

    def set_question_html(self, mysql_db_manager, question, question_html):
        query = "UPDATE question SET question_html = '" + escape_string(
            str(question_html)) + "' WHERE url='" + escape_string(
            str(question.url)) + "' " \
                                 " and server_id='" + str(server_id) + "' "
        mysql_db_manager.excute_query(query)

    def set_question_info(self, mysql_db_manager, question, answer, question_html, page_html, reason):
        query = "UPDATE question SET question_html = '" + escape_string(str(question_html)) + "' " \
                                                                                              ",answer_html='" + escape_string(
            str(answer)) + "' " \
                           ",page_html='" + escape_string(str(page_html)) + "' " \
                                                                            ",answer_retrieved='" + str(1) + "' " \
                                                                                                             ",state='" + str(
            reason) + "' " \
                      " WHERE question_chegg_id ='" + str(question.question_chegg_id) + "' " \
                                                                                        " and server_id='" + str(
            server_id) + "' "
        mysql_db_manager.excute_query(query)

    def is_exist_question(self, mysql_db_manager, question_chegg_id):
        query = "SELECT * FROM question where question_chegg_id ='" + str(question_chegg_id) + "' "
        result = mysql_db_manager.excute_query_fetchone(query)
        if result == None:
            return False
        else:
            return True

    def set_reason(self, mysql_db_manager, question, reason):
        query = "UPDATE question SET state = '" + str(reason) + "' WHERE question_chegg_id ='" + str(
            question.question_chegg_id) + "' "

        mysql_db_manager.excute_query(query)

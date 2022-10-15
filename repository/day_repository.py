import sys
import pymysql
from repository.Model.Day import Day
from pymysql.converters import escape_string
from repository.sub_category_repository import SubCategoryRepository
sub_category_repository = SubCategoryRepository()
#
#server_id=sys.argv[1]
#server_id=1000

class DayRepository:


    def add_record(self, mysql_db_manager, day):
        query = "INSERT INTO day (sub_category_id,day_number,month,year,url) " \
                "VALUES (%s, %s, %s, %s, %s)"




        mysql_db_manager.execute_many_query(query, day)


    def get_first_not_crawled(self,mysql_db_manager):
        query = "SELECT * FROM day where is_crawled=0 "\
                "and server_id='"+str(server_id)+"' "

        result=mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return None
        print(result)
        return Day(result[1], result[2], result[3], result[4],result[5])

    def get_first_not_crawled_k_days(self, mysql_db_manager,k):
        query = "SELECT * FROM day where is_crawled=0 "\
                "and server_id='"+str(server_id)+"' "+" limit "+str(k)

        result = mysql_db_manager.excute_query_fetchall(query)
        if not result:
            return None
        days=[]
        for row in result:
            days.append (Day(row[1], row[2],row[3],row[4],row[5]))
        return days

    def set_crawled(self,mysql_db_manager,day):
        query = "UPDATE day SET is_crawled = '1' WHERE url='"+escape_string(str(day.url))+"' "\
                " and server_id='"+str(server_id)+"' "
        mysql_db_manager.excute_query(query)

    def get_id(self,mysql_db_manager,day):
        query = "SELECT id FROM day WHERE url='"+\
                escape_string(str(day.url))+"' "\
                " and server_id='"+str(server_id)+"' "

        result = mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return None
        print(result)
        return result[0]

    def is_empty(self, mysql_db_manager):
        query = "select * from day"\
                " where server_id='"+str(server_id)+"' "
        result = mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return True
        else:
            return False

    def get_final_month(self,mysql_db_manager):
        query = "SELECT month , year FROM day ORDER BY Id DESC"\
                " where server_id='"+str(server_id)+"' "
        result = mysql_db_manager.excute_query_fetchone(query)
        return result[0], result[1]

    def is_new_category(self,mysql_db_manager,sub_category):
        id=sub_category_repository.get_id(mysql_db_manager, sub_category)
        query = "SELECT id FROM day WHERE sub_category_id='" + str(id) + "' "\
                " and server_id'"+str(server_id)+"' "
        result = mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return True
        print(result)
        return None

    def is_exist_day(self,mysql_db_manager,day_url):
        query = "SELECT * FROM day where url ='" + str(day_url) + "' "
        result = mysql_db_manager.excute_query_fetchone(query)
        if result == None:
            return False
        else:
            return True















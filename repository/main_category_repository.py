from repository.Model.MainCategory import MainCategory


class MainCategoryRepository:
    def add_record(self, mysql_db_manager, main_category):
        query = "INSERT INTO main_category (name, url) " \
                "VALUES (%s, %s) "

        mysql_db_manager.execute_many_query(query, main_category)
    def get_id(self,mysql_db_manager,main_category):
        query = "SELECT id FROM main_category where name='"+main_category.name+"' "
        result = mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return None
        print(result)
        return result[0]

    def get_first_not_crawled(self,mysql_db_manager):
        query = "SELECT * FROM main_category where is_crawled=0"
        result=mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return None

        return MainCategory(result[1], result[2])

    def is_empty(self,mysql_db_manager):
        query = "select * from main_category"
        result = mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return True
        else:
            return False

    def set_crawled(self,mysql_db_manager,main_category):
        query = "UPDATE main_category SET is_crawled = '1' WHERE url='"+str(main_category.url)+"' "
        mysql_db_manager.excute_query(query)

    def get_count(self,mysql_db_manager):
        query = "SELECT COUNT(*) FROM main_category"
        result = mysql_db_manager.excute_query_fetchone(query)
        return result[0]

    def is_exist(self,mysql_db_manager,main_category):
        query = "SELECT * FROM main_category where name ='"+str(main_category)+"' "
        result = mysql_db_manager.excute_query_fetchone(query)
        if result==None:
            return False
        else:
            return True

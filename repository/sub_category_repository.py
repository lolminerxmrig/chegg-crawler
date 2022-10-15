from repository.Model.SubCategory import SubCategory


class SubCategoryRepository:
    def add_record(self, mysql_db_manager, new_sub_category):
        query = "INSERT INTO sub_category (main_category_id, name,url) " \
                "VALUES (%s, %s, %s) "

        mysql_db_manager.execute_many_query(query, new_sub_category)

    def get_id(self, mysql_db_manager,sub_category):
        query = "SELECT id FROM sub_category where name='"+sub_category.name+"' "
        result = mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return None
        print(result)
        return result[0]

    def is_empty(self,mysql_db_manager):
        query = "select * from sub_category"
        result = mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return True
        else:
            return False

    def get_first_not_crawled(self,mysql_db_manager):
        query = "SELECT * FROM sub_category where is_crawled=0"
        result=mysql_db_manager.excute_query_fetchone(query)
        if not result:
            return None
        return SubCategory(result[1], result[2],result[3])

    def set_crawled(self,mysql_db_manager,sub_category):
        query = "UPDATE sub_category SET is_crawled = '1' WHERE url='"+str(sub_category.url)+"' "
        mysql_db_manager.excute_query(query)

    def get_count(self,mysql_db_manager):
        query = "SELECT COUNT(*) FROM sub_category"
        result = mysql_db_manager.excute_query_fetchone(query)
        return result[0]

    def is_exist(self,mysql_db_manager,sub_category):
        query = "SELECT * FROM sub_category where name ='"+str(sub_category)+"' "
        result = mysql_db_manager.excute_query_fetchone(query)
        if result==None:
            return False
        else:
            return True

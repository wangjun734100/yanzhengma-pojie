import pymysql
mysql = '172.18.228.126'
passwd = "2nOI8ca76%$#1Gm4EH"
SQL = "select * from user_invite where user_account_uuid = "
SQL1 = "select * from user_info where mobile="
SQL2 = "select * from user_info where user_account_uuid="

class Recursive:
    def __init__(self,mobile):
        self.mobile = mobile
        self.conn = pymysql.connect(host=mysql, port=3306, user='root', password=passwd, db='gcyh_user', charset='utf8')
        self.cursor = self.conn.cursor()
        self.user_list =[]

    def get_user_first(self):
        sql = SQL1+self.mobile
        self.cursor.execute(sql)
        result = self.cursor.fetchone()[3]
        return  result

    def get_user_uuid(self, user_account_uuid):      # 定义函数来计算数字n的阶乘
        sql = SQL+"'%s'" % user_account_uuid
        print(sql)
        self.cursor.execute(sql)
        result = self.cursor.fetchone() # 执行sql语句，返回sql查询成功的记录数目
        if result[3]=='0':
            return 0
        else:
            self.user_list.append(result[3])
        return self.get_user_uuid(result[3])

    def get_user_info(self, userUUidList):
        for info in userUUidList:
            print(SQL2 + info)
            self.cursor.execute(SQL2+"\""+info+"\"")
            result = self.cursor.fetchone()
            print(result)

a = Recursive('19931992025')
uuid = (a.get_user_first())
a.get_user_uuid(uuid)
print(a.user_list)
a.get_user_info(a.user_list)

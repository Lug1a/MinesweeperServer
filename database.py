import pyodbc

import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from LoginUI import Ui_Dialog as Login_Dialog

# 注：初始化数据库时需要写入一些初始数据
# 1.默认皮肤
# 2.默认关卡
# 3.默认道具加速药水
# 4.超级管理员账户


class Database():
    def __init__(self):
        try:
            self.success = 1
            self.getdata()
            # 建立连接
            # self.server = 'DESKTOP-0NL2E4M\\SQLEXPRESS'
            # self.server = 'LAPTOP-TIOL9T83'

            self.database = 'minesweeper'
            # self.username = 'sa'
            # self.password = '0000'
            # self.password = 'lc1111'
            self.cnxn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.server + ';DATABASE=' + self.database + ';UID=' +
                self.username + ';PWD=' + self.password)
            self.cursor = self.cnxn.cursor()
        except:
            self.success = 0
            print("服务器登录失败！！")

    def getdata(self):
        app = QApplication(sys.argv)
        form = QtWidgets.QDialog()
        ui = Login_Dialog()
        ui.setupUi(form)
        form.show()
        app.exec_()
        self.server, self.username, self.password = ui.getdata()

    """
    def __init__(self):
        # 建立连接
        self.server = 'DESKTOP-0NL2E4M\\SQLEXPRESS'
        # self.server = 'LAPTOP-TIOL9T83'

        self.database = 'minesweeper'
        self.username = 'sa'
        self.password = '0000'
        # self.password = 'lc1111'
        self.cnxn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.server + ';DATABASE=' + self.database + ';UID=' +
            self.username + ';PWD=' + self.password)
        self.cursor = self.cnxn.cursor()
    """

    # 建表
    def create_table(self):
        # admin
        self.cursor.execute("""
        create table admin
        (
        A_ID varchar(10) not null primary key,
        A_Username varchar(16) not null,
        A_Password varchar(16) not null,
        A_Identity varchar(50) not null
        )
        """)

        # player
        self.cursor.execute("""
        create table player
        (
        P_ID varchar(10) not null primary key,
        P_Username varchar(16) not null,
        P_Password varchar(16) not null,
        Integral integer not null,
        Gold integer not null check (Gold>=0),
        Background_Volume integer not null check (Background_Volume>=0 and Background_Volume<=100),
        Sound_Volume integer not null check (Sound_Volume>=0 and Sound_Volume<=100),
        Skin_ID varchar(50) not null
        )
        """)

        # skin_list
        self.cursor.execute("""
        create table skin_list
        (
        S_ID varchar(50) not null primary key,
        S_Name varchar(50) not null,
        S_Price integer not null check (S_Price>=0),
        S_URL varchar(100) not null
        )
        """)

        # item_list
        self.cursor.execute("""
        create table item_list
        (
        I_ID varchar(50) not null primary key,
        I_Name varchar(50) not null,
        I_Price integer not null check (I_Price>=0),
        I_Description varchar(100) not null,
        I_URL varchar(100) not null
        )
        """)

        # stage
        self.cursor.execute("""
        create table stage
        (
        D_ID varchar(50) not null primary key,
        D_Name varchar(50) not null,
        Field_Height integer not null check (Field_Height>=0),
        Field_Width integer not null check (Field_Width>=0),
        Mine_Num integer not null check (Mine_Num>=0),
        Points_Cal_Rule integer not null,
        Gold_Cal_Rule integer not null
        )
        """)

        # record
        self.cursor.execute("""
        create table record
        (
        P_ID varchar(10) not null,
        D_ID varchar(50) not null,
        Single_Or_Pair integer not null check (Single_Or_Pair=0 or Single_Or_Pair=1),
        Game_Num integer not null check (Game_Num>=0),
        Suc_Num integer not null check (Suc_Num>=0),
        Time_Sum integer not null check (Time_Sum>=0),
        Deg_Sum float not null check (Deg_Sum>=0),
        constraint pk_record primary key (P_ID,D_ID,Single_Or_Pair)
        )
        """)

        # match
        self.cursor.execute("""
        create table match
        (
        P1_ID varchar(10) not null,
        P2_ID varchar(10) not null,
        D_ID varchar(50) not null,
        Game_ID varchar(50) not null,
        StartTime datetime not null,
        EndTime datetime not null,
        P1_PointChange integer not null,
        P2_PointChange integer not null,
        constraint pk_match primary key (Game_ID)
        )
        """)

        # friend
        self.cursor.execute("""
        create table friend
        (
        P1_ID varchar(10) not null,
        P2_ID varchar(10) not null,
        FriendTime datetime,
        constraint pk_friend primary key (P1_ID,P2_ID)
        )
        """)

        # skin_property
        self.cursor.execute("""
        create table skin_property
        (
        P_ID varchar(10) not null,
        S_ID varchar(50) not null,
        constraint pk_skin_property primary key (P_ID,S_ID)
        )
        """)

        # item_property
        self.cursor.execute("""
        create table item_property
        (
        P_ID varchar(10),
        I_ID varchar(50),
        I_Quantity integer check (I_Quantity>=0),
        constraint pk_item_property primary key (P_ID,I_ID)
        )
        """)

        self.cnxn.commit()

    ################################################################################

    # 000获取match最大的game_id
    def get_match_game_id(self):
        self.cursor.execute("""
        select max(Game_ID)
        from match
        """)
        row = self.cursor.fetchone()
        return row

    # 100玩家登录，给定p_id，返回单个p_password
    def get_player_password(self, p_id):
        self.cursor.execute("""
        select P_Password
        from player
        where P_ID=?
        """, p_id)
        row = self.cursor.fetchone()
        return row

    # 102玩家注册，提供一个player的所有参数
    # 注意此处要给新玩家初始化一个默认皮肤，以及道具占坑，以及战绩占坑
    def add_player(self, p_id, p_username, p_password, integral, gold, background_volume, sound_volume, skin_id):
        self.cursor.execute("""
        begin transaction register

            insert into player (P_ID,P_Username,P_Password,Integral,Gold,Background_Volume,Sound_Volume,Skin_ID)
            values (?,?,?,?,?,?,?,?)
            insert into skin_property (P_ID,S_ID)
            values (?,?)
            insert into item_property (P_ID,I_ID,I_Quantity)
            values (?,?,?)

        if  @@ERROR!=0 rollback transaction register
        else commit transaction register
        """, p_id, p_username, p_password, integral, gold, background_volume, sound_volume, skin_id,
                            p_id, '1000', p_id, 0, 0)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 200玩家初始化主界面数据，给定p_id，返回基本信息元组
    # 注：此处最后一项是皮肤URL
    def get_my_player_info(self, p_id):
        self.cursor.execute("""
        select P_ID,P_Username,Integral,Gold,Background_Volume,Sound_Volume,S_URL
        from player
        inner join skin_list
        on player.skin_id = skin_list.S_ID
        where P_ID=?
        """, p_id)
        row = self.cursor.fetchone()
        return row

    # 202-1玩家获取关卡信息和玩家数据，返回所有关卡的所有数据
    def get_stage_info(self):
        self.cursor.execute("""
        select D_ID,D_Name,Field_Height,Field_Width,Mine_Num,Points_Cal_Rule,Gold_Cal_Rule
        from stage
        """)
        row = self.cursor.fetchall()
        return row

    # 202-2给定p_id，返回道具数据
    def get_item_info(self, p_id):
        self.cursor.execute("""
        select item_property.I_ID,I_Quantity,I_Name
        from item_property
        inner join item_list
        on item_property.I_ID = item_list.I_ID
        where P_ID=?
        """, p_id)
        row = self.cursor.fetchall()
        return row

    # 204请求排行榜数据，返回所有玩家id,username,积分，按积分从大到小排名
    def get_player_ordered_by_integral(self):
        self.cursor.execute("""
        select P_ID,P_Username,Integral
        from player
        order by Integral DESC
        """)
        row = self.cursor.fetchall()
        return row

    # 206-1请求某玩家数据，给定p_id，返回该玩家基本信息
    def get_other_player_info(self, other_pid):
        self.cursor.execute("""
        select P_ID,P_Username,Integral,Gold
        from player
        where P_ID=?
        """, other_pid)
        row = self.cursor.fetchone()
        return row

    # 206-2请求某玩家全部战绩数据，给定p_id和单/双人，返回该玩家战绩
    def get_other_player_record(self, other_pid, s_or_p):
        self.cursor.execute("""
        select D_Name,Game_Num,Suc_Num,Time_Sum,Deg_Sum
        from record
        inner join stage
        on record.D_ID = stage.D_ID
        where P_ID=? and Single_Or_Pair=?
        """, other_pid, s_or_p)
        row = self.cursor.fetchall()
        return row

    # 206-3返回自己和该玩家是否为好友
    def get_other_player_if_friend(self, my_pid, other_pid):
        self.cursor.execute("""
        select FriendTime
        from friend
        where (P1_ID=? and P2_ID=?) or (P1_ID=? and P2_ID=?)
        """, my_pid, other_pid, other_pid, my_pid)
        row = self.cursor.fetchone()
        return row

    # 300-1单人游戏结束，给定d_id，返回雷数，计算规则
    def get_a_stage(self, d_id):
        self.cursor.execute("""
        select Mine_Num,Points_Cal_Rule,Gold_Cal_Rule
        from stage
        where D_ID=?
        """, d_id)
        row = self.cursor.fetchone()
        return row

    # 300-2（单双共用）查找该玩家是否有该难度的记录，给定p_id，d_id
    def get_a_record(self, p_id, d_id, s_or_p):
        self.cursor.execute("""
        select P_ID
        from record
        where P_ID=? and D_ID=? and Single_Or_Pair=?
        """, p_id, d_id, s_or_p)
        row = self.cursor.fetchone()
        return row

    # 300-3游戏结束更新数据（新建record），给定pid，难度级别，用时，排雷数，剩余道具数
    def update_player_add_record(self, p_id, point_c, gold_c, d_id, s_or_p, suc_c, time_c, deg_c, item):
        self.cursor.execute("""
        begin transaction update_player_add_record

            update player
            set Integral=Integral+?,Gold=Gold+?
            where P_ID=?
            
            insert into record (P_ID,D_ID,Single_Or_Pair,Game_Num,Suc_Num,Time_Sum,Deg_Sum)
            values (?,?,?,?,?,?,?)
            
            update item_property
            set I_Quantity=?
            where P_ID=? and I_ID='0'
            
        if  @@ERROR!=0 rollback transaction update_player_add_record
        else commit transaction update_player_add_record
        """, point_c, gold_c, p_id, p_id, d_id, s_or_p, 1, suc_c, time_c, deg_c, item, p_id)
        self.cnxn.commit()

    # 300-4游戏结束更新数据（更新record），给定pid，难度级别，用时，排雷数，剩余道具数
    def update_player_update_record(self, p_id, point_c, gold_c,  d_id, s_or_p, suc_c, time_c, deg_c, item):
        self.cursor.execute("""
        begin transaction update_player_update_record

            update player
            set Integral=Integral+?,Gold=Gold+?
            where P_ID=?

            update record
            set Game_Num=Game_Num+1,Suc_Num=Suc_Num+?,Time_Sum=Time_Sum+?,Deg_Sum=Deg_Sum+?
            where P_ID=? and D_ID=? and Single_Or_Pair=?
            
            update item_property
            set I_Quantity=?
            where P_ID=? and I_ID='0'

        if  @@ERROR!=0 rollback transaction update_player_update_record
        else commit transaction update_player_update_record
        """, point_c, gold_c, p_id, suc_c, time_c, deg_c, p_id, d_id, s_or_p, item, p_id)
        self.cnxn.commit()

    # 300-5强行退出
    def forced_exit(self, p_id, point_c, gold_c, item):
        self.cursor.execute("""
        begin transaction forced_exit
        
            update player
            set Integral=Integral+?,Gold=Gold+?
            where P_ID=?
            
            update item_property
            set I_Quantity=?
            where P_ID=? and I_ID='0'
            
        if  @@ERROR!=0 rollback transaction forced_exit
        else commit transaction forced_exit
        """, point_c, gold_c, p_id, item, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 302-1游戏结束更新数据（新建record），给定pid，难度级别，用时，排雷数，剩余道具数
    # 没有item
    def update_player_add_record_p(self, p_id, point_c, gold_c, d_id, s_or_p, suc_c, time_c, deg_c):
        self.cursor.execute("""
        begin transaction update_player_add_record

            update player
            set Integral=Integral+?,Gold=Gold+?
            where P_ID=?

            insert into record (P_ID,D_ID,Single_Or_Pair,Game_Num,Suc_Num,Time_Sum,Deg_Sum)
            values (?,?,?,?,?,?,?)

        if  @@ERROR!=0 rollback transaction update_player_add_record
        else commit transaction update_player_add_record
        """, point_c, gold_c, p_id, p_id, d_id, s_or_p, 1, suc_c, time_c, deg_c)
        self.cnxn.commit()

    # 302-2游戏结束更新数据（更新record），给定pid，难度级别，用时，排雷数，剩余道具数
    # 没有item
    def update_player_update_record_p(self, p_id, point_c, gold_c, d_id, s_or_p, suc_c, time_c, deg_c):
        self.cursor.execute("""
        begin transaction update_player_update_record

            update player
            set Integral=Integral+?,Gold=Gold+?
            where P_ID=?

            update record
            set Game_Num=Game_Num+1,Suc_Num=Suc_Num+?,Time_Sum=Time_Sum+?,Deg_Sum=Deg_Sum+?
            where P_ID=? and D_ID=? and Single_Or_Pair=?

        if  @@ERROR!=0 rollback transaction update_player_update_record
        else commit transaction update_player_update_record
        """, point_c, gold_c, p_id, suc_c, time_c, deg_c, p_id, d_id, s_or_p)
        self.cnxn.commit()

    # 302-3强行退出没有item，或者躺赢躺输
    def forced_exit_without_item(self, p_id, point_c, gold_c):
        self.cursor.execute("""
        update player
        set Integral=Integral+?,Gold=Gold+?
        where P_ID=? 
        """, point_c, gold_c, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 302-4存match
    def save_match(self, p1_id, p2_id, d_id, game_id, starttime, endtime, p1_pointchange, p2_pointchange):
        self.cursor.execute("""
        insert into match (P1_ID,P2_ID,D_ID,Game_ID,StartTime,EndTime,P1_PointChange,P2_PointChange)
        values (?,?,?,?,?,?,?,?)
        """, p1_id, p2_id, d_id, game_id, starttime, endtime, p1_pointchange, p2_pointchange)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 304更新道具数量
    def change_item_quantity(self, p_id, quantity):
        self.cursor.execute("""
        update item_property
        set I_Quantity=?
        where P_ID=? and I_ID='0'
        """, quantity, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 400-1打开商店，？给定pid，返回所有皮肤
    def get_shop_skin(self):
        self.cursor.execute("""
        select S_ID,S_Name,S_Price,S_URL
        from skin_list
        """)
        row = self.cursor.fetchall()
        return row

    # 400-2打开商店，？给定pid，返回所有道具
    def get_shop_item(self):
        self.cursor.execute("""
        select I_ID,I_Name,I_Price,I_Description,I_URL
        from item_list
        """)
        row = self.cursor.fetchall()
        return row

    # 402-1查询皮肤拥有权，查找pid是否拥有sid
    def get_skin_property(self, p_id, s_id):
        self.cursor.execute("""
        select P_ID
        from skin_property
        where P_ID=? and S_ID=?
        """, p_id, s_id)
        row = self.cursor.fetchone()
        return row

    # 402-2获取玩家的金钱数
    def get_player_gold(self, p_id):
        self.cursor.execute("""
        select Gold
        from player
        where P_ID=?
        """, p_id)
        row = self.cursor.fetchone()
        return row

    # 402-3查询皮肤价格，查找sid的price
    def get_skin_price(self, s_id):
        self.cursor.execute("""
        select S_Price
        from skin_list
        where S_ID=?
        """, s_id)
        row = self.cursor.fetchone()
        return row

    # 402-4购买皮肤
    def buy_shop_skin(self, p_id, s_id):
        self.cursor.execute("""
        begin transaction buy_shop_skin

            update player
            set Gold = Gold-(
                select S_Price
                from skin_list
                where S_ID=?)
            where P_ID=?

            insert into skin_property
            values (?,?)

        if  @@ERROR!=0 rollback transaction buy_shop_skin
        else commit transaction buy_shop_skin
        """, s_id, p_id, p_id, s_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 403-1查询道具价格
    def get_item_price(self, i_id):
        self.cursor.execute("""
        select I_Price
        from item_list
        where I_ID=?
        """, i_id)
        row = self.cursor.fetchone()
        return row

    # 403-2购买道具
    def buy_shop_item(self, p_id, i_id, quantity):
        self.cursor.execute("""
        begin transaction buy_shop_item

            update player
            set Gold = Gold-?*(
                select I_Price
                from item_list
                where I_ID=?)
            where P_ID=?

            update item_property
            set I_Quantity = I_Quantity+?
            where P_ID=? and I_ID=?

        if  @@ERROR!=0 rollback transaction buy_shop_item
        else commit transaction buy_shop_item
        """, quantity, i_id, p_id, quantity, p_id, i_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 500-1打开背包，给定pid，返回拥有的皮肤id,name,price,url
    def get_my_skin(self, p_id):
        self.cursor.execute("""
        select skin_property.S_ID,S_Name,S_Price,S_URL
        from skin_property
        inner join skin_list
        on skin_property.S_ID = skin_list.S_ID
        where P_ID=?
        order by skin_property.S_ID ASC
        """, p_id)
        row = self.cursor.fetchall()
        return row

    # 500-2打开背包，给定pid，返回拥有的道具id,name,quantity,price,description,url
    def get_my_item(self, p_id):
        self.cursor.execute("""
        select item_property.I_ID,I_Name,I_Quantity,I_Price,I_Description,I_URL
        from item_property
        inner join item_list
        on item_property.I_ID = item_list.I_ID
        where P_ID=?
        order by item_property.I_ID ASC
        """, p_id)
        row = self.cursor.fetchall()
        return row

    # 502设置皮肤，给定pid和sid
    def change_skin(self, p_id, s_id):
        self.cursor.execute("""
        update player
        set Skin_ID=?
        where P_ID=?
        """, s_id, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 600打开好友列表，给定自己的pid，返回所有已经成为好友的用户的username,id,integral
    def get_friend_list(self, my_pid):
        self.cursor.execute("""
        (select P1_ID as my_friend,P_Username,Integral,Gold,FriendTime
        from friend
        inner join player
        on P1_ID = P_ID
        where P2_ID=? and FriendTime is NOT NULL)
        union
        (select P2_ID as my_friend,P_Username,Integral,Gold,FriendTime
        from friend
        inner join player
        on P2_ID = P_ID
        where P1_ID=? and FriendTime is NOT NULL)
        """, my_pid, my_pid)
        row = self.cursor.fetchall()
        return row

    # 602-1加好友，给定两人id，前者加后者好友
    def add_friend(self, my_pid, other_pid):
        self.cursor.execute("""
        insert into friend (P1_ID,P2_ID,FriendTime)
        values (?,?,NULL)
        """, my_pid, other_pid)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 602-2删好友
    def delete_friend(self, my_pid, other_pid):
        self.cursor.execute("""
        delete from friend
        where (P1_ID=? and P2_ID=?) or (P1_ID=? and P2_ID=?)
        """, my_pid, other_pid, other_pid, my_pid)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 602-3同意申请
    def pass_friend_apply(self, my_pid, friend_pid, friend_time):
        self.cursor.execute("""
        update friend
        set FriendTime=?
        where P1_ID=? and P2_ID=?
        """, friend_time, friend_pid, my_pid)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 604查询好友申请列表，给定id，返回该用户的好友列表list
    def get_friend_apply(self, p_id):
        self.cursor.execute("""
        select P1_ID,P_Username
        from friend
        inner join player
        on friend.P1_ID = player.P_ID
        where P2_ID=? and FriendTime is NULL
        """, p_id)
        row = self.cursor.fetchall()
        return row

    # 700打开设置界面，给定p_id，返回username,bgm音量,音效音量的元组
    def get_setting_info(self, p_id):
        self.cursor.execute("""
        select P_Username,Background_Volume,Sound_Volume
        from player
        where P_ID=?
        """, p_id)
        row = self.cursor.fetchone()
        return row

    # 702更改密码，给定用户id，新密码，返回受影响的行数
    def change_password(self, p_id, new_password):
        self.cursor.execute("""
        update player
        set P_Password=?
        where P_ID=?
        """, new_password, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 704保存音量设置，给定用户id，音乐音量，音效音量，返回受影响的行数
    def change_volume(self, p_id, background_volume, sound_volume):
        self.cursor.execute("""
        update player
        set Background_Volume=?,Sound_Volume=?
        where P_ID=?
        """, background_volume, sound_volume, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # ???管理员更改密码
    def change_password_a(self, a_id, old_password, new_password):
        self.cursor.execute("""
        update admin
        set A_Password=?
        where A_ID=? and A_Password=?
        """, new_password, a_id, old_password)
        self.cnxn.commit()

    # 800管理员登录，给定a_id，返回所有信息
    def get_admin_login(self, a_id):
        self.cursor.execute("""
        select A_Password,A_Username,A_Identity
        from admin
        where A_ID=?
        """, a_id)
        row = self.cursor.fetchone()
        return row

    # 802修改玩家数据，给玩家账号，修改后的数据，修改的数据项目
    # 1积分Integral 2金币Gold 3音量Background_Volume 4音效Sound_Volume
    def modify_player_integral(self, p_id, data):
        self.cursor.execute("""
        update player
        set Integral=?
        where P_ID=?
        """, data, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    def modify_player_gold(self, p_id, data):
        self.cursor.execute("""
        update player
        set Gold=?
        where P_ID=?
        """, data, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    def modify_player_bgm(self, p_id, data):
        self.cursor.execute("""
        update player
        set Background_Volume=?
        where P_ID=?
        """, data, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    def modify_player_sound(self, p_id, data):
        self.cursor.execute("""
        update player
        set Sound_Volume=?
        where P_ID=?
        """, data, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 804请求关卡数据，给定？账号，返回所有关卡的长 宽 雷数 名称
    # 使用202-1:get_stage_info()

    # 806请求修改关卡数据，给定？id，操作序号
    # 1增加关卡
    def modify_stage_add(self, d_id, d_name, field_height, field_width, mine_num, points_cal_rule, gold_cal_rule):
        self.cursor.execute("""
        insert into stage (D_ID,D_Name,Field_Height,Field_Width,Mine_Num,Points_Cal_Rule,Gold_Cal_Rule)
        values (?,?,?,?,?,?,?)
        """, d_id, d_name, field_height, field_width, mine_num, points_cal_rule, gold_cal_rule)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 2删除关卡
    # 查找某关卡
    def search_stage(self, d_id):
        self.cursor.execute("""
        select D_ID
        from stage
        where D_ID=?
        """, d_id)
        row = self.cursor.fetchone()
        return row

    # ############################可能要级联删除所有D_ID相关
    def modify_stage_del(self, d_id):
        self.cursor.execute("""
        begin transaction del_stage

            delete from stage
            where D_ID=?
            delete from record
            where D_ID=?
            delete from match
            where D_ID=?

        if  @@ERROR!=0 rollback transaction del_stage
        else commit transaction del_stage
        """, d_id, d_id, d_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 3修改长 宽
    def modify_stage_field(self, d_id, field_height, field_width):
        self.cursor.execute("""
        update stage
        set Field_Height=?,Field_Width=?
        where D_ID=?
        """, field_height, field_width, d_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 4修改雷数
    def modify_stage_mine(self, d_id, mine_num):
        self.cursor.execute("""
        update stage
        set Mine_Num=?
        where D_ID=?
        """, mine_num, d_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 5修改规则
    def modify_stage_rule(self, rule):
        self.cursor.execute("""
        update stage
        set Gold_Cal_Rule=?,Points_Cal_Rule=?
        """, rule, rule)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 808获取商店数据
    # 使用400-1:get_shop_skin(), 400-2:get_shop_item()

    # 810修改商店数据
    # 1增加皮肤
    def modify_skin_add(self, s_id, s_name, s_price, s_url):
        self.cursor.execute("""
        insert into skin_list (S_ID,S_Name,S_Price,S_URL)
        values (?,?,?,?)
        """, s_id, s_name, s_price, s_url)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 2删除皮肤
    # 查找皮肤是否存在
    def search_skin(self, s_id):
        self.cursor.execute("""
        select S_ID
        from skin_list
        where S_ID=?
        """, s_id)
        row = self.cursor.fetchone()
        return row

    # 删除（关联）
    def modify_skin_del(self, s_id):
        self.cursor.execute("""
        begin transaction del_skin

            delete from skin_list
            where S_ID=?
            delete from skin_property
            where S_ID=?
            update player
            set Skin_ID='1000'
            where Skin_ID=?

        if  @@ERROR!=0 rollback transaction del_skin
        else commit transaction del_skin
        """, s_id, s_id, s_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 3修改皮肤
    def modify_skin_change(self, s_id, s_price, s_url):
        self.cursor.execute("""
        update skin_list
        set S_Price=?,S_URL=?
        where S_ID=?
        """, s_price, s_url, s_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 4修改道具
    def modify_item_change(self, i_id, i_price, i_url):
        self.cursor.execute("""
        update item_list
        set I_Price=?,I_URL=?
        where I_ID=?
        """, i_price, i_url, i_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 812查询所有玩家列表
    def get_all_player(self):
        self.cursor.execute("""
        select P_ID,P_Username,P_Password
        from player
        """)
        row = self.cursor.fetchall()
        return row

    # 814删除玩家账号
    # ##################未完，所有含有P_ID的都要删掉-已添加
    def del_player_account(self, p_id):
        self.cursor.execute("""
        begin transaction del_player_account

            delete from player
            where P_ID=?
            delete from record
            where P_ID=?
            delete from match
            where P1_ID=? or P2_ID=?
            delete from friend
            where P1_ID=? or P2_ID=?
            delete from skin_property
            where P_ID=?
            delete from item_property
            where P_ID=?

        if  @@ERROR!=0 rollback transaction del_player_account
        else commit transaction del_player_account
        """, p_id, p_id, p_id, p_id, p_id, p_id, p_id, p_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 816查询所有普通管理员
    def get_normal_admin(self):
        self.cursor.execute("""
        select A_ID,A_Username,A_Password
        from admin
        where A_Identity='0'
        """)
        row = self.cursor.fetchall()
        return row

    # 818删除管理员
    def del_admin(self, a_id):
        self.cursor.execute("""
        delete from admin
        where A_ID=? and A_Identity='0'
        """, a_id)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 820-1查是否有aid的管理员
    # 使用800

    # 820-2增加管理员
    def add_admin(self, a_id, a_username, a_password, a_identity):
        self.cursor.execute("""
        insert into admin (A_ID,A_Username,A_Password,A_Identity)
        values (?,?,?,?)
        """, a_id, a_username, a_password, a_identity)
        self.cnxn.commit()
        return self.cursor.rowcount

    # 824查询gameid的对局
    def get_match(self, game_id):
        self.cursor.execute("""
        select P1_ID,P2_ID,D_ID,StartTime,EndTime,P1_PointChange,P2_PointChange
        from match
        where Game_ID=?
        """, game_id)
        row = self.cursor.fetchone()
        return row




'''
db = Database()

db.add_item_list(0, 'accel potion', 10, 'accelerate potion, used in game', 'none')
db.add_item_property('91906712', '0', 0)

db.add_stage(0, '初级', 9, 9, 10, 1, 1)
db.add_stage(1, '中级', 16, 16, 40, 2, 2)
db.add_stage(2, '高级', 16, 30, 99, 3, 3)
'''

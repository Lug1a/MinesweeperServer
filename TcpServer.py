# 服务器端代码
import json
import random
from math import log
from socket import *
import os
from time import ctime, localtime, strftime
import time
import threading
from cmd import Cmd

from database import *

lock = threading.Lock()  # 创建一个锁


# 服务器端socket
class TcpServerSocket(Cmd):
    def __init__(self):
        self.client_socket_list = []  # 存各个与服务器建立连接的socket对象与其对应的登陆id，若socket对象对应客户端未登陆，id填''空字符
        self.addr_list = []  # 存储每个连接的地址
        self.ID_list = []  # 某个连接的客户端成功登陆后，向本list存入登陆的用户id，用于防止同账号重复登陆
        self.matching_pool = []  # 匹配池
        self.gaming_pool = []  # 游戏池,每一项格式 [a的ID，a的socket，b的ID，b的socket,对局ID，对局开始时间, 游戏难度, a是否断线， b是否断线]

        self.skinlist = [
            ["0820001",
             "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1595766234979&di=63dbd28f41929e2f3ba5697f0da47e1b&imgtype=0&src=http%3A%2F%2Fbbs.orzice.com%2Fdata%2Fattachment%2Fforum%2F201802%2F14%2F102510j91highd9zieecdh.jpg",
             "100"],
            ["0820002",
             "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1595766292724&di=c5a61af635c4163ecf9e29483857a3f8&imgtype=0&src=http%3A%2F%2Fpic1.win4000.com%2Fwallpaper%2F7%2F579ef5112d8d7.jpg",
             "110"],
            ["0820003",
             "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1595766325740&di=e69bef5a84f29fda29d3b935eed2ca9c&imgtype=0&src=http%3A%2F%2Fattach.bbs.miui.com%2Fforum%2F201307%2F17%2F210102zcl75v557n4od478.jpg",
             "120"],
            ["0820004", "http://p15.qhmsg.com/t01e2252d21f5bf45a5.jpg", "130"]]
        self.tools = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1595763643935&di=3f32a34fd774f9a24ca320020b2060a6&imgtype=0&src=http%3A%2F%2Fbpic.588ku.com%2Felement_origin_min_pic%2F00%2F61%2F78%2F7456db7f599becf.jpg"
        self.toolsprice = "10"
        # self.level_data = [[10, 10, 10, "初级"], [14, 14, 20, "中级"], [17, 17, 30, "高级"], [20, 20, 40, "大师"]]
        # self.level_data = []

        self.db = Database()
        # 初始化从数据库获得当前最大的game_id
        self.gameID = int(self.db.get_match_game_id()[0]) + 1  # 对局序号，每生成一个对局后该变量加1

        self.start_time = ctime()
        print('     starting ', self.start_time)

    # 返回数据库是否成功连接
    def get_success(self):
        return self.db.success

    # 创建socket对象，绑定端口
    def conf(self):
        self.host = '10.128.196.18'
        self.port = 8090
        self.bufsize = 1024 * 1024
        self.addr = (self.host, self.port)

        # 声明一个socket对象
        self.tcp_server_sock = socket(AF_INET, SOCK_STREAM)
        self.tcp_server_sock.bind(self.addr)
        self.tcp_server_sock.listen(30)  # 最多30个tcp连接
        print('     waiting for connection...')

    # 建立tcp连接，并对每个连接创建线程进行消息的监听
    def accept(self):
        i = 0
        while True:
            client_socket, addr = self.tcp_server_sock.accept()
            # self.client_socket_list.append([client_socket, ''])
            if addr not in self.addr_list:
                self.addr_list.append(addr)
                self.client_socket_list.append([client_socket, ''])
                i = i + 1
                t = threading.Thread(target=self.rec, args=(client_socket, addr), name="线程" + str(i))
                t.start()
            print('     client connected from: ', addr)

    # 发送消息
    def send(self, client_socket, data):
        client_socket.send(data.encode('utf-8'))

    # 监听端口，接收消息
    def rec(self, client_socket, addr):
        while True:
            try:
                data = client_socket.recv(self.bufsize)
                data = data.decode('utf-8')
                if not data:
                    continue
                if data == "disconnection":
                    for socket_id in self.client_socket_list:  # 找到本socket
                        if socket_id[0] == client_socket:
                            if socket_id[1] != '':  # 如果本socket有登陆的id
                                self.ID_list.remove(socket_id[1])  # 登陆列表移除本id
                                socket_id[1] = ''
                    for gamer in self.gaming_pool:  # 游戏池寻找自己
                        if gamer[1] == client_socket:  # 如果是对战双方的A
                            if gamer[8] == 1:  # 如果B也断线，移除该对局
                                self.gaming_pool.remove(gamer)
                            else:  # 如果只是自己断线，则设置自己掉线
                                gamer[7] = 1
                        elif gamer[3] == client_socket:  # 如果是对战双方的B
                            if gamer[7] == 1:  # 如果A也断线，移除该对局
                                self.gaming_pool.remove(gamer)
                            else:  # 如果只是自己断线，则设置自己掉线
                                gamer[8] = 1
                    for gamer in self.matching_pool:  # 匹配池寻找自己,有则移除
                        if gamer[1] == client_socket:
                            self.send(client_socket, "209 0")
                            self.matching_pool.remove(gamer)
                            print("匹配取消，匹配池：", self.matching_pool)
                    client_socket.close()
                    print("     disconnection:" + str(addr) + " offline" + '\n')
                    break

                self.process_data(client_socket, data, addr)

            except:  # 连接出错，则关闭连接
                for socket_id in self.client_socket_list:  # 找到本socket
                    if socket_id[0] == client_socket:
                        if socket_id[1] != '':  # 如果本socket有登陆的id
                            self.ID_list.remove(socket_id[1])  # 登陆列表移除本id
                            socket_id[1] = ''
                for gamer in self.gaming_pool:  # 游戏池寻找自己
                    if gamer[1] == client_socket:  # 如果是对战双方的A
                        if gamer[8] == 1:  # 如果B也断线，移除该对局
                            self.gaming_pool.remove(gamer)
                        else:  # 如果只是自己断线，则设置自己掉线
                            gamer[7] = 1
                    elif gamer[3] == client_socket:  # 如果是对战双方的B
                        if gamer[7] == 1:  # 如果A也断线，移除该对局
                            self.gaming_pool.remove(gamer)
                        else:  # 如果只是自己断线，则设置自己掉线
                            gamer[8] = 1
                for gamer in self.matching_pool:  # 匹配池寻找自己,有则移除
                    if gamer[1] == client_socket:
                        self.send(client_socket, "209 0")
                        self.matching_pool.remove(gamer)
                        print("匹配取消，匹配池：", self.matching_pool)

                client_socket.close()
                print("     disconnection:" + str(addr) + " offline" + '\n')
                break

    # 对从客户端接收的消息进行分析处理，与数据库进行交互，计算出发送的消息
    def process_data(self, client_socket, data, addr):
        data_list = data.split()  # 对获取的消息进行切片

        if data_list[0] == "100":  # 用户登陆
            print("100:收到用户:" + data_list[1] + "的登陆请求")

            userID = data_list[1]  # 用户ID
            userPWD = data_list[2]  # 用户密码

            # login分为4种情况 1:账号不存在 2:密码错误 3:账号已在别处登陆,登陆失败 4:登陆成功， 给客户端回送消息
            if userID in self.ID_list:  # 查看用户id是否已登陆（login = 3）
                login = 3
            else:  # 如果没有则与数据库进行交互
                # 在数据表中查看用户id是否存在（login = 1），密码是否正确（login = 2），如果全部无误则login = 4
                pwd = self.db.get_player_password(userID)
                if pwd is None:
                    login = 1
                elif pwd[0] != userPWD:
                    login = 2
                else:
                    login = 4

            # 如果可以登陆
            if login == 4:
                self.ID_list.append(userID)
                for socket_id in self.client_socket_list:
                    if socket_id[0] == client_socket:
                        socket_id[1] = userID

            # 向客户端回送消息
            self.send(client_socket, "101" + ' '
                      + str(login))

        if data_list[0] == "102":  # 用户注册
            print("102:收到用户:" + data_list[1] + "的注册请求")

            # 随机给用户分配一个8位数ID
            while (True):
                randNum = random.randint(10000000, 99999999)
                newID = str(randNum)
                # 进数据库查询，看看生成的用户id（账号）在数据库里面有没有重复,如果不重复了，就设置 repeat = 0
                pwd = self.db.get_player_password(newID)

                if pwd is None:
                    break

            username = data_list[1]  # 用户名
            password = data_list[2]  # 用户密码

            # 把newID,username和password存入数据库
            ret = self.db.add_player(newID, username, password, 0, 0, 50, 50, '1000')
            if ret == 0:
                print('failed')

            # 发送消息
            self.send(client_socket, "103" + ' '
                      + str(newID))

        if data_list[0] == "200":  # 用户主界面数据请求
            print("200:收到用户:" + data_list[1] + "的主界面数据请求")

            userID = data_list[1]  # 用户账号

            # 根据userID，在数据库中查询用户的 用户名 积分 金币 背景音乐音量 音效音量 使用的大厅皮肤url
            ret = self.db.get_my_player_info(userID)

            username = ret[1]  # 用户名
            point = ret[2]  # 积分
            gold = ret[3]  # 金币
            background_volume = ret[4]  # 背景音乐音量，百分制
            sound_volume = ret[5]  # 音效音量，百分制
            skin_url = ret[6]  # 使用的皮肤url

            # 返回数据
            self.send(client_socket, "201" + ' '
                      + username + ' '
                      + userID + ' '
                      + str(point) + ' '
                      + str(gold) + ' '
                      + str(background_volume) + ' '
                      + str(sound_volume) + ' '
                      + str(skin_url))

        if data_list[0] == "202":  # 关卡数据请求与用户道具数据请求
            print("202:收到用户:" + data_list[1] + "的关卡数据请求与用户道具数据请求")

            # 在数据库中查询 关卡数据与用户道具数量（道具只有一种）
            # 关卡数据导出的格式   [长（高？），宽，雷数，关卡名] (数据库里面存的面积，长和宽用面积开方取整数得到)
            ret1 = self.db.get_stage_info()
            level_data = []
            if ret1 is not None:
                for every_stage in ret1:
                    a_level = [every_stage[2], every_stage[3], every_stage[4], every_stage[1]]
                    level_data.append(a_level)

            # 加速药水道具数量
            ret2 = self.db.get_item_info(data_list[1])
            if ret2 is not None:
                stagenum = ret2[0][1]
            else:
                stagenum = -1

            # 返回数据
            self.send(client_socket, "203" + '@'
                      + json.dumps(level_data) + '@'
                      + str(stagenum))

        if data_list[0] == "204":  # 请求排行榜数据
            print("204:收到用户:" + data_list[1] + "的排行榜数据请求")

            # 在数据库中查询用户积分并进行排行，存入rank_list中
            # rank_list里面每一项的格式如下， 按积分顺序由小到大排序，每个玩家的格式是[ID,用户名,积分(字符串格式)]
            ret = self.db.get_player_ordered_by_integral()
            rank_list = []
            if ret is not None:
                for every_player in ret:
                    a_player = [every_player[0], every_player[1], str(every_player[2])]
                    rank_list.append(a_player)

            # 返回数据
            self.send(client_socket, "205" + '@'
                      + json.dumps(rank_list))

        if data_list[0] == "206":  # 请求玩家战绩数据
            print("206:收到用户:" + data_list[1] + "的查询玩家战绩数据请求")

            my_userID = data_list[1]  # 自己的用户账号
            query_userID = data_list[2]  # 查询的用户账号

            # 通过query_userID，在数据库中查询该被查询用户的 用户名，积分数，金币数，战绩数据
            ret1 = self.db.get_other_player_info(query_userID)
            # 其中战绩数据存入exploits_list中，exploits_list（二维数组）里面每一项的格式如下（注意除第二项外都要转成int或者float）
            ret2 = self.db.get_other_player_record(query_userID, 0)
            ret3 = self.db.get_other_player_record(query_userID, 1)
            # [是否是单人游戏（0代表是）,难度名称,游戏次数，成功率（0-1之间,4位小数），平均每局时长（2位小数），平均完成度（0-1之间,4位小数）]
            exploits_list = []

            if len(ret2) != 0:
                for every_rec_s in ret2:
                    a_record_s = [0,
                                  every_rec_s[0],
                                  every_rec_s[1],
                                  float(every_rec_s[2] / every_rec_s[1]),
                                  float(every_rec_s[3] / every_rec_s[1]),
                                  float(every_rec_s[4] / every_rec_s[1])]
                    exploits_list.append(a_record_s)
            if len(ret3) != 0:
                for every_rec_p in ret3:
                    a_record_p = [1,
                                  every_rec_p[0],
                                  every_rec_p[1],
                                  float(every_rec_p[2] / every_rec_p[1]),
                                  float(every_rec_p[3] / every_rec_p[1]),
                                  float(every_rec_p[4] / every_rec_p[1])]
                    exploits_list.append(a_record_p)

            query_username = ret1[1]  # 查询用户的用户名
            point = ret1[2]  # 积分
            gold = ret1[3]  # 金币
            if my_userID == query_userID:  # 如果查询的用户是自己，该项为0
                is_friend = 0
            else:  # 如果查询的用户不是自己

                # 在数据库中查询 用户是否是好友（0为不是，1为是, 2为等待回应）
                ret4 = self.db.get_other_player_if_friend(my_userID, query_userID)
                if ret4 is None:
                    is_friend = 0
                elif ret4[0] is None:
                    is_friend = 2
                else:
                    is_friend = 1

            # 返回数据
            self.send(client_socket, "207" + '@'
                      + query_userID + '@'
                      + query_username + '@'
                      + str(point) + '@'
                      + str(gold) + '@'
                      + json.dumps(exploits_list) + '@'
                      + str(is_friend))

        if data_list[0] == "208":  # 请求开始匹配
            print("208:收到用户:" + data_list[1] + "的开始匹配请求")

            data_list = [data_list[1], data_list[2], data_list[3], data_list[4]]
            name = threading.current_thread().name
            flag = 0

            with lock:  # 加锁，防止同时对匹配池读写
                # 遍历匹配池查找可以匹配的对手
                if len(self.matching_pool) > 0:
                    for gamer in self.matching_pool:
                        if gamer[0][2] == data_list[2]:  # 如果同难度且该玩家在匹配池，匹配成功
                            print(name, "匹配成功,", gamer[0][3], "vs", data_list[3])

                            # 自己发送回复信息
                            self.send(client_socket, "209" + ' '
                                      + '1' + ' '
                                      + gamer[0][3] + ' '
                                      + gamer[0][1])
                            # 帮对手发送回复信息
                            self.send(gamer[1], "209" + ' '
                                      + '1' + ' '
                                      + data_list[3] + ' '
                                      + data_list[1])
                            # self.gaming_pool.append([data_list[0], client_socket, gamer[0][0], gamer[1], self.gameID,
                            #                         str(ctime()), gamer[0][2], 0, 0])  # 加入游戏池
                            self.gaming_pool.append([data_list[0], client_socket, gamer[0][0], gamer[1], self.gameID,
                                                     strftime("%Y-%m-%d %H:%M:%S", localtime()), gamer[0][2], 0,
                                                     0])  # 加入游戏池

                            self.gameID += 1
                            self.matching_pool.remove(gamer)  # 从匹配池里面移除匹配到的人
                            print("匹配成功，匹配池：", self.matching_pool)
                            flag = 1
                            break
                # 未匹配,加入匹配池
                if flag == 0:
                    self.matching_pool.append([data_list, client_socket])

        if data_list[0] == "208a":  # 请求取消匹配
            print("208a:收到用户:" + data_list[1] + "的取消匹配请求")
            with lock:  # 加锁，防止同时对匹配池读写
                # 匹配池寻找自己
                for gamer in self.matching_pool:
                    # print(208, "a success", self.matching_pool)
                    if gamer[1] == client_socket:
                        self.send(client_socket, "209 0")
                        self.matching_pool.remove(gamer)
                        print("匹配取消，匹配池：", self.matching_pool)

        if data_list[0] == "300":  # 扫雷游戏结束更新玩家数据
            print("300:收到用户:" + data_list[1] + "的扫雷游戏结束，更新玩家数据请求")

            userID = data_list[1]  # 用户账号
            level = int(data_list[2]) - 1  # 游戏难度l
            time = int(data_list[3])  # 花费时间t
            mine_num = int(data_list[4])  # 排雷个数n
            stagenum = int(data_list[5])  # 现在拥有的道具数量

            # 在数据库里面找到 该对局难度对应的 总雷数total_mine 和 积分金币计算规则序号 index 取值为(0-3)，暂时只设立了4套规则
            ret1 = self.db.get_a_stage(level)
            if ret1 is not None:
                total_mine = ret1[0]
                index = ret1[1]
            else:
                index = 0
                total_mine = 1

            # 用存在服务器的对应规则，利用扫雷数量（等于总雷数为扫雷成功）,用时,难度级别,算出玩家的积分变化和金币变化
            if time == -1 or mine_num == -1:  # 强行退出
                success = -1
            elif mine_num == total_mine:  # 扫雷成功
                success = 1
            else:  # 扫雷失败
                success = 0

            point_change = 0  # 积分变化数
            gold_change = 0  # 金币变化数

            # ##############################此处设计积分金币计算方法

            if mine_num != 0:
                ave_time = int(time / mine_num)  # 平均每个雷用时
            else:
                ave_time = 10000
            complete = int(mine_num / total_mine)  # 完成度
            # 积分规则（建议取0,1）
            if index == 0:
                base_point = 50 + 20 * level
                if success == 1:
                    point_change = base_point + int(50 // (ave_time + 1))
                elif success == 0:
                    point_change = -base_point + int(35 * complete // (ave_time + 1))
                else:
                    point_change = -base_point * 2

                gold_change = 2 * point_change
            elif index == 1:
                base_point = 20 + 40 * level
                if success == 1:
                    point_change = base_point + int(80 // (ave_time + 1))
                elif success == 0:
                    point_change = -base_point + int(20 * complete // (ave_time + 1))
                else:
                    point_change = -base_point * 4

                gold_change = 2 * point_change
            elif index == 2:
                base_point = 50 + 20 * level
                if success == 1:
                    point_change = base_point + int(50 // int(log((ave_time + 1), 2) + 1))
                elif success == 0:
                    point_change = -base_point + int(35 * complete // int(log((ave_time + 1), 2) + 1))
                else:
                    point_change = -base_point * 2

                gold_change = 2 * point_change
            elif index == 3:
                base_point = 20 + 40 * level
                if success == 1:
                    point_change = base_point + int(80 // int(log((ave_time + 1), 2) + 1))
                elif success == 0:
                    point_change = -base_point + int(20 * complete // int(log((ave_time + 1), 2) + 1))
                else:
                    point_change = -base_point * 4

                gold_change = 2 * point_change

            # point_change = 10 + index * 10
            # gold_change = 10 + index * 10

            # 1.把变化后的积分金币数存入数据库 2.在战绩数据库修改玩家的战绩数据 3.修改拥有的道具数量

            # 获取玩家的金币数以防金币被扣成负数（太惨了）
            player_gold = 0
            ret2 = self.db.get_player_gold(userID)
            if ret2 is not None:
                player_gold = ret2[0]
            if player_gold + gold_change <= 0:
                gold_change = (-1) * player_gold

            if success == -1:  # 强行退出只扣分扣钱不算场次
                self.db.forced_exit(userID, point_change, gold_change, stagenum)
            else:
                # 判断p_id是否已经有d_id的记录了
                ret3 = self.db.get_a_record(userID, level, 0)
                if ret3 is None:  # 如果没有
                    self.db.update_player_add_record(userID, point_change, gold_change,
                                                     level, 0, success, time, mine_num / total_mine, stagenum)
                else:  # 如果有
                    self.db.update_player_update_record(userID, point_change, gold_change,
                                                        level, 0, success, time, mine_num / total_mine, stagenum)

            # 返回数据
            self.send(client_socket, "301" + ' '
                      + str(point_change) + ' '
                      + str(gold_change))

        if data_list[0] == "302":  # 扫雷游戏结束更新玩家数据（匹配）
            print("302:收到用户:" + data_list[1] + "的匹配对战结束，更新玩家数据请求")
            print(self.gaming_pool)
            with lock:  # 加锁，防止同时对游戏池读写
                flag = 0
                # 游戏池寻找自己
                for gamer in self.gaming_pool:
                    if gamer[1] == client_socket:  # 如果是对战双方的A
                        flag = 1
                        # todo 以下5行是需要用到的数据
                        enemy_ID = gamer[2]  # 获取对手的ID
                        enemy_client_socket = gamer[3]  # 获取对手的通信接口
                        gameID = gamer[4]  # 游戏ID
                        start_time = gamer[5]  # 游戏开始时间
                        game_level = gamer[6]  # 游戏难度

                        a_game = gamer
                        # self.gaming_pool.remove(gamer)
                        # print("对战", gameID, "结束，游戏池：", self.gaming_pool)
                        break

                    elif gamer[3] == client_socket:  # 如果是对战双方的B
                        flag = 1
                        enemy_ID = gamer[0]  # 获取对手的ID
                        enemy_client_socket = gamer[1]  # 获取对手的通信接口
                        gameID = gamer[4]  # 游戏ID
                        start_time = gamer[5]  # 游戏开始时间
                        game_level = gamer[6]  # 游戏难度

                        a_game = gamer
                        # self.gaming_pool.remove(gamer)
                        # print("对战", gameID, "结束，游戏池：", self.gaming_pool)
                        break

                # print("对战", gameID, "结束，游戏池：", self.gaming_pool)
                self.gaming_pool.remove(a_game)

            if flag == 1:  # 如果在游戏池里面找到了自己
                time = int(data_list[3])  # 花费时间
                mine_num = int(data_list[4])  # 排雷个数
                stagenum = int(data_list[5])  # 现在拥有的道具数量

                userID = data_list[1]  # 用户账号
                end_time = strftime("%Y-%m-%d %H:%M:%S", localtime())  # 对局结束时间

                print(data_list)

                # todo:在数据库里面找到 该对局难度对应的 总雷数total_mine 和 积分金币计算规则序号 index 取值为(0-3)，暂时只设立了4套规则
                ret1 = self.db.get_a_stage(str(int(game_level) - 1))

                print(ret1)

                if ret1 is not None:
                    total_mine = int(ret1[0])
                    index = int(ret1[1])
                else:
                    index = 0
                    total_mine = 1

                # 用存在服务器的对应规则，利用扫雷数量（等于总雷数为扫雷成功）,用时,难度级别,算出玩家的积分变化和金币变化
                if time == -1 or mine_num == -1:  # 强行退出
                    success = -1
                elif mine_num == total_mine:  # 扫雷成功
                    success = 1
                else:  # 扫雷失败
                    success = 0

                print(success)

                my_point_change = 0  # 自己的积分变化数
                enemy_point_change = 0  # 对方的积分变化数
                my_gold_change = 0  # 自己的金币变化数
                enemy_gold_change = 0  # 对方的金币变化数

                if mine_num != 0:
                    ave_time = int(time / mine_num)  # 平均每个雷用时
                else:
                    ave_time = 10000
                complete = int(mine_num / total_mine)  # 完成度
                # 积分规则（建议取0,1）
                if index == 0:
                    base_point = 50 + 20 * int(game_level)
                    if success == 1:
                        my_point_change = base_point + int(50 // (ave_time + 1))
                    elif success == 0:
                        my_point_change = -base_point + int(35 * complete // (ave_time + 1))
                    else:
                        my_point_change = -base_point * 2

                    my_gold_change = 2 * my_point_change
                    enemy_point_change = -my_point_change
                    enemy_gold_change = 2 * enemy_point_change
                elif index == 1:
                    base_point = 20 + 40 * int(game_level)
                    if success == 1:
                        my_point_change = base_point + int(80 // (ave_time + 1))
                    elif success == 0:
                        my_point_change = -base_point + int(20 * complete // (ave_time + 1))
                    else:
                        my_point_change = -base_point * 4

                    my_gold_change = 2 * my_point_change
                    enemy_point_change = -my_point_change
                    enemy_gold_change = 2 * enemy_point_change
                elif index == 2:
                    base_point = 50 + 20 * int(game_level)
                    if success == 1:
                        my_point_change = base_point + int(50 // int(log((ave_time + 1), 2) + 1))
                    elif success == 0:
                        my_point_change = -base_point + int(35 * complete // int(log((ave_time + 1), 2) + 1))
                    else:
                        my_point_change = -base_point * 2

                    my_gold_change = 2 * my_point_change
                    enemy_point_change = -my_point_change
                    enemy_gold_change = 2 * enemy_point_change
                elif index == 3:
                    base_point = 20 + 40 * int(game_level)
                    if success == 1:
                        my_point_change = base_point + int(80 // int(log((ave_time + 1), 2) + 1))
                    elif success == 0:
                        my_point_change = -base_point + int(20 * complete // int(log((ave_time + 1), 2) + 1))
                    else:
                        my_point_change = -base_point * 4

                    my_gold_change = 2 * my_point_change
                    enemy_point_change = -my_point_change
                    enemy_gold_change = 2 * enemy_point_change

                print(my_point_change, my_gold_change, enemy_point_change, enemy_gold_change)

                # todo：1.把变化后的积分金币数存入数据库 2.在战绩数据库修改对战双方的战绩数据 3.把对局数据存入匹配对局数据表 4.修改拥有的道具数量

                print("break1")

                # 获取双方玩家的金币以防被扣成负数
                my_gold = 0
                enemy_gold = 0
                ret2 = self.db.get_player_gold(userID)
                if ret2 is not None:
                    my_gold = ret2[0]
                if my_gold + my_gold_change <= 0:
                    my_gold_change = (-1) * my_gold
                ret3 = self.db.get_player_gold(enemy_ID)
                if ret3 is not None:
                    enemy_gold = ret3[0]
                if enemy_gold + enemy_gold_change <= 0:
                    enemy_gold_change = (-1) * enemy_gold

                print(my_point_change, my_gold_change, enemy_point_change, enemy_gold_change)

                print(userID, enemy_ID, str(int(game_level) - 1), gameID, start_time, end_time, my_point_change,
                      enemy_point_change)
                # 记录match
                self.db.save_match(userID, enemy_ID, str(int(game_level) - 1), gameID, start_time, end_time,
                                   my_point_change, enemy_point_change)

                if success == -1:  # 强行退出
                    self.db.forced_exit_without_item(userID, my_point_change, my_gold_change)
                else:
                    # 判断我是否已经有d_id的记录了
                    ret4 = self.db.get_a_record(userID, str(int(game_level) - 1), 1)

                    if ret4 is None:  # 如果没有

                        print(userID, my_point_change, my_gold_change, str(int(game_level) - 1), 1, success, time,
                              mine_num / total_mine)
                        self.db.update_player_add_record_p(userID, my_point_change, my_gold_change,
                                                           str(int(game_level) - 1), 1, success, time,
                                                           mine_num / total_mine)
                    else:  # 如果有
                        print(userID, my_point_change, my_gold_change, str(int(game_level) - 1), 1, success, time,
                              mine_num / total_mine)
                        self.db.update_player_update_record_p(userID, my_point_change, my_gold_change,
                                                              str(int(game_level) - 1), 1, success, time,
                                                              mine_num / total_mine)

                # 另一方记录金钱和积分变化
                self.db.forced_exit_without_item(enemy_ID, enemy_point_change, enemy_gold_change)

                try:
                    # 返回数据
                    # 给自己的客户端返回数据
                    self.send(client_socket, "303" + ' '
                              + str(my_point_change) + ' '
                              + str(my_gold_change))
                    # 给对手的客户端返回数据
                    self.send(enemy_client_socket, "303" + ' '
                              + str(enemy_point_change) + ' '
                              + str(enemy_gold_change))
                except:
                    print(enemy_ID, "已断开连接")

        if data_list[0] == "304":  # 匹配扫雷结束后更新道具数量
            print("304:收到用户:" + data_list[1] + "的更新道具数量请求")
            print(data_list)
            # todo:success代表是否成功，记得赋值,把stagenum存入数据库
            success = 1
            userID = data_list[1]  # 用户账号
            stagenum = int(data_list[2])  # 现在剩余的道具数量

            self.db.change_item_quantity(userID, stagenum)

            # 返回数据
            self.send(client_socket, "305" + ' '
                      + str(success))

        if data_list[0] == "400":  # 请求数据打开商店
            print("400:收到用户:" + data_list[1] + "的打开商店请求")
            userID = data_list[1]  # 用户帐号
            skinlist = []
            toolsurl = ""
            toolsprice = int

            # 从table：皮肤里查询所有的皮肤ID、皮肤URL、皮肤价格，存入二维数组skinlist[[ele1],[ele2]...]元素格式如下
            # [皮肤ID,皮肤URL,皮肤价格]
            ret1 = self.db.get_shop_skin()
            if ret1 is not None:
                for every_skin in ret1:
                    a_skin = [every_skin[0], every_skin[3], str(every_skin[2])]
                    skinlist.append(a_skin)

            # 从table：游戏道具里查询道具图片URL存入toolsurl，查询道具价格存入toolsprice
            ret2 = self.db.get_shop_item()
            if ret2 is not None:
                toolsurl = ret2[0][4]
                toolsprice = str(ret2[0][2])

            # 正式
            data = toolsurl + " " + toolsprice
            for i in skinlist:
                data = data + " " + i[0] + " " + i[1] + " " + i[2]
            self.send(client_socket, "401 " + data)
            '''
            # 测试
            data = self.tools + " " + self.toolsprice
            for i in self.skinlist:
                data = data + " " + i[0] + " " + i[1] + " " + i[2]
            self.send(client_socket, "401 " + data)'''

        if data_list[0] == "402":  # 请求购买皮肤
            print("402:收到用户:" + data_list[1] + "的购买皮肤请求,皮肤ID:" + data_list[2])
            userID = data_list[1]  # 用户帐号
            skinID = data_list[2]  # 购买皮肤ID
            key = int
            usergold = int
            skinprice = int

            # 在table：拥有皮肤 中查找是否存在userID和skinID对应的项，存在则key=1，不存在则key=0
            ret1 = self.db.get_skin_property(userID, skinID)
            if ret1 is not None:
                key = 1
            else:
                key = 0

            # 在table：玩家 中查询userID对应的金币gold，存入usergold
            ret2 = self.db.get_player_gold(userID)
            if ret2 is not None:
                usergold = ret2[0]
            else:
                usergold = 0

            # 在table：皮肤 中查询skinID对应的皮肤价格，存入skinprice
            ret3 = self.db.get_skin_price(skinID)
            if ret3 is not None:
                skinprice = ret3[0]
            else:
                skinprice = 0

            # 正式
            if key == 1:
                self.send(client_socket, "402b")
            elif key == 0:
                if usergold >= skinprice:

                    # 将table：玩家 中userID对应的gold减去skinprice
                    # 将table：拥有皮肤 中添加项（userID、skinID）
                    ret4 = self.db.buy_shop_skin(userID, skinID)

                    self.send(client_socket, "402a")

                else:
                    self.send(client_socket, "402c")
            """
            # 测试
            self.send(client_socket, "402a")
            """

        if data_list[0] == "403":  # 请求购买道具
            print("402:收到用户:" + data_list[1] + "的购买道具请求,购买数量:" + data_list[2])
            userID = data_list[1]  # 用户帐号
            num = int(data_list[2])  # 购买数量
            usergold = int
            toolsprice = int

            # 在table：玩家 中查询userID对应的金币gold，存入usergold
            ret1 = self.db.get_player_gold(userID)
            if ret1 is not None:
                usergold = ret1[0]
            else:
                usergold = 0

            # 在table：游戏道具 中查询道具价格，存入toolsprice
            ret2 = self.db.get_item_price('0')
            if ret2 is not None:
                toolsprice = ret2[0]
            else:
                toolsprice = 0

            # 正式
            if usergold >= toolsprice * num:

                # 将table：玩家 中userID对应的gold减去toolsprice * num
                # 将table：拥有道具 中userID对应的数量加上num
                ret3 = self.db.buy_shop_item(userID, '0', num)

                self.send(client_socket, "403a")

            else:
                self.send(client_socket, "403b")
            """
            # 测试
            self.send(client_socket, "403a")
            """

        if data_list[0] == "500":  # 请求打开背包
            print("500:收到用户:" + data_list[1] + "的打开背包请求")
            userID = data_list[1]  # 用户帐号
            skinlist = []
            toolsurl = ''
            toolsnum = int

            # 在table：拥有皮肤 中查询userID对应的skinID，并且用这些skinID在table：皮肤 中将皮肤URL、皮肤价格，
            #  存入二维数组skinlist[[ele1],[ele2]...]元素格式如下
            # [皮肤ID,皮肤URL,皮肤价格]
            ret1 = self.db.get_my_skin(userID)
            if ret1 is not None:
                for every_skin in ret1:
                    a_skin = [every_skin[0], every_skin[3], str(every_skin[2])]
                    skinlist.append(a_skin)

            # 从table：游戏道具 里查询道具图片URL存入toolsurl
            # 从table：拥有道具 里查询userID对应的道具数量存入toolsnum
            ret2 = self.db.get_my_item(userID)
            if ret2 is not None:
                toolsurl = ret2[0][5]
                toolsnum = ret2[0][2]

            # 正式
            data = toolsurl + " " + str(toolsnum)
            for i in skinlist:
                data = data + " " + i[0] + " " + i[1] + " " + i[2]

            self.send(client_socket, "501 " + data)
            """
            # 测试
            toolsnum="16"
            data = self.tools + " " + toolsnum
            for i in self.skinlist:
                data = data + " " + i[0] + " " + i[1] + " " + i[2]
            self.send(client_socket, "501 " + data)
            """

        if data_list[0] == "502":  # 皮肤设置
            print("502:收到用户:" + data_list[1] + "的皮肤设置请求")
            userID = data_list[1]  # 用户帐号
            skinID = data_list[2]  # 皮肤ID

            # 将table：玩家 中userID对应的使用皮肤ID更新成skinID
            ret = self.db.change_skin(userID, skinID)

            self.send(client_socket, "502a")

        if data_list[0] == "600":  # 请求打开好友列表
            print("600:收到用户:" + data_list[1] + "的打开好友列表请求")
            userID = data_list[1]  # 用户帐号
            friend_list = []

            #  friend_list为二维数组，每个好友格式为[ID，用户名，积分数，金币数]
            #  1.   在 table：好友 中查询userID的好友，即找到包含userID的条目（P1_ID , P2_ID两列都要找），
            #  2.   并记录该条目下的另一个玩家（如果userID是P1_ID则记录P2_ID，反之亦然）的id，存在friend_list[n][0]中  (n：第n个好友)
            #  3.   在 table：玩家 中依次查询 P_ID = friend_list[n][0]的条目中的P_UserName，Integral，Gold，分别存入friend_list[n][1]、friend_list[n][2]、friend_list[n][3]中
            #  5.   返回friend_list，如下：
            ret = self.db.get_friend_list(userID)
            if ret is not None:
                for every_friend in ret:
                    a_friend = [every_friend[0], every_friend[1], str(every_friend[2]), str(every_friend[3])]
                    friend_list.append(a_friend)
            print(friend_list)

            # friend_list = [["20365268", "我是小" + str(i), "1025", "12"] for i in range(50)]

            self.send(client_socket, "601" + '@'
                      + json.dumps(friend_list))

        if data_list[0] == "602":  # 请求改变好友关系
            print("602:收到用户:" + data_list[1] + "的改变好友关系请求")
            my_userID = data_list[1]  # 自己的账号
            friend_userID = data_list[2]  # 添加的好友账号
            is_add_friend = data_list[3]  # 取值0/1 ， 0为加好友，1为删好友，2为同意申请

            print(data_list)

            if is_add_friend == '0':
                # 如果is_add_friend是加好友（0）：向数据库好友table添加一条(my_userID,friend_userID,null)
                ret1 = self.db.add_friend(my_userID, friend_userID)
                print(ret1)

            if is_add_friend == '1':
                # 如果is_add_friend是删好友（1）：在数据库好友table找到P1_ID,P2_ID分别为my_userID,friend_userID或friend_userID,my_userID的条目，删除
                ret2 = self.db.delete_friend(my_userID, friend_userID)
                print(ret2)

            if is_add_friend == '2':
                # 此情况是applyUI同意好友申请专用的情况，提供当前时间
                # 格式化成 YYYY-MM-DD HH:MM:SS 形式
                friend_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
                ret3 = self.db.pass_friend_apply(my_userID, friend_userID, friend_time)
                print(ret3)

            self.send(client_socket, "603" + ' '
                      + str(1))

        if data_list[0] == "604":  # 请求打开申请列表
            print("602:收到用户:" + data_list[1] + "的打开申好友请列表请求")
            userID = data_list[1]  # 用户帐号
            apply_list = []

            # 生成applylist，list里每个元素为[用户名，用户ID]
            #   1.在 table：好友 中查询 P2_ID 为 userID 且 FriendTime 为 null 的条目
            #   2.将该条目下另一个玩家的ID（如果userID是P1_ID则记录P2_ID，反之亦然）存入applylist[n][1] （n为第n个好友）
            #   3.在 table：玩家 中查询applylist[n][1] 所对应的用户名，存入applylist[n][1]
            #   4.返回applylist，如下：
            ret = self.db.get_friend_apply(userID)
            if ret is not None:
                for every_apply in ret:
                    an_apply = [every_apply[1], every_apply[0]]
                    apply_list.append(an_apply)

            self.send(client_socket, "605" + '@'
                      + json.dumps(apply_list))

        if data_list[0] == "700":  # 请求打开设置界面
            print("700:收到用户:" + data_list[1] + "的打开设置请求")
            userID = data_list[1]  # 用户帐号

            # 在table:玩家  中查询userID条目的P_UserName，Background_Volume，Sound_Volume并分别存入username ，background_volume ，sound_volume
            ret = self.db.get_setting_info(userID)
            if ret is not None:
                username = ret[0]
                background_volume = ret[1]
                sound_volume = ret[2]
            else:
                username = "error"  # 用户名
                background_volume = 0  # 背景音乐音量，百分制
                sound_volume = 0  # 音效音量

            # 返回数据
            self.send(client_socket, "701" + '@'
                      + username + '@'
                      + userID + '@'
                      + str(background_volume) + '@'
                      + str(sound_volume))

        if data_list[0] == "702":  # 请求更改密码
            print("702:收到用户:" + data_list[1] + "的更改密码请求")
            userID = data_list[1]  # 用户帐号
            oldPassword = data_list[2]  # 用户输入的当前密码
            newPassword = data_list[3]  # 用户设置的新密码

            # 在 table：好友 中查询userID条目的，P_Password
            ret1 = self.db.get_player_password(userID)
            if ret1 is not None:
                realPassword = ret1[0]
            else:
                realPassword = ''

            # todo:
            if (oldPassword != realPassword):  # 修改失败
                self.send(client_socket, "703b")
            else:  # 修改成功
                # todo:在修改成功的if分支里，则修改 table：玩家 使userID条目的P_Password=newPassword
                ret2 = self.db.change_password(userID, newPassword)

                self.send(client_socket, "703a")

            # self.send(client_socket, "703a")

        if data_list[0] == "704":  # 请求保存音量设置
            print("704:收到用户:" + data_list[1] + "的保存音量设置请求")
            userID = data_list[1]  # 用户帐号
            BGM_volume = data_list[2]  # 背景音乐音量
            Sound_volume = data_list[3]  # 音效音量

            # 在 table：好友 中修改userID对应条目，令Background_Volume = BGM_Volume ，Sound_Volume = sound_Volumn
            ret = self.db.change_volume(userID, BGM_volume, Sound_volume)

            self.send(client_socket, "705a")

        if data_list[0] == "800":  # 管理员登陆
            print("800:收到管理员:" + data_list[1] + "的登陆请求")
            # 查看用户id是否在ID_list (初始化时定义了self.ID_list) 里面（是否已登陆）（login = 3）
            # 如果没有则与数据库进行交互， 在数据表（管理员的表）中查看用户id是否存在（login = 1），密码是否正确（login = 2），如果全部无误则login = 4
            # 分为4种情况 1:账号不存在 2:密码错误 3:账号已在别处登陆,登陆失败 4:登陆成功， 给客户端回送消息
            # 获取管理员用户名赋值给username， 最后查看该用户是否是超级管理员，不是的话is_super = 0, 是的话is_super = 1
            adminID = data_list[1]  # 用户ID
            adminPWD = data_list[2]  # 用户密码
            adminName = ''
            is_super = 0

            # login分为4种情况 1:账号不存在 2:密码错误 3:账号已在别处登陆,登陆失败 4:登陆成功， 给客户端回送消息
            if adminID in self.ID_list:  # 查看用户id是否已登陆（login = 3）
                login = 3
            else:  # 如果没有则与数据库进行交互
                # 在数据表中查看管理员id是否存在（login = 1），密码是否正确（login = 2），如果全部无误则login = 4
                ret = self.db.get_admin_login(adminID)
                print(ret)
                if ret is None:
                    login = 1
                elif ret[0] != adminPWD:
                    login = 2
                else:
                    login = 4
                    adminName = ret[1]
                    is_super = ret[2]  # 是否是超级管理员，不是的话is_super = 0, 是的话is_super = 1

            # 如果可以登陆
            if login == 4:
                self.send(client_socket, "801" + ' '
                          + str(login) + ' '
                          + adminName + ' '
                          + str(is_super))
                self.ID_list.append(adminID)
                for socket_id in self.client_socket_list:
                    if socket_id[0] == client_socket:
                        socket_id[1] = adminID
            else:
                self.send(client_socket, "801" + ' '
                          + str(login) + ' '
                          + 'none' + ' '
                          + str(0))

        if data_list[0] == "802":  # 管理员修改用户数据
            print("802:收到管理员:" + data_list[1] + "的修改用户数据请求")
            # todo: data_list[3]的值为1/2/3/4 ，代表要修改的数据项目，其意义如下
            changeData = int(data_list[2])
            op = data_list[3]
            userID = data_list[4]

            if op == '1':
                # 1：积分
                self.db.modify_player_integral(userID, changeData)
            if op == '2':
                # 2：金币
                self.db.modify_player_gold(userID, changeData)
            if op == '3':
                # 3：背景音乐音量
                self.db.modify_player_bgm(userID, changeData)
            if op == '4':
                # 4：点击音效
                self.db.modify_player_sound(userID, changeData)

                # todo: data_list[2]为修改后的值，在数据库中修改， 然后返回是否成功， 0为失败  1为成功

            self.send(client_socket, "803" + ' '
                      + str(1))

        if data_list[0] == "804":  # 管理员请求关卡数据
            print("804:收到管理员:" + data_list[1] + "的关卡数据请求")
            # todo:将数据库中的关卡数据以[[长，宽，雷数，关卡名称]，[长，宽，雷数，关卡名称]，[长，宽，雷数，关卡名称]]的形式存入leveldata
            level_data = []
            ret = self.db.get_stage_info()
            if ret is not None:
                for every_level in ret:
                    a_level = [every_level[2], every_level[3], every_level[4], every_level[1]]
                    level_data.append(a_level)

            data = "805"
            for i in level_data:
                for j in i:
                    data = data + " " + str(j)
            self.send(client_socket, data)

        if data_list[0] == "806":  # 管理员请求修改关卡
            print("806:收到管理员:" + data_list[1] + "的修改关卡数据请求")

            if len(data_list) == 3:
                self.send(client_socket, "807 0")
            else:
                if data_list[2] == "1":  # 增加关卡
                    key = 0
                    levelName = data_list[3]

                    ret1 = self.db.get_stage_info()
                    if len(ret1) != 0:
                        levelID = str(int(ret1[-1][0]) + 1)
                    else:
                        levelID = '0'

                    self.db.modify_stage_add(levelID, levelName, 0, 0, 0, 0, 0)
                    self.send(client_socket, "807 1")

                elif data_list[2] == "2":  # 删除关卡
                    lid = str(int(data_list[3]) - 1)
                    print(lid)
                    ret2 = self.db.search_stage(lid)
                    if ret2 is not None:
                        self.db.modify_stage_del(lid)

                        self.send(client_socket, "807 1")
                    else:
                        self.send(client_socket, "807 0")

                elif data_list[2] == "3":  # 修改关卡面积
                    lid = str(int(data_list[3]) - 1)
                    height = data_list[4]
                    width = data_list[5]
                    ret3 = self.db.search_stage(lid)
                    if ret3 is not None:
                        self.db.modify_stage_field(lid, height, width)
                        self.send(client_socket, "807 1")
                    else:
                        self.send(client_socket, "807 0")

                elif data_list[2] == "4":  # 修改关卡总雷数
                    lid = str(int(data_list[3]) - 1)
                    mine = int(data_list[4])
                    ret4 = self.db.search_stage(lid)
                    if ret4 is not None:
                        self.db.modify_stage_mine(lid, mine)
                        self.send(client_socket, "807 1")
                    else:
                        self.send(client_socket, "807 0")

                elif data_list[2] == "5":  # 切换积分金币规则
                    rule = data_list[3]
                    self.db.modify_stage_rule(str(rule))
                    self.send(client_socket, "807 1")

        if data_list[0] == "808":  # 管理员请求商城皮肤数据
            print("808:收到管理员:" + data_list[1] + "的商城数据请求")

            skinlist = []
            toolsurl = ""
            toolsprice = int
            # 从table：皮肤里查询所有的皮肤ID、皮肤URL、皮肤价格，存入二维数组skinlist[[ele1],[ele2]...]元素格式如下
            # [皮肤ID,皮肤URL,皮肤价格]
            ret1 = self.db.get_shop_skin()
            if ret1 is not None:
                for every_skin in ret1:
                    a_skin = [every_skin[0], every_skin[3], str(every_skin[2])]
                    skinlist.append(a_skin)

            # 从table：游戏道具里查询道具图片URL存入toolsurl，查询道具价格存入toolsprice
            ret2 = self.db.get_shop_item()
            if ret2 is not None:
                toolsurl = ret2[0][4]
                toolsprice = str(ret2[0][2])

            # 正式
            data = toolsurl + " " + toolsprice
            for i in skinlist:
                data = data + " " + i[0] + " " + i[1] + " " + i[2]
            self.send(client_socket, "809 " + data)

        if data_list[0] == "810":  # 管理员请求修改商城皮肤数据
            print("810:收到管理员:" + data_list[1] + "的修改商城数据请求")

            if data_list[2] == "1":  # 增加皮肤
                ret1 = self.db.get_shop_skin()
                if len(ret1) != 0:
                    skinID = str(int(ret1[-1][0]) + 1)
                else:
                    skinID = '1000'

                self.db.modify_skin_add(skinID, 'NONE', data_list[4], data_list[3])
                self.send(client_socket, "811 1")

            elif data_list[2] == "2":  # 删除皮肤
                key = 0
                sid = data_list[3]
                if sid != '1000':
                    ret2 = self.db.search_skin(sid)
                    if ret2 is not None:
                        self.db.modify_skin_del(sid)
                        key = 1
                        self.send(client_socket, "811 1")
                if key == 0:
                    self.send(client_socket, "811 0")

            elif data_list[2] == "3":  # 修改皮肤
                sid = data_list[3]
                price = data_list[5]
                url = data_list[4]
                ret3 = self.db.search_skin(sid)
                if ret3 is not None:
                    self.db.modify_skin_change(sid, price, url)
                    self.send(client_socket, "811 1")
                else:
                    self.send(client_socket, "811 0")

            elif data_list[2] == "4":  # 修改道具
                item_url = data_list[3]
                item_price = data_list[4]
                self.db.modify_item_change('0', item_price, item_url)
                self.send(client_socket, "811 1")

        if data_list[0] == "812":
            print("812:收到管理员:" + data_list[1] + "的查询玩家账号请求")
            # todo:查询 table：玩家 中的所有玩家的 P_ID、P_UserName、P_Password，并存入playerList里
            playerList = []
            ret1 = self.db.get_all_player()
            if ret1 is not None:
                for every_player in ret1:
                    a_player = [every_player[0], every_player[1], every_player[2]]
                    playerList.append(a_player)
            # todo:playerList为二维数组，每个元素是一个玩家，每个玩家的格式为：[玩家ID,用户名,密码]，如下：
            # playerList = [[111111, "小红", 123123], [2222222, "小白", 234234], [333333, "小黑", 345345]]
            self.send(client_socket, "813" + "@" + json.dumps(playerList))

        if data_list[0] == "814":
            print("814:收到管理员:" + data_list[1] + "的删除玩家账号请求")
            delPlayerID = data_list[2]
            if delPlayerID not in self.ID_list:
                # todo：删除table：玩家 中 P_ID = delPlayerID 的条目
                ret = self.db.del_player_account(delPlayerID)

                self.send(client_socket, "815 1")
            else:  # 用户登陆状态，暂时无法删除
                self.send(client_socket, "815 2")

        if data_list[0] == "816":
            print("816:收到超级管理员:" + data_list[1] + "的查询管理员账号请求")
            # todo:查询 table：管理员 中  Identity = 普通管理员 的所有管理员的 A_ID、A_AccountNum、A_Password，并存入administratorList里
            # todo:administratorList为二维数组，每个元素是一个管理员，每个管理员的格式为：[管理员ID,用户名,密码]，如下：
            # administratorList = [[111111, "管理员1", 123123], [2222222, "管理员2", 234234], [333333, "管理员3", 345345]]
            administratorList = []
            ret = self.db.get_normal_admin()
            if ret is not None:
                for every_admin in ret:
                    an_admin = [every_admin[0], every_admin[1], every_admin[2]]
                    administratorList.append(an_admin)

            self.send(client_socket, "817" + "@" + json.dumps(administratorList))

        if data_list[0] == "818":
            print("818:收到超级管理员:" + data_list[1] + "的删除管理员账号请求")
            delAdministratorID = data_list[2]
            # todo：删除table：管理员 中 A_ID =  delAdministratorID的条目
            ret = self.db.del_admin(delAdministratorID)
            print(ret)
            self.send(client_socket, "819 1")

        if data_list[0] == "820":
            print("820:收到超级管理员:" + data_list[1] + "的添加管理员请求")
            adminName = data_list[2]
            password = data_list[3]

            while (True):
                randNum = random.randint(10000000, 99999999)
                adminID = str(randNum)
                flag = 1

                # todo：在table：管理员 查询 A_ID = adminID 的条目是否已存在 ,若如果不存在，设置 flag = 0
                ret1 = self.db.get_admin_login('a' + adminID)
                if ret1 is None:
                    break

            # todo: 向table：管理员 写入条目：（adminID, adminName, password, "普通管理员"）
            ret2 = self.db.add_admin('a' + adminID, adminName, password, '0')

            self.send(client_socket, "821 " + "a" + str(adminID))

        if data_list[0] == "822":
            print("822:收到管理员:" + data_list[1] + "的查询战绩请求")
            userID = data_list[2]  # 被查询的玩家
            exploits_list = []

            # todo: 在 table：战绩 中查询 玩家 P_ID = userID 的 Single_Player_Game、D_ID、Game_Num、Suc_Rate、Ave_Time、Ave_Degree

            # todo：若该玩家存在:      令 flag=1 ;    将查询结果存入exploits_list中, 再 self.send(client_socket, "823@1@" + json.dumps(exploits_list))
            #       若该玩家不存在：    令 flag=0 ；仅执行 self.send(client_socket, "823@0")
            # 查询玩家是否存在
            ret1 = self.db.get_player_password(userID)
            print(ret1)
            if ret1 is None:  # 不存在
                self.send(client_socket, "823@0")
            else:  # 存在
                ret2 = self.db.get_other_player_record(userID, 0)  # 单人
                ret3 = self.db.get_other_player_record(userID, 1)  # 匹配
                print(ret2)
                print(ret3)
                # todo：exploits_list（二维数组）里面每一项的格式如下（注意除第二项外都要转成int或者float）
                # todo:[是否是单人游戏（0代表是）,难度名称,游戏次数，成功率（0-1之间,4位小数），平均每局时长（2位小数），平均完成度（0-1之间,4位小数）]
                if len(ret2) != 0:
                    for every_rec_s in ret2:
                        a_record_s = [0,
                                      every_rec_s[0],
                                      every_rec_s[1],
                                      float(every_rec_s[2] / every_rec_s[1]),
                                      float(every_rec_s[3] / every_rec_s[1]),
                                      float(every_rec_s[4] / every_rec_s[1])]
                        exploits_list.append(a_record_s)
                if len(ret3) != 0:
                    for every_rec_p in ret3:
                        a_record_p = [1,
                                      every_rec_p[0],
                                      every_rec_p[1],
                                      float(every_rec_p[2] / every_rec_p[1]),
                                      float(every_rec_p[3] / every_rec_p[1]),
                                      float(every_rec_p[4] / every_rec_p[1])]
                        exploits_list.append(a_record_p)
                print(exploits_list)
                self.send(client_socket, "823" + "@" + "1" + "@" + json.dumps(exploits_list))

        if data_list[0] == "824":
            print("824:收到管理员:" + data_list[1] + "的对局查询请求")
            gameID = data_list[2]
            combat = []
            # todo: 在table：匹配对局 中查询 Game_ID = gameID 的对局的 P1_ID、P2_ID、D_ID、StartTime、EndTime、P1_PointChange、P2_PointChange

            # todo:  若该对局存在：     将查询结果存入combat（一维数组）中, 再执行 self.send(client_socket, "825@1@" + json.dumps(combat))
            #                                    注：combat格式为[玩家1ID,玩家2ID,难度编号,开始时间,结束时间,玩家1积分变化,玩家2积分变化]
            #       若该对局不存在：    仅执行 self.send(client_socket, "825@0")
            # 并存入combat中，格式为[玩家1ID,玩家2ID,难度编号,开始时间,结束时间,玩家1积分变化,玩家2积分变化]
            print(data_list)
            ret = self.db.get_match(gameID)
            if ret is not None:  # 对局存在
                combat = [ret[0], ret[1], ret[2],
                          str(ret[3]), str(ret[4]),
                          ret[5], ret[6]]
                self.send(client_socket, "825" + "@" + "1" + "@" + json.dumps(combat))
            else:  # 不存在
                self.send(client_socket, "825@0")

        if data_list[0] == "826":  # 查询玩家账号是否存在
            print("826:收到管理员:" + data_list[1] + "查询玩家账号是否存在的请求")
            if len(data_list) == 2:
                login = 0
            else:
                userID = data_list[2]  # 用户ID

                # 在数据表中查看用户id是否存在（login = 1），密码是否正确（login = 2），如果全部无误则login = 4
                pwd = self.db.get_player_password(userID)
                if pwd is None:
                    login = 0
                else:
                    login = 1

            # 向客户端回送消息
            self.send(client_socket, "827" + ' '
                      + str(login))

        if data_list[0] == "828":  # 玩家主界面数据请求
            print("828:收到管理员:" + data_list[1] + "的玩家数据请求")

            userID = data_list[2]  # 用户账号

            # 根据userID，在数据库中查询用户的 用户名 积分 金币 背景音乐音量 音效音量 使用的大厅皮肤url
            ret = self.db.get_my_player_info(userID)

            username = ret[1]  # 用户名
            point = ret[2]  # 积分
            gold = ret[3]  # 金币
            background_volume = ret[4]  # 背景音乐音量，百分制
            sound_volume = ret[5]  # 音效音量，百分制
            skin_url = ret[6]  # 使用的皮肤url

            # 返回数据
            self.send(client_socket, "829" + ' '
                      + username + ' '
                      + userID + ' '
                      + str(point) + ' '
                      + str(gold) + ' '
                      + str(background_volume) + ' '
                      + str(sound_volume) + ' '
                      + str(skin_url))

        if data_list[0] == "830":  # 查看用户好友列表
            print("830:收到管理员:" + data_list[1] + "的查看用户好友列表请求")
            userID = data_list[2]  # 用户帐号
            friend_list = []

            #  friend_list为二维数组，每个好友格式为[ID，用户名，积分数，金币数]
            #  1.   在 table：好友 中查询userID的好友，即找到包含userID的条目（P1_ID , P2_ID两列都要找），
            #  2.   并记录该条目下的另一个玩家（如果userID是P1_ID则记录P2_ID，反之亦然）的id，存在friend_list[n][0]中  (n：第n个好友)
            #  3.   在 table：玩家 中依次查询 P_ID = friend_list[n][0]的条目中的P_UserName，Integral，Gold，分别存入friend_list[n][1]、friend_list[n][2]、friend_list[n][3]中
            #  5.   返回friend_list，如下：
            ret = self.db.get_friend_list(userID)
            if ret is not None:
                for every_friend in ret:
                    a_friend = [every_friend[0], every_friend[1], str(every_friend[2]), str(every_friend[3])]
                    friend_list.append(a_friend)

            # friend_list = [["20365268", "我是小" + str(i), "1025", "12"] for i in range(50)]

            self.send(client_socket, "831" + '@'
                      + json.dumps(friend_list))

        if data_list[0] == "832":  # 请求查看用户背包数据
            print("832:收到管理员:" + data_list[1] + "的查看用户背包数据请求")
            userID = data_list[2]  # 用户帐号
            skinlist = []
            toolsurl = ''
            toolsnum = int

            # 在table：拥有皮肤 中查询userID对应的skinID，并且用这些skinID在table：皮肤 中将皮肤URL、皮肤价格，
            #  存入二维数组skinlist[[ele1],[ele2]...]元素格式如下
            # [皮肤ID,皮肤URL,皮肤价格]
            ret1 = self.db.get_my_skin(userID)
            if ret1 is not None:
                for every_skin in ret1:
                    a_skin = [every_skin[0], every_skin[3], str(every_skin[2])]
                    skinlist.append(a_skin)

            # 从table：游戏道具 里查询道具图片URL存入toolsurl
            # 从table：拥有道具 里查询userID对应的道具数量存入toolsnum
            ret2 = self.db.get_my_item(userID)
            if ret2 is not None:
                toolsurl = ret2[0][5]
                toolsnum = ret2[0][2]

            # 正式
            data = toolsurl + " " + str(toolsnum)
            for i in skinlist:
                data = data + " " + i[1]

            self.send(client_socket, "833 " + data)
            """
            # 测试
            toolsnum="16"
            data = self.tools + " " + toolsnum
            for i in self.skinlist:
                data = data + " " + i[0] + " " + i[1] + " " + i[2]
            self.send(client_socket, "501 " + data)
            """


def main():
    x = TcpServerSocket()
    x.conf()

    # 对tcp连接进行监听
    t = threading.Thread(target=x.accept, name='accept')
    t.start()


if __name__ == '__main__':
    main()

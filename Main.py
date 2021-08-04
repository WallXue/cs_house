# -*- coding: utf-8 -*-
import html
import json
import re
import resource
import uuid
from datetime import datetime

import gevent as gevent
import requests
from bs4 import BeautifulSoup
from sqlalchemy import update, and_
from sqlalchemy.orm import sessionmaker

from DBHelper import engine
from Model import HousePreSale, HouseInfo, Building, Room

Session = sessionmaker(bind=engine)


def load_house_pre_sale():
    with open('data/house_swq.json', 'r') as read:
        house_json = json.load(read)
    soup = BeautifulSoup(house_json['content'], 'html.parser')
    house_bean_list = []
    for tr in soup.find_all('tr')[1:]:
        tds = tr.find_all('td')
        if tds[0].find('a'):
            house_id = tds[0].find('a').get('href').split('/')[-1]
        else:
            house_id = ''
        house_name = tds[0].text
        house_address = tds[1].text
        house_presale_no = tds[2].text
        house_presale_date = tds[3].text
        print(house_id + " " + house_name)
        house_bean = HousePreSale(house_id=house_id,
                                  house_name=house_name,
                                  house_address=house_address,
                                  house_presale_no=house_presale_no,
                                  house_presale_date=house_presale_date,
                                  status='有效',
                                  insert_time=datetime.now(),
                                  update_time=datetime.now()
                                  )
        house_bean_list.append(house_bean)
    session = Session()
    session.add_all(house_bean_list)
    session.commit()


def load_house():
    page = 1
    while True:
        house_id_list = get_task_list(page)
        if not house_id_list:
            print('同步完成！')
            break
        print('获取任务列表：' + str(house_id_list))
        task_list = []
        for house_id in house_id_list:
            task_list.append(gevent.spawn(do_import, house_id))
        page += 1
        gevent.joinall(task_list)
        # if page == 2:
        #     break



def do_import(house_id):
    print('开始同步：' + house_id)
    url = 'http://222.240.149.21:8081/floorinfo/' + house_id
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    code = soup.select('.code')
    if code:
        if code[0].text.strip() == '404':
            update_house_pre_sale = (update(HousePreSale).where(HousePreSale.house_id == house_id).values(status='无效'))
            with engine.begin() as conn:
                conn.execute(update_house_pre_sale)
            return
    do_import_house_info(soup, house_id)
    do_import_building(soup, house_id)


def do_import_house_info(soup, house_id):
    print(f'{house_id}同步house...')
    detail_tables = soup.select('table')
    if not detail_tables:
        return
    detail_table = detail_tables[0]
    house_name = detail_table.find('th').text
    house_region = table_helper(detail_table, 1, 1)
    house_developer_company = table_helper(detail_table, 2, 1)
    house_project_address = table_helper(detail_table, 3, 1)  # 项目地址
    house_sale_address = table_helper(detail_table, 4, 1)  # 售楼处地址
    house_plan_count = table_helper(detail_table, 5, 1)  # 规划户数
    house_sum_area = table_helper(detail_table, 6, 1)  # 总占地面积
    house_sum_building_area = table_helper(detail_table, 7, 1)  # 总建筑面积
    house_area_ratio = table_helper(detail_table, 8, 1)  # 容积率
    house_green_ratio = table_helper(detail_table, 9, 1)  # 绿化率
    house_house_fee = table_helper(detail_table, 10, 1)  # 物业费
    house_detail = table_helper(detail_table, 11, 1)  # 项目简介

    house_project_no = table_helper(detail_table, 1, 3)  # 立项批文号
    house_total_building = table_helper(detail_table, 2, 3)  # 总栋数
    house_sale_price = table_helper(detail_table, 3, 3)  # 销售起价
    house_sale_tel = table_helper(detail_table, 4, 3)  # 售楼部电话
    house_bus = table_helper(detail_table, 5, 3)  # 公交路线
    house_design_company = table_helper(detail_table, 6, 3)  # 设计单位
    house_sale_proxy = table_helper(detail_table, 7, 3)  # 销售代理
    house_management_company = table_helper(detail_table, 8, 3)  # 物业管理
    house_build_company = table_helper(detail_table, 9, 3)  # 施工单位
    house_finish_date = table_helper(detail_table, 10, 3)  # 竣工时间
    house_info = HouseInfo(
        house_id=house_id,
        house_name=house_name,
        house_region=house_region,
        house_developer_company=house_developer_company,
        house_project_address=house_project_address,
        house_sale_address=house_sale_address,
        house_plan_count=house_plan_count,
        house_sum_area=house_sum_area,
        house_sum_building_area=house_sum_building_area,
        house_area_ratio=house_area_ratio,
        house_green_ratio=house_green_ratio,
        house_house_fee=house_house_fee,
        house_detail=house_detail,
        house_project_no=house_project_no,
        house_total_building=house_total_building,
        house_sale_price=house_sale_price,
        house_sale_tel=house_sale_tel,
        house_bus=house_bus,
        house_design_company=house_design_company,
        house_sale_proxy=house_sale_proxy,
        house_management_company=house_management_company,
        house_build_company=house_build_company,
        house_finish_date=house_finish_date,
        status='有效',
        insert_time=datetime.now(),
        update_time=datetime.now()
    )
    update_house_info = (update(HouseInfo).where(HouseInfo.house_id == house_id).values(status='过期'))
    with engine.begin() as conn:
        conn.execute(update_house_info)
    session = Session()
    session.add(house_info)
    session.commit()


def do_import_building(soup, house_id):
    print(f"{house_id} 同步building...")
    update_building_info = (update(Building).where(Building.house_id == house_id).values(status='过期'))
    with engine.begin() as conn:
        conn.execute(update_building_info)

    detail_tables = soup.select('table')
    if not detail_tables:
        return
    detail_table = detail_tables[0]
    trs = detail_table.select('tr')
    if not trs:
        return
    batch_no = str(uuid.uuid1())
    building_list = []
    task_list = []
    for tr in trs[1:]:
        tds = tr.find_all('td')
        if len(tds) < 3:
            continue
        building_id = tds[8]['onclick'].split('\'')[1]
        building_presale_num = tds[0].text  # 预售许可证号
        building_num = tds[1].text  # 对应栋号
        building_certificate_date = tds[2].text  # 发证日期
        building_permit_area = tds[3].text  # 批准预售总面积(㎡)
        building_china_num = tds[4].text  # 国土证号
        building_project_permit_num = tds[5].text  # 工程规划许可证号
        building_land_plan_num = tds[6].text  # 工程规划许可证号
        building_develop_num = tds[7].text  # 工程施工许可证
        building = Building(building_id=building_id,
                            house_id=house_id,
                            building_presale_num=building_presale_num,
                            building_num=building_num,
                            building_certificate_date=building_certificate_date,
                            building_permit_area=building_permit_area,
                            building_china_num=building_china_num,
                            building_project_permit_num=building_project_permit_num,
                            building_land_plan_num=building_land_plan_num,
                            building_develop_num=building_develop_num,
                            batch_no=batch_no,
                            status='有效',
                            insert_time=datetime.now(),
                            update_time=datetime.now()
                            )
        building_list.append(building)
        task_list.append(gevent.spawn(do_import_room, house_id, building_id, batch_no))
    session = Session()
    session.add_all(building_list)
    session.commit()
    gevent.joinall(task_list)


def do_import_room(house_id, building_id, bath_no):
    print(f'{house_id} {building_id} 同步room...')
    update_room_info = (update(Room).where(and_(Room.house_id == house_id, Room.building_id == building_id)
                                           ).values(status='过期'))
    with engine.begin() as conn:
        conn.execute(update_room_info)
    resp = requests.post('http://222.240.149.21:8081/hslist', data={'ywzh': building_id})
    text = resp.content.decode('unicode-escape')
    text = html.unescape(text)
    text = re.sub(r"\\", "", text)
    soup = BeautifulSoup(text, 'html.parser')
    trs = soup.find_all('tr')
    if trs:
        room_list = []
        for tr in trs[1:]:
            tds = tr.find_all('td')
            room_id = tds[0].text  # 楼层
            room_floor = tds[1].text  # 楼层
            room_use_for = tds[2].text  # 房屋用途
            room_type = tds[3].text  # 房屋类型
            room_building_area = tds[4].text  # 建筑面积
            room_area = tds[5].text  # 套内面积
            room_common_area = tds[6].text  # 分摊面积
            room_sale_status = tds[7].text  # 期房销售状态
            room = Room(house_id=house_id,
                        building_id=building_id,
                        room_id=room_id,
                        room_floor=room_floor,
                        room_use_for=room_use_for,
                        room_type=room_type,
                        room_building_area=room_building_area,
                        room_area=room_area,
                        room_common_area=room_common_area,
                        room_sale_status=room_sale_status,
                        batch_no=bath_no,
                        status='有效',
                        insert_time=datetime.now(),
                        update_time=datetime.now())
            room_list.append(room)
        session = Session()
        session.add_all(room_list)
        session.commit()


def table_helper(table, tr_index, td_index):
    return table.find_all('tr')[tr_index].find_all('td')[td_index].text


def get_task_list(page):
    page = max(page, 1)
    size = 5
    begin = (page - 1) * size
    with engine.begin() as con:
        rs = con.execute(
            'select a.house_id from (select distinct house_id from house_pre_sale where status=\'有效\') a         left '
            'join (select '
            'house_id from house_info h where h.status = \'有效\') b on    a.house_id = b.house_id where b.house_id is '
            'null order by a.house_id desc limit ?,?',
            (begin, size))
        house_id_list = [house_id for house_id, in rs]
    return house_id_list


if __name__ == '__main__':
    # load_house_pre_sale()
    load_house()

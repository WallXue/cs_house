from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

from DBHelper import engine

Base = declarative_base()


class HousePreSale(Base):
    __tablename__ = 'house_pre_sale'

    id = Column(Integer, autoincrement=True, primary_key=True)
    house_id = Column(String)  # 小区ID
    house_presale_no = Column(String)  # 预售ID
    house_name = Column(String)
    house_address = Column(String)
    house_presale_date = Column(String)

    status = Column(String)  # 是否有效
    insert_time = Column(DateTime)
    update_time = Column(DateTime)


class HouseInfo(Base):
    __tablename__ = 'house_info'

    id = Column(Integer, autoincrement=True, primary_key=True)
    house_id = Column(String)
    house_name = Column(String)

    house_region = Column(String)  # 所属区域
    house_developer_company = Column(String)  # 开发商
    house_project_address = Column(String)  # 项目地址
    house_sale_address = Column(String)  # 售楼处地址
    house_plan_count = Column(String)  # 规划户数
    house_sum_area = Column(String)  # 总占地面积
    house_sum_building_area = Column(String)  # 总建筑面积
    house_area_ratio = Column(String)  # 容积率
    house_green_ratio = Column(String)  # 绿化率
    house_house_fee = Column(String)  # 物业费
    house_detail = Column(String)  # 项目简介

    house_project_no = Column(String)  # 立项批文号
    house_total_building = Column(String)  # 总栋数
    house_sale_price = Column(String)  # 销售起价
    house_sale_tel = Column(String)  # 售楼部电话
    house_bus = Column(String)  # 公交路线
    house_design_company = Column(String)  # 设计单位
    house_sale_proxy = Column(String)  # 销售代理
    house_management_company = Column(String)  # 物业管理
    house_build_company = Column(String)  # 施工单位
    house_finish_date = Column(String)  # 竣工时间

    status = Column(String)  # 是否有效
    insert_time = Column(DateTime)
    update_time = Column(DateTime)


class Building(Base):
    __tablename__ = 'building'

    id = Column(Integer, autoincrement=True, primary_key=True)
    building_id = Column(String)  # id
    house_id = Column(String)
    building_presale_num = Column(String)  # 预售许可证号
    building_num = Column(String)  # 对应栋号
    building_certificate_date = Column(String)  # 发证日期
    building_permit_area = Column(String)  # 批准预售总面积(㎡)
    building_china_num = Column(String)  # 国土证号
    building_project_permit_num = Column(String)  # 工程规划许可证号
    building_land_plan_num = Column(String)  # 工程规划许可证号
    building_develop_num = Column(String)  # 工程施工许可证

    batch_no = Column(String)  # 批次
    status = Column(String)  # 是否有效
    insert_time = Column(DateTime)
    update_time = Column(DateTime)


class Room(Base):
    __tablename__ = 'room'

    id = Column(Integer, autoincrement=True, primary_key=True)
    house_id = Column(String)
    building_id = Column(String)
    room_id = Column(String)  # 户室号

    room_floor = Column(String)  # 楼层
    room_use_for = Column(String)  # 房屋用途
    room_type = Column(String)  # 房屋类型
    room_building_area = Column(String)  # 建筑面积
    room_area = Column(String)  # 套内面积
    room_common_area = Column(String)  # 分摊面积
    room_sale_status = Column(String)  # 期房销售状态

    batch_no = Column(String)  # 批次
    status = Column(String)  # 是否有效
    insert_time = Column(DateTime)
    update_time = Column(DateTime)


if __name__ == '__main__':
    Base.metadata.create_all(engine)

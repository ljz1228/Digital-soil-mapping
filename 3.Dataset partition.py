import os
import pandas as pd
import numpy as np
from osgeo import gdal
from configargparse import ArgParser


def main(covariantdir,labeldir,labelname,koppen_level):
  ###根据目标变量路径读取数据
  data=pd.read_excel(labeldir)
  label=data[labelname]
  koppen_type=data['koppen_type'].str[:koppen_level]
  soil_depth=data['shn']
  print('不同气候区域的站点数量：')
  print(koppen_type.value_counts())
  koppen_type_counts=koppen_type.unique()
  print('不同土壤深度的站点数量：')
  print(soil_depth.value_counts())
  soil_depth_counts = soil_depth.unique()
  ###循环每一层土壤深度
  for i in range(1,10):
      soil_depth_index = soil_depth.loc[soil_depth == i]
      ######筛选第一层土壤深度的所有气候区域
      koppen_type_soil_depth=koppen_type[soil_depth_index.index]

      koppen_type_soil_depth.to_excel('../'+str(i) + "-th soil_depth_index.xlsx", index=True,index_label='index')
      print('第',i ,'层土壤深度的label处理结束........：')



if __name__ == '__main__':
    p = ArgParser()
    ###设置协变量路径
    p.add_argument('--covariantdir', type=str, default=r'../../Covariates80Npy', help='Path to covariates')
    ###设置标签路径
    p.add_argument('--labeldir', type=str, default=r'../label.xlsx', help='Path to label')
    ###设置标签名字
    p.add_argument('--labelname', type=str, default=[ 'OC', 'sand', 'silt', 'clay'], help='label name')
    ###设置气候区域级别 I级：1; II级：2; III级：3
    p.add_argument('--koppen_level', type=int, default=2, help='The level of koppen')

    args = p.parse_args()

    main(
        covariantdir=args.covariantdir,
        labeldir=args.labeldir,
        labelname=args.labelname,
        koppen_level=args.koppen_level
    )
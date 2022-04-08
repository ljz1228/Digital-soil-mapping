import os
# import cv2
import numpy as np
from osgeo import gdal
from configargparse import ArgParser

def read_tiff(path):
    ds = gdal.Open(path)
    im_width  = ds.RasterXSize
    im_height = ds.RasterYSize
    im_proj = ds.GetProjection()
    im_Geotrans = ds.GetGeoTransform()
    im_data = ds.ReadAsArray(0, 0, im_width, im_height)
    return im_data,im_Geotrans,im_width,im_height


###按照经纬度最相近的位置进行赋值
def resize(im_data,im_Geotrans,im_width,im_height,baselinedatadir,datadir,name):
# ————————————————————————————————————————————————————————————————————————————————————————————————————
    ###读取标准协变量的数据信息，为了使其它协变量按照该标准协变量调整分辨率
    ###im_data_new：协变量的数值； im_Geotrans_new：协变量的经纬度；im_width_new：协变量的经度；im_height_new：协变量的纬度
    im_data_new, im_Geotrans_new, im_width_new, im_height_new = read_tiff(baselinedatadir)
    ###按照标准经纬度大小，初始化标准数据
    data_index_lon = np.zeros((im_width_new),dtype=int)
    data_index_lat = np.zeros((im_height_new),dtype=int)
# ————————————————————————————————————————————————————————————————————————————————————————————————————
###按照标准经纬度大小，初始化标准数据
###经度---im_Geotrans[0]：协变量经度起点；im_Geotrans[1]：协变量经度分辨率
###纬度---im_Geotrans[3]：协变量纬度起点；im_Geotrans[5]：协变量纬度分辨率
    ###初始化预处理数据
    lon = [im_Geotrans[1]*i+im_Geotrans[0] for i in range(im_width)]
    lat = [im_Geotrans[5]*i+im_Geotrans[3] for i in range(im_height)]
    lon=np.array(lon)
    lat=np.array(lat)
    ###初始化标准数据
    lon_new = [im_Geotrans_new[1]*i+im_Geotrans_new[0] for i in range(im_width_new)]
    lat_new = [im_Geotrans_new[5]*i+im_Geotrans_new[3] for i in range(im_height_new)]
# ————————————————————————————————————————————————————————————————————————————————————————————————————
###根据最近的经度，寻找预处理数据与标准数据间
    temp = 0
    data_index_lon=[]
    for i in lon_new:
        range_max_index = np.where(lon >= i)
        range_max = lon[range_max_index]
        if range_max.any():
            range_max_value=range_max.min()
            range_max_value_index=range_max_index[0][0]
        else:
            range_max_value = 999999

        range_min_index = np.where(lon < i)
        range_min = lon[range_min_index]
        if range_min.any():
            range_min_value=range_min.max()
            range_min_value_index = range_min_index[0][-1]
        else:
            range_min_value = 999999
        if abs(range_max_value - i) < abs(range_min_value - i):
            data_index_lon.append(range_max_value_index)
        else:
            data_index_lon.append(range_min_value_index)
    temp = temp + 1
###根据最近的纬度，寻找预处理数据与标准数据间,由于纬度是从大到下排序，因此找最近的方式，与经度相反
    temp = 0
    data_index_lat=[]
    for i in lat_new:
        range_max_index = np.where(lat >= i)
        range_max = lat[range_max_index]
        if range_max.any():
            range_max_value=range_max.min()
            range_max_value_index=range_max_index[0][-1]
        else:
            range_max_value = 999999
        range_min_index = np.where(lat < i)
        range_min = lat[range_min_index]

        if range_min.any():
            range_min_value=range_min.max()
            range_min_value_index = range_min_index[0][0]
        else:
            range_min_value = 999999
        if abs(range_max_value - i) < abs(range_min_value - i):
            data_index_lat.append(range_max_value_index)
        else:
            data_index_lat.append(range_min_value_index)
    temp = temp + 1
# ————————————————————————————————————————————————————————————————————————————————————————————————————
    ###初始化调整后的协变量
    data_index_lon=np.array(data_index_lon)
    data_index_lat=np.array(data_index_lat)
    # data_new=im_data[data_index_lat,data_index_lon]
    data_new=np.zeros((im_height_new,im_width_new),dtype='float32')

    ###根据最近的经纬度，生产调整分辨率后的协变量
    for i in range(len(data_index_lat)):
        data_new[i]=im_data[data_index_lat[i]][data_index_lon]

    np.save(datadir+'/'+name,data_new)





def main(datadir,datadir_save,baselinedatadir):
  ###根据协变量路径读取数据
  fileList = os.listdir(datadir);
  ###遍历所有协变量
  for covariates_name in fileList:
      ###读取某一协变量
      ###im_data：协变量的数值； im_Geotrans：协变量的经纬度；im_width：协变量的经度；im_height：协变量的纬度
      path=datadir+'/'+covariates_name
      im_data, im_Geotrans, im_width, im_height = read_tiff(path)
      ###定义协变量的名字
      name = covariates_name.replace('.tif','')
      ###目前数据库协变量对于纬度分为7398，7401和其它情况
      ###如果协变量纬度总大小是7401，我们删除右下角信息（多余的海洋区域）
      ###如果协变量是其它情况，我们按照经纬度最相近的位置进行赋值
      if  im_width==7398:
          np.save(datadir+'/'+name,im_data)
      elif im_width==7401:
          np.save(datadir+'/'+name,im_data[:-4,:-3])
      else:
          resize(im_data, im_Geotrans, im_width, im_height, baselinedatadir, datadir_save,name)
      print('Tne end for adjusting resolution of all covariates')


if __name__ == '__main__':
    p = ArgParser()
    ###设置协变量路径
    p.add_argument('--datadir', type=str, default=r'../Covariates80', help='Path to data')
    p.add_argument('--datadir_save', type=str, default=r'../Covariates80Npy', help='Save path to data')
    ###挑选一个具有标准分辨率的协变量，并定义其路径
    p.add_argument('--baselinedatadir', type=str, default=r'../Covariates/TX6MOD.tif', help='Path to baseline data')
    args = p.parse_args()

    main(
        datadir=args.datadir,
        datadir_save=args.datadir_save,
        baselinedatadir=args.baselinedatadir
    )
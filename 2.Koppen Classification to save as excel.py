from bisect import bisect_left
import pandas as pd
import numpy as np
import pyreadr
#二分查找
def takeClosest(myList, myNumber):
    """
     Assumes myList is sorted. Returns closest value to myNumber.
     If two numbers are equally close, return the smallest number.
     If number is outside of min or max return False
    """
    if (myNumber > myList[-1] or myNumber < myList[0]):
        return False
    pos = bisect_left(myList, myNumber)
    return pos
# ————————————————————————————————————————————————————————————————————————————————————————————————————
#####d.RData文件，首先删除空值，使数据集可处理
dataFrame= pyreadr.read_r(r'../../d.RData')
data=dataFrame['d']
col=['OC','sand','silt','clay',
     'no','bot',   'up',      'd',       'TX5MOD',    'TX3MOD',  'TX4MOD',   'lon',  'DEM','LFTUSG15',
    'TDHMOD' , 'TNHMOD',    'PDMGPW',  'EVMMOD',    'GACGEM',  'MODCF',    'lat',
    'TDMMOD' , 'BICUSG14',  'PREGSM',  'P06DWD',    'PX3WCL',  'TNMMOD',   'INSSRE',
    'INMSRE' , 'EVSMOD',    'PX4WCL',  'L3POBI',    'BDTICM',  'P09DWD',   'SEDDEP',
    'TX6MOD' , 'RTMUSG15',  'P04DWD',  'TNLMOD',    'P03DWD',  'TX2MOD',   'PX2WCL',
    'P10DWD' , 'TNSMOD',    'P05DWD',  'TDSMOD',    'TX1MOD',  'P02DWD',   'P11DWD',
    'P07DWD' , 'ENTROPY',   'PX1WCL',  'P12DWD',    'P01DWD',  'P08DWD',   'MAX0105',
    'TDLMOD' , 'L10IGB',    'L14IGB',  'G12IGB',    'L06IGB',  'L05IGB',   'G04ESA',
    'COVER' ,  'G04IGB',    'STGHWS',  'G14ESA',    'G08ESA',  'GGLHWS',
    'GLCJRC' , 'G01IGB',    'L01IGB',  'G01ESA',    'G11ESA',  'EVENNESS', 'G02IGB',
    'GLCESA' , 'GALHWS',    'G09ESA',  'RANGE0105', 'G11IGB',  'GCRHWS',
    'GUMHWS' , 'G05ESA',    'G20ESA','shn']
#########定义预处理的土壤碳，沙粒、粉和黏的含量比等信息，及站点相关信息，同时附有部分excel文件用的协变量。
## 站点相关信息    'no'：站点ID；'lat'：站点纬度； 'lon'：站点经度；'shn'：土壤层数；
##  label 信息    'OC'：土壤碳  'sand','silt','clay'：沙粒、粉和黏的含量比
##   附加协变量信息  'bot'：  ；'up'：   'd'：
label_col=['no','lat','lon','shn','bot','up','d','OC','sand','silt','clay']
xy=data[col]
xy=xy.dropna(axis=0,how='any')
label=xy[label_col]

# ————————————————————————————————————————————————————————————————————————————————————————————————————
#####提前删除空值后，每个站点的ID号和经纬度信息
Lon_Lat=xy.loc[:,['no','lon','lat']]
Lon_Lat=np.array(Lon_Lat)
# ————————————————————————————————————————————————————————————————————————————————————————————————————
#####读取柯本气候区域类型表，按照经纬度，将站点进行气候区域标注
koppenData=pd.read_excel('../../koppen.xlsx')
# ————————————————————————————————————————————————————————————————————————————————————————————————————
#####为了减小计算量，通过中国所在范围经纬度，手动查找在表格所处的位置，锁定该区间
koppenData=koppenData.iloc[40678:70101]#纬度中国区域
#####读取中国区域柯本数据的纬度信息
koppen_lat=np.array(koppenData.iloc[:,0])
#####读取中国区域柯本数据的经度信息
koppen_lon=np.array(koppenData.iloc[:,1])
#####读取中国区域柯本数据的类型
koppen_type=np.array(koppenData.iloc[:,2])
stations_koppen_type=[]
# ————————————————————————————————————————————————————————————————————————————————————————————————————
#####循环站点数据，并根据其经纬度信息匹配最近距离的柯本气候区域类型
for i in range(len(Lon_Lat)):
    #提取每个站点的经纬度
    lon = Lon_Lat[i, 1]
    lat = Lon_Lat[i, 2]
    print('该站点的纬度是：', lat, '; 经度是：', lon)
    # 利用二分查找封装函数，快速锁定站点维度在柯本数据中；
    # posLat和posLat-1表示柯本气候区域中，离站点维度最近的两个样本索引ID
    posLat = takeClosest(koppen_lat, lat)
    # 判断离站点维度最近的两个样本，哪一个绝对距离最小
    if abs(koppen_lat[posLat] - lat) > abs(koppen_lat[posLat - 1] - lat):
        tempPosLat = posLat - 1
        # 查找柯本气候区域中维度最近的所有样本
        lat_index=np.where(koppen_lat==koppen_lat[tempPosLat])
        # ————————————————————————————————————————————————————————————————————————————————————————————————————
        # 根据维度最近的所有样本，查找精度最近的两个相邻样本
        posLon = takeClosest(koppen_lon[lat_index], lon)
        temp_lon = koppen_lon[lat_index]
        # 计算最近三个相邻样本的距离绝对值
        ##首先为了防止边界溢出的情况，如果posLon是temp_lon列表的最大索引
        if posLon == temp_lon.size-1:
            temp_lon_values = [abs(temp_lon[posLon - 1] - lon), abs(temp_lon[posLon] - lon)]
            temp_lon_index = [posLon - 1, posLon]
            min_lon_index = temp_lon_index[temp_lon_values.index(min(temp_lon_values))]
            tempPosLon = lat_index[0][min_lon_index]
        ##如果posLon是temp_lon列表的最小索引
        elif posLon == 0:
            temp_lon_values = [abs(temp_lon[posLon] - lon), abs(temp_lon[posLon + 1] - lon)]
            temp_lon_index = [posLon, posLon + 1]
            min_lon_index = temp_lon_index[temp_lon_values.index(min(temp_lon_values))]
            tempPosLon = lat_index[0][min_lon_index]
        else:
            temp_lon_values = [abs(temp_lon[posLon - 1] - lon), abs(temp_lon[posLon] - lon),
                               abs(temp_lon[posLon + 1] - lon)]
            temp_lon_index = [posLon - 1, posLon, posLon + 1]
            min_lon_index = temp_lon_index[temp_lon_values.index(min(temp_lon_values))]
            tempPosLon = lat_index[0][min_lon_index]
    else:
        tempPosLat = posLat
        # 查找柯本气候区域中维度最近的所有样本
        lat_index = np.where(koppen_lat == koppen_lat[tempPosLat])
        # ————————————————————————————————————————————————————————————————————————————————————————————————————
        # 根据维度最近的所有样本，查找精度最近的两个相邻样本
        posLon = takeClosest(koppen_lon[lat_index], lon)
        temp_lon=koppen_lon[lat_index]
        # 计算最近三个相邻样本的距离绝对值
        ##首先为了防止边界溢出的情况，如果posLon是temp_lon列表的最大索引
        if posLon==temp_lon.size-1:
            temp_lon_values=[abs(temp_lon[posLon-1]- lon),abs(temp_lon[posLon]- lon)]
            temp_lon_index = [posLon - 1, posLon]
            min_lon_index = temp_lon_index[temp_lon_values.index(min(temp_lon_values))]
            tempPosLon = lat_index[0][min_lon_index]
        ##如果posLon是temp_lon列表的最小索引
        elif posLon==0:
            temp_lon_values = [abs(temp_lon[posLon] - lon), abs(temp_lon[posLon+1] - lon)]
            temp_lon_index = [posLon, posLon+1]
            min_lon_index = temp_lon_index[temp_lon_values.index(min(temp_lon_values))]
            tempPosLon = lat_index[0][min_lon_index]
        else:
            temp_lon_values=[abs(temp_lon[posLon-1]- lon),abs(temp_lon[posLon]- lon),abs(temp_lon[posLon+1]- lon)]
            temp_lon_index=[posLon-1,posLon,posLon+1]
            min_lon_index=temp_lon_index[temp_lon_values.index(min(temp_lon_values))]
            tempPosLon=lat_index[0][min_lon_index]
    stations_koppen_type.append(koppen_type[tempPosLon])
    print('第',i,'个站点','对应柯本数据的纬度是：',koppen_lat[tempPosLat],'; 经度是：',koppen_lon[tempPosLon])
    print('该站点的气候类型是：', koppen_type[tempPosLon])
label["koppen_type"]=stations_koppen_type
label.to_excel("label.xlsx",index=False)
# np.save('label',label)
print('end')

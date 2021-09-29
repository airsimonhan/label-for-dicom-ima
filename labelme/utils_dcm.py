# encoding=utf-8
from pydicom import dcmread
import pydicom
import numpy as np
from PIL import Image
import os
import re
import shutil
import cv2
import SimpleITK as sitk


class DicomProcess(object):
    @staticmethod
    def dcm2png(dcm, single=True):
        dc = dcmread(dcm, force=True)  # 读取dcm文件
        dc.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        # ---------------------第一步：加载图像基本信息-----------------------
        key_list = DicomProcess.extra_info(dc)

        # 读取系列名字
        if ('0x0008', '0x103e') in key_list:
            series_description = dc[0x0008, 0x103e].value
        else:
            series_description = 'series_tmp'

        # 读取模态名称
        if ('0x0008', '0x0060') in key_list:
            modality = dc[0x0008, 0x0060].value
        else:
            modality = 'series_tmp'

        # 读取截距和斜率
        if ('0x0028', '0x1052') in key_list:
            intercept = dc[0x0028, 0x1052].value
            slope = dc[(0x0028, 0x1053)].value
        else:
            intercept = 0
            slope = 1

        # 读取pixel array
        try:
            pixel_array = dc.pixel_array
            shape = pixel_array.shape
            dcm_array = (pixel_array * slope + intercept)
        except:
            print('pydicom cannot import pixel_array')
            dc_tmp = sitk.ReadImage(dcm)
            dcm_array = sitk.GetArrayFromImage(dc_tmp)
            dcm_array = np.squeeze(dcm_array)
            shape = dcm_array.shape

        # 读取 病人ID 和 instance number
        if ('0x0010', '0x0020') in key_list:
            patient_id = str(dc[0x0010, 0x0020].value)
        else:
            patient_id = 0
        if ('0x0020', '0x0013') in key_list:
            instance = str(dc[0x0020, 0x0013].value)
        else:
            instance = 0

        # 读取 DWI 数据中的 B 值
        if ('0x0019', '0x100c') in key_list:
            b_value = str(dc[0x0019, 0x100c].value)
        else:
            b_value = ''
        # -----------------------------------------------------

        path = './tmp/'
        if single:
            DicomProcess.check_dir(path)  # 检测路径存在与否,清空文件夹
        file_path = ''
        if len(shape) == 4:  # 序列
            # todo 如果是序列的话，就直接顺序排列，不需要instance number了
            for i in range(shape[0]):
                file_path = DicomProcess.save_img(
                    shape=shape,
                    modality=modality,
                    dcm_array=dcm_array[i],
                    path=path,
                    patient_id=patient_id,
                    series_description=series_description,
                    b_value=b_value,
                    instance=i,  # 如果是序列，那么就直接让instance=i就可以了
                    )
        elif len(shape) == 3 or 2:  # 单张图片
            file_path = DicomProcess.save_img(
                shape=shape,
                modality=modality,
                dcm_array=dcm_array,
                path=path,
                patient_id=patient_id,
                series_description=series_description,
                b_value=b_value,
                instance=instance,
            )
        return path, file_path, dc

    @staticmethod
    def dcm2npy(dcm, path):
        dc = dcmread(dcm)  # 读取dcm文件
        np.save(path, dc.pixel_array)

    @staticmethod
    def check_dir(dir):
        re = True
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
            else:
                shutil.rmtree(dir)  # 清空文件夹
                os.makedirs(dir)
        except BaseException:
            re = False
        return re

    @staticmethod
    def extra_info(dc):
        raw_data = str(dc).replace(" ", "")
        raw_key_list = re.findall("\((.*?)\)", raw_data)

        key_list = []
        for i in raw_key_list:
            if len(i) >= 9 and ',' in i:
                i1 = i.split(',')[0]
                i2 = i.split(',')[1]
                i1 = '0x' + i1
                i2 = '0x' + i2
                i1.replace(" ", "")
                i2.replace(" ", "")
                key_list.append(tuple([i1, i2]))

        return key_list

    @staticmethod
    def normalization(shape, imageData):
        ymax = 255
        ymin = 0
        xmax = np.max(imageData)
        xmin = np.min(imageData)

        # todo: 文件颜色格式
        if len(shape) == 3:  # 彩色图像
            # ima only    字段：dc.PhotometricInterpretation={str}'RGB'
            imageData = cv2.cvtColor(imageData, cv2.COLOR_RGB2BGR)
        else:
            imageData = ((imageData - xmin) / (xmax - xmin)
                         * (ymax - ymin)) + ymin

        imageData = imageData.astype(np.uint8)
        return imageData

    @ staticmethod
    def save_img(shape, modality, dcm_array, path, patient_id, series_description, b_value, instance):
        imageData = DicomProcess.normalization(shape, dcm_array)
        file_path = path + str(patient_id) + '_' + modality + '_' + series_description + '_' + b_value + '_' + str(instance).zfill(4) + '.png'
        file_path = file_path.replace(' ', '_')
        file_path = file_path.replace(':', '_')
        file_path = file_path.replace('-', '_')
        file_path = file_path.replace('*', 'anonymous')
        cv2.imwrite(file_path, imageData)
        return file_path

# A label tool for dicom and ima files

这个代码是在[labelme](https://github.com/wkentaro/labelme)的基础上进行修改，用来标注医学图像数据

## 功能描述
1. 可以实现Dicom和Ima文件的 `批量` 读入和标注
2. 保存的文件为npy和json，前者包含原始Dicom文件中的pixel_array，后者包含标注信息
 - 根据dicom中的参数对保存的文件进行命名，可以唯一标识标注文件
 - 配合自动保存规则，标注省时省力
5. 可以读取并显示当前dicom文件中的全部信息

[] TODO 上一张和下一张的快捷键分别是 `A` 和 `D` ，但是软件界面显示是 `N` 和 `P` ，需要修改一下

## 界面展示
由于数据未脱敏，软件相关信息打码了
1. 右侧第一栏为当前文件夹内的所有dcm文件（已经重新根据patientID, series number, instance number, modality等信息进行重命名）
2. 右侧第二栏为当前dcm文件中的数据信息，便于对当前数据进行信息的阅读
3. 右侧下方为标注的信息
![demo](./imgs/demo.png)

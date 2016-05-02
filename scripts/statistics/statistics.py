#coding:utf-8

import os
import sys
import csv
import xlrd
import xlsxwriter
import glob


sys.path.append( os.path.join( os.path.abspath(os.path.dirname(__file__)) , '../..'))
from glearn.crf.datasets import datasets
from glearn.crf import orm
from glearn.crf import global_variables as gv

def fetch_labels_num():
        category_sampleNum_dict = dict()
        all_model_ids = orm.CrfModel.fetch_all_model_ids()

        unlabeled_categories=list()
        for crf_model_id in all_model_ids:
                category = datasets.fetch_category( crf_model_id )
                crf_labeled_samples = datasets.load_labeld_samples(crf_model_id)
                if crf_labeled_samples==None:
                        category_sampleNum_dict[category] = 0
                        unlabeled_categories.append(category)
                        continue
                else:
                        category_sampleNum_dict[category] = len(crf_labeled_samples)
        # print sorted(unlabeled_categories)
        return category_sampleNum_dict

def main():
        # 有模型的类别（有数据的类别）
        trained_catigories = list()
        modelfiles = glob.glob(os.path.expanduser( os.path.join('~','crf_learn_model','gldjc','*.model')))
        for f in modelfiles:
                trained_catigories.append(os.path.basename(f).lstrip('gldjc@').rstrip('.model'))
        print '\n'.join(sorted(trained_catigories))
        

        category_sampleNum_dict = fetch_labels_num()
        

        # 写excel
        workbook = xlsxwriter.Workbook( './base_material_types_.xlsx' )
        red_font_format = workbook.add_format() ;red_font_format.set_font_color('red')
        worksheet = workbook.add_worksheet()
        # Start from the first cell below the headers.
        row = 1
        col = 0
        

        # read CSV
        reader = csv.reader(file('./base_material_types.csv', 'rb'), delimiter=',')
        reader_list = list(reader)
        header = reader_list[0]
        for line in reader_list[1:]:
                row_values = line
                print row_values
                
                lv1_code,lv2_code = row_values[0],row_values[1]
                if lv1_code+'.'+lv2_code in trained_catigories:
                        for idx,value in enumerate(row_values):
                                print row, idx, row_values[idx]
                                worksheet.write(row, idx, row_values[idx])
                        worksheet.write(row, idx+1, category_sampleNum_dict.get(lv1_code+'.'+lv2_code,0))
                        row = row +1
                else:
                        for idx,value in enumerate(row_values):
                                worksheet.write(row, idx, row_values[idx] , red_font_format)
                        worksheet.write(row, idx+1, category_sampleNum_dict.get(lv1_code+'.'+lv2_code,0))
                        row = row +1

        # 读excel
        # data_workbook = xlrd.open_workbook( './base_material_types.xlsx' )
        # table = data_workbook.sheet_by_index(0) #通过索引顺序获取
        # nrows = table.nrows
        # ncols = table.ncols

        # header = table.row_values(0)
        # for i in range(nrows)[1:]:
        #         row_values = table.row_values(i)
        #         print row_values

        #         # import pdb;pdb.set_trace()
        #         lv1_code,lv2_code = row_values[0],row_values[1]
        #         if lv1_code+'.'+lv2_code in trained_catigories:
        #                 for idx,value in enumerate(row_values):
        #                         print row, idx, row_values[idx]
        #                         worksheet.write(row, idx, row_values[idx])
        #                 worksheet.write(row, idx+1, category_sampleNum_dict.get(lv1_code+'.'+lv2_code,0))
        #                 row = row +1
        #         else:
        #                 for idx,value in enumerate(row_values):
        #                         worksheet.write(row, idx, row_values[idx] , red_font_format)
        #                 worksheet.write(row, idx+1, category_sampleNum_dict.get(lv1_code+'.'+lv2_code,0))
        #                 row = row +1


        workbook.close()

if __name__ == '__main__':
        main()
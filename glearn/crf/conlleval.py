#!/usr/bin/env python
# -*- coding: utf-8 -*- "

import commands
import global_variables as gv

def conlleval(output_file):
	"""利用perl脚本对decode的数据做一次整体上的评估
	"""
	conlleval_pl_file = gv.conlleval_path + '/' + 'conlleval.pl'
	commandLine = "perl "+conlleval_pl_file+" -d '\t' < " + output_file
	print commandLine
	(status, output)=commands.getstatusoutput(commandLine)
	
	return (status,output)


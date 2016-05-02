#!/usr/bin/env python
# #_*_ coding: utf-8 _*_

import sys
import re

try:
	_, infile_path, outfile_path = sys.argv[0],sys.argv[1],sys.argv[2]
except Exception, e:
	print "Useage: python amendment_label infile_path outfile_path"
	sys.exit()


def main():
	prog = re.compile(r'<XS>(\d+)\+(\d+)</XS>')
	sentense = '橡套电缆 <XXX>YC</XXX>  <BCJMM>25</BCJMM>*<XS>3+1</XS>'
	print sentense
	print prog.subn(r'<XS>\1</XS>+<XS>\2</XS>',sentense)[0]
	

	def func1(m):
		return '<XS>'+m.group(1)+'</XS>*<BCJMM>'+m.group(2)+'</BCJMM>+<XS>'+m.group(3)+'</XS>*<BCJMM>'+m.group(4).rstrip('@')+'</BCJMM>'
	prog1 = re.compile(r'<XS>(\d+)</XS>\*<BCJMM>([\d\.]+)</BCJMM>\+<XS>(\d+)</XS>\*([\d\.@]+)')
	sentense1 = '<XXCZ>铜芯</XXCZ>交联聚氯乙烯绝缘聚氯乙烯钢带铠装护套电力电缆	<XXX>VLJV2-22</XXX>	   <XS>3</XS>*<BCJMM>300</BCJMM>+<XS>1</XS>*150@'
	print sentense1
	print prog1.subn(func1,sentense1)[0]

	lines_subn = list()
	with open(infile_path,'r') as infile:
		for line in infile.readlines():
			line = line.strip()
			# import pdb;pdb.set_trace()
			line_subn = prog.subn(r'<XS>\1</XS>+<XS>\2</XS>', line)[0]
			line_subn = prog1.subn(func1, line_subn)[0]
			lines_subn.append( line_subn )
			print line_subn

	with open(outfile_path,'w') as outfile:
		outfile.write('\n'.join(lines_subn))

if __name__ == '__main__':
	main()
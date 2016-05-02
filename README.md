* interfaces:

tornado_glearn的crf模块有四个接口：
	1.训练模型 TrainCrfModelHandler
	2.训练所有的模型TrainAllCrfModelHandler
	3.解码操作 DecodeHandler
	4.交叉验证 CrossValidateHandler

dependence:
	需要提前安装CRF++-0.58工具包（主目录中INSTALL文件）和perl工具
	weishiwei@ubuntu:~$ perl -v
	This is perl 5, version 18, subversion 2 (v5.18.2) built for i686-linux-gnu-thread-multi-64int
	(with 41 registered patches, see perl -V for more detail)perl





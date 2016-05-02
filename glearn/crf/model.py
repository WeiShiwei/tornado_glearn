# -*- coding: utf-8 -*-

import orm

class crf_model(object):
	"""docstring for crf_model"""
	def __init__(self, crf_model_id):
		super(crf_model, self).__init__()
		self.crf_model_id = crf_model_id
		self.orm_model = orm.session.query( orm.CrfModel ).filter( orm.CrfModel.id == crf_model_id ).first()

	def set_status(self,status):
		self.orm_model.status = status
		orm.session.add(self.orm_model)
		orm.session.commit()
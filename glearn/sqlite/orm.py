# -*- coding: utf-8 -*-
""" regex_match & stemmed moudule access to local sqlite databases
"""

import collections

from sqlalchemy import Column, Integer, Unicode, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, mapper
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from base import Base
from session import get_session


class Users(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	name = Column(Unicode(128), nullable=True)
	email_addr = Column(Unicode(128), nullable=True)

	@classmethod
	def authorized(cls, identity):
		with get_session() as session:
			user = session.query( cls ).filter(cls.name == identity).first()
			if not user:
				return False
			else:
				return True


class CrfStemmed(Base):
	"""docstring for CrfStemmed"""
	__tablename__ = 'crf_stemmed'

	id = Column(Integer, primary_key=True)
	word = Column(Unicode(128), nullable=True)
	stem = Column(Unicode(128), nullable=True)
	updated_at = Column( DateTime ) 
	created_at = Column( DateTime ) 

	@classmethod
	def get_word_stem_dict(cls):
		word_stem_dict = collections.defaultdict(str)
		with get_session() as session:
			all_crf_word_stems = session.query( cls.word, cls.stem).all()
			for kwr in all_crf_word_stems:
				stem = kwr.stem
				if stem == '':
					continue
				word = kwr.word # u'\u95e8\u7981\u673a'
				word_stem_dict[word] = stem
		return word_stem_dict

	@classmethod
	def fetch_latest_updated_time(cls):
		""" created_at =< updated_at"""
		with get_session() as session:
			latest_update_time = session.query(func.max(cls.updated_at)).first()
			return latest_update_time[0]

class CrfPattern(Base):
	"""docstring for CrfPattern"""
	__tablename__ = 'crf_pattern'

	id = Column(Integer, primary_key=True)
	first_type_code = Column(Unicode(128), nullable=True)
	second_type_code = Column(Unicode(128), nullable=True)
	pattern = Column(Unicode(128), nullable=True)
	regrex = Column(Unicode(128), nullable=True)
	substitute = Column(Unicode(128), nullable=True)
	# updated_at = Column( DateTime ) # would be an error
	# created_at = Column( DateTime ) 

	@classmethod
	def fetch_patterns(cls):
		pattern_list = list()
		with get_session() as session:
			for p in session.query(cls.first_type_code,cls.second_type_code,cls.pattern,cls.regrex,cls.substitute).all():
				category = p.first_type_code + '.' +p.second_type_code
				pattern = p.pattern
				regrex = p.regrex
				substitute = p.substitute
				pattern_list.append([category, pattern, regrex, substitute])
		return pattern_list




def main():
	print Users.authorized('gldjc')

	print CrfStemmed.get_word_stem_dict()
	print CrfStemmed.fetch_latest_updated_time()

	print CrfPattern.fetch_patterns()

if __name__ == '__main__':
	main()